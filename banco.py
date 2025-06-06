# Vamos utilizar o pacote SQLAlchemy para acesso a banco de dados:
# https://docs.sqlalchemy.org
#
# Para isso, ele precisa ser instalado via pip (de preferência com o VS Code fechado):
# python -m pip install SQLAlchemy
#
# Além disso, o SQLAlchemy precisa de um driver do conexão ao banco. Isso depende do servidor
# (MySQL, Postgres, SQL Server, Oracle...) e do driver real. Vamos utilizar o driver MySQL-Connector,
# que também precisa ser instalado (de preferência com o VS Code fechado):
# python -m pip install mysql-connector-python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config import conexao_banco
import mysql.connector

# Como criar uma comunicação com o banco de dados:
# https://docs.sqlalchemy.org/en/14/core/engines.html
#
# Detalhes específicos ao MySQL
# https://docs.sqlalchemy.org/en/14/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mysqlconnector
#
# mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
engine = create_engine(conexao_banco)

# A função text(), utilizada ao longo desse código, serve para encapsular um comando
# SQL qualquer, de modo que o SQLAlchemy possa entender!

def listarPessoas():
	# O with do Python é similar ao using do C#, ou o try with resources do Java.
	# Ele serve para limitar o escopo/vida do objeto automaticamente, garantindo
	# que recursos, como uma conexão com o banco, não sejam desperdiçados!
	with Session(engine) as sessao:
		pessoas = sessao.execute(text("SELECT id, nome, email FROM pessoa ORDER BY nome"))

		# Como cada registro retornado é uma tupla ordenada, é possível
		# utilizar a forma de enumeração de tuplas:
		for (id, nome, email) in pessoas:
			print(f'\nid: {id} / nome: {nome} / email: {email}')

		# Ou, se preferir, é possível retornar cada tupla, o que fica mais parecido
		# com outras linguagens de programação:
		#for pessoa in pessoas:
		#	print(f'\nid: {pessoa.id} / nome: {pessoa.nome} / email: {pessoa.email}')

def obterPessoa(id):
	with Session(engine) as sessao:
		parametros = {
			'id': id
		}

		# Mais informações sobre o método execute e sobre o resultado que ele retorna:
		# https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.execute
		# https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Result
		pessoa = sessao.execute(text("SELECT id, nome, email FROM pessoa WHERE id = :id"), parametros).first()

		if pessoa == None:
			print('Pessoa não encontrada!')
		else:
			print(f'\nid: {pessoa.id} / nome: {pessoa.nome} / email: {pessoa.email}')

def criarPessoa(nome, email):
	# É importante utilizar o método begin() para que a sessão seja comitada
	# automaticamente ao final, caso não ocorra uma exceção!
	# Isso não foi necessário nos outros exemplos porque nenhum dado estava sendo
	# alterado lá! Caso alguma exceção ocorra, rollback() será executado automaticamente,
	# e nenhuma alteração será persistida. Para mais informações de como explicitar
	# esse processo de commit() e rollback():
	# https://docs.sqlalchemy.org/en/14/orm/session_basics.html#framing-out-a-begin-commit-rollback-block
	with Session(engine) as sessao, sessao.begin():
		pessoa = {
			'nome': nome,
			'email': email
		}

		sessao.execute(text("INSERT INTO pessoa (nome, email) VALUES (:nome, :email)"), pessoa)

		# Para inserir, ou atualizar, vários registros ao mesmo tempo, a forma mais rápida
		# é passar uma lista como segundo parâmetro:
		# lista = [ ... ]
		# sessao.execute(text("INSERT INTO pessoa (nome, email) VALUES (:nome, :email)"), lista)

def obterDadosTempoReal():
	with Session(engine) as sessao:
		registros = sessao.execute(text("""
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 1 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 2 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 3 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 4 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 5 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 6 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 7 order by id desc limit 1)
union all
(select id_sensor, ocupado, time_to_sec(timediff(now(), data)) delta_agora from presenca where id_sensor = 8 order by id desc limit 1)
;
		"""))

		lista = []

		for (id_sensor, ocupado, delta_agora) in registros:
			lista.append({
				"id_sensor": id_sensor,
				"ocupado": ocupado,
				"delta_agora": delta_agora
			})

		return lista

def listarConsolidado(data_inicial, data_final):
	with Session(engine) as sessao:
		parametros = {
			'data_inicial': data_inicial + ' 00:00:00',
			'data_final': data_final + ' 23:59:59'
		}

		# Mais informações sobre o método execute e sobre o resultado que ele retorna:
		# https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.execute
		# https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Result
		registros = sessao.execute(text("""
		select date_format(tmp1.dia, '%d/%m/%Y') dia, cast(tmp1.total_entrada as signed) total_entrada1, cast(tmp1.total_saida as signed) total_saida1, cast(tmp2.total_entrada as signed) total_entrada2, cast(tmp2.total_saida as signed) total_saida2, cast(tmp3.total_entrada as signed) total_entrada3, cast(tmp3.total_saida as signed) total_saida3
		from (
			select date(data) dia, sum(entrada) total_entrada, sum(saida) total_saida
			from passagem
			where data between :data_inicial and :data_final
			and time(data) between '07:30:00' and '09:10:00'
			and id_sensor = 2 group by dia
		) tmp1
		inner join (
			select date(data) dia, sum(entrada) total_entrada, sum(saida) total_saida
			from passagem
			where data between :data_inicial and :data_final
			and time(data) between '09:30:00' and '11:10:00'
			and id_sensor = 2 group by dia
		) tmp2 on tmp2.dia = tmp1.dia
		inner join (
			select date(data) dia, sum(entrada) total_entrada, sum(saida) total_saida
			from passagem
			where data between :data_inicial and :data_final
			and time(data) between '11:20:00' and '13:00:00'
			and id_sensor = 2 group by dia
		) tmp3 on tmp3.dia = tmp1.dia
		"""), parametros)

		lista = []

		for (dia, total_entrada1, total_saida1, total_entrada2, total_saida2, total_entrada3, total_saida3) in registros:
			lista.append({
				"dia": dia,
				"total_entrada1": total_entrada1,
				"total_saida1": total_saida1,
				"total_entrada2": total_entrada2,
				"total_saida2": total_saida2,
				"total_entrada3": total_entrada3,
				"total_saida3": total_saida3,
			})

		return lista

# Para mais informações:
# https://docs.sqlalchemy.org/en/14/tutorial/dbapi_transactions.html
