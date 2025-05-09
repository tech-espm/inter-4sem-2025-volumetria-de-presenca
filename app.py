from flask import Flask, jsonify, render_template, json, request, Response
import config
import requests
from datetime import datetime
from banco import engine
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

app = Flask(__name__)

@app.get('/')
def index():
    hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/index.html', hoje=hoje)

@app.get('/sobre')
def sobre():
    return render_template('index/sobre.html', titulo='Sobre Nós')

@app.get("/dashboard")
def dashboard():
    return render_template('index/dashboard.html', titulo='Dashboard')


@app.get('/dados/temperatura')
def dados_temp():
    with Session(engine) as sessao, sessao.begin():
        result = sessao.execute(text("""
            SELECT data, temperatura, umidade
            FROM temperatura
            WHERE (HOUR(data) * 60 + MINUTE(data)) % 90 = 0
            ORDER BY data DESC
            LIMIT 100
        """))
        dados = result.fetchall()
        dados = [
            {
                "data": row["data"].strftime("%d/%m %H:%M"),
                "temperatura": row["temperatura"],
                "umidade": row["umidade"]
            } for row in dados
        ]
    return jsonify(dados)


@app.route("/obterDados")
def obterDados():
    with Session(engine) as sessao, sessao.begin():
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
    
    return jsonify(dados_temp + dados_pres + dados_pass)
    
@app.post('/criar')
def criar():
    dados = request.json
    print(dados['id'])
    print(dados['nome'])
    return Response(status=204)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)
