
# # A very simple Flask Hello World app for you to get started with...

# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello from Flask!'

from flask import Flask, request, jsonify, render_template_string
from chat_hander import init_chat, continue_chat
from functools import wraps
import json

from config import TOKEN

app = Flask(__name__)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token de autorização ausente!'}), 403
        if token != f"Bearer {TOKEN}":
            return jsonify({'message': 'Token inválido!'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    """
    Rota para verificar se o site está online.
    Retorna uma página HTML com o texto "IFTUTOR".
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IFTUTOR</title>
    </head>
    <body>
        <h1>IFTUTOR</h1>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/start_chat', methods=['POST'])
@token_required  # Protege a view com o token de autorização
def start_chat():
    """
    Rota para iniciar um novo chat com o estudante.
    """
   # Verifica se a requisição contém dados JSON
    if request.content_type == 'application/json':
        data = json.loads(request.data)  # Decodifica o JSON da requisição

        # Agora você pode acessar os campos do JSON, por exemplo:
        nome = data.get('nome')
        curso_periodo = data.get('curso_periodo')
        idade = data.get('idade')
        estilo_aprendizagem = data.get('estilo_aprendizagem')
        disciplinas_afinidade = data.get('disciplinas_afinidade')
        disciplinas_dificuldade = data.get('disciplinas_dificuldade')
        autoavaliacao_desempenho = data.get('autoavaliacao_desempenho')
        horarios_disponiveis = data.get('horarios_disponiveis')

        tipo = request.args.get('tipo', '').upper()

       # Iniciar o chat
        response, chat_store_key = init_chat(
            nome, curso_periodo, idade, estilo_aprendizagem,
            disciplinas_afinidade, disciplinas_dificuldade,
            autoavaliacao_desempenho, horarios_disponiveis,
            tipo
        )
        return jsonify({'message': 'Chat iniciado com sucesso!', "response": str(response), "chat_store_key": chat_store_key}, 200)


    return jsonify({'message': 'Formato de dados inválido, JSON esperado!'}), 400


@app.route('/continue_chat', methods=['POST'])
@token_required  # Protege a view com o token de autorização
def continue_chat_route():
    """
    Rota para continuar um chat com uma nova mensagem.
    """
    if request.content_type == 'application/json':
        data = json.loads(request.data)  # Decodifica o JSON da requisição
        # Extrair chat_store_key e nova mensagem
        chat_store_key = data.get('chat_store_key')
        new_message = data.get('new_message')

        # Continuar o chat
        response = continue_chat(chat_store_key, new_message)

        # Retornar a resposta gerada
        return jsonify({'message': 'Chat continuado com sucesso!', "response": str(response), "chat_store_key": chat_store_key}, 200)

    return jsonify({'message': 'Formato de dados inválido, JSON esperado!'}), 400

if __name__ == '__main__':
    app.run(debug=True)