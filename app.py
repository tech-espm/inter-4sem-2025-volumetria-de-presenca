from flask import Flask, jsonify, render_template, json, request, Response
import config
import requests
from datetime import datetime
from banco import engine

app = Flask(__name__)

@app.get('/')
def index():
    hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/index.html', hoje=hoje)

@app.get('/sobre')
def sobre():
    return render_template('index/sobre.html', titulo='Sobre Nós')

@app.route("/obterDados")
def obterDados():
    with engine.connect() as conn:
        # TEMPERATURA
        result = conn.execute("SELECT max(id) FROM temperatura")
        max_id_temp = result.fetchone()[0] or 0

        response_temp = requests.get(f"{config.url_api}?sensor=temperature&id_inferior={max_id_temp}")
        dados_temp = response_temp.json()

        for dado in dados_temp:
            try:
                conn.execute("""
                    INSERT INTO temperatura (id, data, id_sensor, delta, umidade, temperatura)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    dado['id'], dado['data'], dado['id_sensor'],
                    dado['delta'], dado['umidade'], dado['temperatura']
                ))
            except Exception as e:
                print(f"Erro ao inserir temperatura: {e}")

        # PRESENCA
        result = conn.execute("SELECT max(id) FROM presenca")
        max_id_pres = result.fetchone()[0] or 0

        response_pres = requests.get(f"{config.url_api}?sensor=presence&id_inferior={max_id_pres}")
        dados_pres = response_pres.json()

        for dado in dados_pres:
            try:
                conn.execute("""
                    INSERT INTO presenca (id, data, id_sensor, delta, bateria, ocupado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    dado['id'], dado['data'], dado['id_sensor'],
                    dado['delta'], dado['bateria'], dado['ocupado']
                ))
            except Exception as e:
                print(f"Erro ao inserir presenca: {e}")

        # PASSAGEM
        result = conn.execute("SELECT max(id) FROM passagem")
        max_id_pass = result.fetchone()[0] or 0

        response_pass = requests.get(f"{config.url_api}?sensor=passage&id_inferior={max_id_pass}")
        dados_pass = response_pass.json()

        for dado in dados_pass:
            try:
                conn.execute("""
                    INSERT INTO passagem (id, data, id_sensor, delta, bateria, entrada, saida)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    dado['id'], dado['data'], dado['id_sensor'],
                    dado['delta'], dado['bateria'], dado['entrada'], dado['saida']
                ))
            except Exception as e:
                print(f"Erro ao inserir passagem: {e}")
    
    return jsonify(dados_temp + dados_pres + dados_pass)
    
@app.post('/criar')
def criar():
    dados = request.json
    print(dados['id'])
    print(dados['nome'])
    return Response(status=204)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)
