# Projeto Interdisciplinar IV - Sistemas de Informação ESPM

<p align="center">
    <a href="https://www.espm.br/cursos-de-graduacao/sistemas-de-informacao/"><img src="https://raw.githubusercontent.com/tech-espm/misc-template/main/logo.png" alt="Sistemas de Informação ESPM" style="width: 375px;"/></a>
</p>

# Estudo Volumétrico de Presença

### 2025-01

## Visão Geral

O estudo volumétrico de presença se concentra em capturar dados tridimensionais sobre a ocupação e movimentação de pessoas dentro de um ambiente. Isso é feito por meio de sensores que mapeiam volumes físicos e detectam variações na densidade e posição das pessoas.

## Participantes

- [Fernando Sabella](https://github.com/caicara29)

- [Gabriel Prestes](https://github.com/gabrielpmcardoso)

- [Henrique Lecce](https://github.com/hqlcc)

- [Isabelle Dib](https://github.com/isa-dib)

- [João Helbel](https://github.com/joaohelbel)

## Objetivos do Projeto

O projeto está dividido em três principais objetivos:

- Monitorar a presença de alunos e professores em sala de aula.
- Ajustar temperatura, ventilação e iluminação de salas de aula automaticamente.
- Gerar um mapa de ocupação das salas de aula.

## Configuração do Projeto

Para executar, deve criar o arquivo `config.py` da seguinte forma:

```python
host = '0.0.0.0'
port = 3000
conexao_banco = 'mysql+mysqlconnector://usuario:senha@host/banco'
url_api = 'https://site.com'
```

Todos os comandos abaixo assumem que o terminal esteja com o diretório atual na raiz do projeto.

## Criação e Ativação do venv

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```
.venv\Scripts\activate
python app.py
```

## Mais Informações

https://flask.palletsprojects.com/en/3.0.x/quickstart/
https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/

# Licença

Este projeto é licenciado sob a [MIT License](https://github.com/tech-espm/inter-4sem-2025-volumetria-de-presenca/blob/main/LICENSE).

<p align="right">
    <a href="https://www.espm.br/cursos-de-graduacao/sistemas-de-informacao/"><img src="https://raw.githubusercontent.com/tech-espm/misc-template/main/logo-si-512.png" alt="Sistemas de Informação ESPM" style="width: 375px;"/></a>
</p>
