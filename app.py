from flask import Flask, request, render_template, jsonify;

import sqlite3;

from flask_cors import CORS

#--------------------------CRIAÇÃO DA TABELA DE AGENDAMENTO----------------------------------------

app = Flask(__name__)

CORS(app)

def nova_agenda():
    with sqlite3.connect('agenda.db') as conn:
        conn.execute("""
                CREATE TABLE IF NOT EXISTS agendamento(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        dia TEXT NOT NULL,
                        horario TEXT NOT NULL,
                        especialidade_exame TEXT NOT NULL,
                        convenio TEXT NOT NULL
                    )
""")
    print('Banco de dados iniciado')

nova_agenda()

#-------------------------------MOSTRA AS INFORMAÇÕES E CONSUMO DA API-----------------------------------

@app.route("/")
def home_page():
        return render_template("index.html")

#----------------------------------METODOS DE CONSUMO DA API----------------------------------------
#POST: Insere os dados na tabela criada

@app.route("/agendamento" , methods =['POST'])
def novo_agendamento():
    dados = request.get_json()

    nome = dados.get("nome")
    dia = dados.get("dia")
    horario = dados.get("horario")
    especialidade_exame = dados.get("especialidade_exame")
    convenio = dados.get("convenio")

    if not all ([nome, dia, horario, especialidade_exame, convenio]):
        return jsonify({'erro': "Todos os campos devem ser preenchidos"}), 400


    with sqlite3.connect('agenda.db') as conn:
        conn.execute("""INSERT INTO agendamento(nome, dia, horario, especialidade_exame, convenio) VALUES (? , ? , ? , ? , ?)""" , (nome, dia, horario, especialidade_exame, convenio))
        conn.commit()

        return jsonify({'mensagem': "Agendamento concluído com sucesso!"}), 201
    
#----------------------------------METODOS DE CONSUMO DA API----------------------------------------
#GET: mostra os dados inseridos

@app.route("/visualizar" , methods =['GET'])
def agendamentos_realizados():
    with sqlite3.connect('agenda.db') as conn:
        agendado = conn.execute("SELECT * FROM agendamento").fetchall()

    dado_agenda = [
        {
            'id': item[0],
            'nome': item[1],
            'dia': item[2],
            'horario': item[3],
            'especialidade_exame': item[4],
            'convenio': item[5]
        }
        for item in agendado
    ]
    return jsonify(dado_agenda)

#----------------------------------METODOS DE CONSUMO DA API----------------------------------------
#PUT: atualiza os dados existentes

@app.route('/update/<int:id>', methods=['PUT'])
def modificar_agenda(id):
    dados = request.get_json()

    # Validação consistente das chaves
    chaves_necessarias = {"dia", "horario", "nome", "especialidade_exame", "convenio"}
    if not chaves_necessarias.issubset(dados):
        return jsonify({'erro': "Faltam informações, agendamento não foi atualizado!"}), 400

    try:
        with sqlite3.connect('agenda.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agendamento
                SET dia = ?, horario = ?, nome = ?, especialidade_exame = ?, convenio = ?
                WHERE id = ?
            """, (dados["dia"], dados["horario"], dados["nome"], dados["especialidade_exame"], dados["convenio"], id))
            
            if cursor.rowcount == 0:  # Verifica se alguma linha foi alterada
                return jsonify({'erro': "Não houve alteração nos agendamentos!"}), 404

        return jsonify({'mensagem': "Alteração concluída, agendamento atualizado!"})

    except sqlite3.Error as e:
        return jsonify({'erro': f"Ocorreu um erro ao atualizar: {str(e)}"}), 500

#----------------------------------METODOS DE CONSUMO DA API----------------------------------------
#DELETE: exclui os dados existentes

@app.route('/delete/<int:id>', methods=['DELETE'])
def excluir(id):
    try:
        with sqlite3.connect('agenda.db') as conn:
            cursor = conn.cursor()  # Captura o cursor para realizar operações
            cursor.execute('DELETE FROM agendamento WHERE id = ?', (id,))
            
            # Verifica se alguma linha foi afetada
            if cursor.rowcount == 0:
                return jsonify({'erro': "Não constam estas informações na base!"}), 404

        return jsonify({'mensagem': "Este agendamento foi excluído da base!"}), 200

    except sqlite3.Error as e:
        return jsonify({'erro': f"Ocorreu um erro no banco de dados: {str(e)}"}), 500


#verifica se este é o script principal e inicia o depurador para detalhes de erros
if __name__ == '__main__':
    app.run(debug=True)