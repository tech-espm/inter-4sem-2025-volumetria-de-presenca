from flask import Flask, jsonify, render_template, json, request, Response
import config
import requests
from datetime import datetime, timedelta
import banco
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

app = Flask(__name__)

@app.get('/')
def index():
    semana_passada = (datetime.today() + timedelta(days=-6)).strftime('%Y-%m-%d')
    hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/index.html', semana_passada=semana_passada, hoje=hoje)

@app.get('/sobre')
def sobre():
    return render_template('index/sobre.html', titulo='Sobre Nós')

@app.get("/dashboard")
def dashboard():
    return render_template('index/dashboard.html', titulo='Dashboard')

@app.get('/dados/temperatura')
def dados_temp():
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')

    if not data_inicial or not data_final:
        return jsonify([])

    with Session(banco.engine) as sessao, sessao.begin():
        result = sessao.execute(text("""
            SELECT 
                DATE_FORMAT(data, '%H:00:00') AS hora,
                AVG(temperatura) AS temperatura,
                AVG(umidade) AS umidade
            FROM temperatura
            WHERE data BETWEEN :inicio AND :fim
            GROUP BY hora
            ORDER BY hora
        """), {"inicio": data_inicial, "fim": data_final + " 23:59:59"})

        dados = result.fetchall()
        dados = [
            {
                "data": row[0],
                "temperatura": round(row[1], 2),
                "umidade": round(row[2], 2)
            } for row in dados
        ]
    
    return jsonify(dados)



@app.route("/obterDadosTempoReal")
def obterDadosTempoReal():
    with Session(banco.engine) as sessao, sessao.begin():
        # PRESENCA
        result = sessao.execute(text("SELECT max(id) FROM presenca"))
        max_id_pres = result.fetchone()[0] or 0

        response_pres = requests.get(f"{config.url_api}?sensor=presence&id_inferior={max_id_pres}")
        dados_pres = response_pres.json()

        for dado in dados_pres:
            sessao.execute(text("""
                INSERT INTO presenca (id, data, id_sensor, delta, bateria, ocupado)
                VALUES (:id, :data, :id_sensor, :delta, :bateria, :ocupado)
            """), dado)

    return jsonify(banco.obterDadosTempoReal())

@app.route("/obterDados")
def obterDados():
    data_inicial = request.args['data_inicial']
    data_final = request.args['data_final']

    with Session(banco.engine) as sessao, sessao.begin():
        # TEMPERATURA
        result = sessao.execute(text("SELECT max(id) FROM temperatura"))
        max_id_temp = result.fetchone()[0] or 0

        response_temp = requests.get(f"{config.url_api}?sensor=temperature&id_inferior={max_id_temp}")
        dados_temp = response_temp.json()

        for dado in dados_temp:
            sessao.execute(text("""
                INSERT INTO temperatura (id, data, id_sensor, delta, umidade, temperatura)
                VALUES (:id, :data, :id_sensor, :delta, :umidade, :temperatura)
            """), dado)

        # PRESENCA
        result = sessao.execute(text("SELECT max(id) FROM presenca"))
        max_id_pres = result.fetchone()[0] or 0

        response_pres = requests.get(f"{config.url_api}?sensor=presence&id_inferior={max_id_pres}")
        dados_pres = response_pres.json()

        for dado in dados_pres:
            sessao.execute(text("""
                INSERT INTO presenca (id, data, id_sensor, delta, bateria, ocupado)
                VALUES (:id, :data, :id_sensor, :delta, :bateria, :ocupado)
            """), dado)

        # PASSAGEM
        result = sessao.execute(text("SELECT max(id) FROM passagem"))
        max_id_pass = result.fetchone()[0] or 0

        response_pass = requests.get(f"{config.url_api}?sensor=passage&id_inferior={max_id_pass}")
        dados_pass = response_pass.json()

        for dado in dados_pass:
            sessao.execute(text("""
                INSERT INTO passagem (id, data, id_sensor, delta, bateria, entrada, saida)
                VALUES (:id, :data, :id_sensor, :delta, :bateria, :entrada, :saida)
            """), dado)
    
    return jsonify({
        "consolidado": banco.listarConsolidado(data_inicial, data_final)
	})
    
@app.get('/dados/temperatura/kpi')
def dados_temp_kpi():
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')

    if not data_inicial or not data_final:
        return jsonify({"erro": "Datas inválidas"}), 400

    try:
        with Session(banco.engine) as sessao, sessao.begin():
            result = sessao.execute(text("""
                SELECT MIN(temperatura), MAX(temperatura), AVG(temperatura)
                FROM temperatura
                WHERE data BETWEEN :inicio AND :fim
            """), {
                "inicio": data_inicial,
                "fim": data_final + " 23:59:59"
            })

            row = result.fetchone()
            if row is None or any(v is None for v in row):
                return jsonify({"min": None, "max": None, "avg": None}), 200

            min_temp, max_temp, avg_temp = row

        return jsonify({
            "min": round(min_temp, 1),
            "max": round(max_temp, 1),
            "avg": round(avg_temp, 1)
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.get("/dados/consolidado/dashboard")
def dados_consolidado_dashboard():
    data_inicial = request.args.get("data_inicial")
    data_final = request.args.get("data_final")
    
    lista = banco.listarConsolidado(data_inicial, data_final)

    total_entradas = 0
    total_saidas = 0
    dias = []
    valores_diarios = []

    for dado in lista:
        entradas = dado['total_entrada1'] + dado['total_entrada2'] + dado['total_entrada3']
        saidas = dado['total_saida1'] + dado['total_saida2'] + dado['total_saida3']
        total_entradas += entradas
        total_saidas += saidas
        dias.append(dado['dia'])
        valores_diarios.append(entradas + saidas)

    return jsonify({
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "movimento_diario": {
            "labels": dias,
            "valores": valores_diarios
        }
    })

    
@app.post('/criar')
def criar():
    dados = request.json
    print(dados['id'])
    print(dados['nome'])
    return Response(status=204)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)
