from flask import Flask, render_template, jsonify, request
import random
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from json import loads

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="qwen/qwen3-32b",
    api_key=os.getenv('GROQ_API_KEY'),
    temperature=0.0,
    reasoning_format="parsed"
)

#teste groq
resposta = llm.invoke("voce está funcinado?")
print(resposta)

SYSTEM_PROMPT =""""
Voce eh um agente inteligente que deve coletar o ouro e sair da arena. A arena é um grid 4x4, onde cada célula pode conter:
0: Célula vazia
1: Buraco (obstáculo)
2: Wumpus (alvo)
3: Agente (sua posição atual)

Você tem acesso às seguintes ferramentas:
move(direcao): Move o agente para uma casa adjacente válida. As direções podem ser 'up', 'down', 'left' ou 'right'.


Para usar uma ferramenta, você deve responder com um JSON no seguinte formato:
Action:
{
  "action": "NOME_DA_FERRAMENTA",
  "action_input": {"PARAMETRO": "VALOR"}
}
exemplo:
Action:
{
  "action": "move",
  "action_input": {"direcao": "up"}
}
"""

app = Flask(__name__)

# Inicializar a arena 4x4
arena = [[0 for _ in range(4)] for _ in range(4)]

class agente:
    def __init__(self):
        self.posicao = [1, 1]  # Posição inicial do agente
        self.has_arrow = True
        self.has_gold = False

#inicializar a arena com obstáculos e alvos
def initialize_game():
    global arena
    global person
    person = agente()

    arena = [[0 for _ in range(4)] for _ in range(4)]
    arena[person.posicao[0]][person.posicao[1]] = 3  # Posição inicial do agente

    #adiciona Buraco
    for _ in range(1):
        while True:
            x, y = random.randint(0, 3), random.randint(0, 3)
            if arena[x][y] == 0:
                arena[x][y] = 1  # Obstáculo
                break

    # Adiciona alguns alvos
    for _ in range(1):
        while True:
            x, y = random.randint(0, 3), random.randint(0, 3)
            if arena[x][y] == 0:
                arena[x][y] = 2  # Wumpus
                break

@app.route('/')
def index():
    initialize_game()
    return render_template('index.html')

@app.route('/api/arena')
def get_arena():
    return jsonify(arena)

@app.route('/api/reset')
def reset_arena():
    initialize_game()
    return jsonify({'arena': arena})


#`pegar_ouro()`: Coleta o ouro se estiver na mesma casa.
#`escalar_saida()`: Finaliza o jogo se o agente estiver na casa [1,1].

#`andar(direcao)`: Move o agente para uma casa adjacente válida.
@app.route('/api/move', methods=['POST'])
def move(direcao=None, direction=None):
    # Se chamado via POST, pega os dados do JSON
    if request.method == 'POST':
        data = request.get_json()
        direction = data.get('direction')
    # Se chamado pela IA, usa o argumento direcao ou direction
    elif direcao:
        direction = direcao
    
    data = {"direction": direction}
    return move_logic(data)

#`atirar(direcao)`: Dispara a única flecha na tentativa de matar o Wumpus.

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    global arena

    # Converter arena para string legível
    arena_str = "\n".join([" ".join(map(str, row)) for row in arena])

    # Prompt para a IA
    prompt = f"""{SYSTEM_PROMPT}

Estado atual da arena:
{arena_str}

Posição do agente: {person.posicao}
Tem flecha: {person.has_arrow}
Tem ouro: {person.has_gold}

Decida sua próxima ação baseada no estado atual."""

    try:
        # Chamar a IA
        response = llm.invoke(prompt)
        ai_response = response.content.strip()

        # Extrair ação da resposta da IA
        if "Action:" in ai_response:
            action_part = ai_response.split("Action:")[1].strip()
            import json
            action_data = json.loads(action_part)

            if action_data["action"] == "move":
                direction = action_data["action_input"]["direcao"]

                # Executar movimento
                data = {"direction": direction}
                # Simular a requisição para a função move
                move_result = move_logic(data)
                return move_result
        else:
            return jsonify({"error": "IA não retornou uma ação válida", "response": ai_response})

    except Exception as e:
        return jsonify({"error": f"Erro na IA: {str(e)}"})

def move_logic(data):
    """Lógica de movimento extraída da função move() para reutilização"""
    direction = data.get('direction')
    global arena
    
    consequence = 'invalid'  # Valor padrão

    # Encontrar posição do agente
    row, col = person.posicao

    if direction == 'up':
        if row == 0:
            consequence = 'bumped'
        elif arena[row - 1][col] == 1:  # Verifica se é buraco
            arena[row][col] = 0
            arena[row - 1][col] = 4  # Marca o agente como morto
            consequence = 'falled'
        else:
            arena[row][col] = 0
            arena[row - 1][col] = 3
            person.posicao = [row - 1, col]  # Atualiza a posição do agente
            consequence = 'moved'

    elif direction == 'down':
        if row == 3:
            consequence = 'bumped'
        elif arena[row + 1][col] == 1:
            arena[row][col] = 0
            arena[row + 1][col] = 4  # Marca o agente como morto
            consequence = 'falled'
        else:
            arena[row][col] = 0
            arena[row + 1][col] = 3
            person.posicao = [row + 1, col]  # Atualiza a posição do agente
            consequence = 'moved'

    elif direction == 'left':
        if col == 0:
            consequence = 'bumped'
        elif arena[row][col - 1] == 1:
            arena[row][col] = 0
            arena[row][col - 1] = 4  # Marca o agente como morto
            consequence = 'falled'
        else:
            arena[row][col] = 0
            arena[row][col - 1] = 3
            person.posicao = [row, col - 1]  # Atualiza a posição do agente
            consequence = 'moved'

    elif direction == 'right':
        if col == 3:
            consequence = 'bumped'
        elif arena[row][col + 1] == 1:
            arena[row][col] = 0
            arena[row][col + 1] = 4  # Marca o agente como morto
            consequence = 'falled'
        else:
            arena[row][col] = 0
            arena[row][col + 1] = 3
            person.posicao = [row, col + 1]  # Atualiza a posição do agente
            consequence = 'moved'

    return jsonify({'arena': arena, 'consequence': consequence, 'ai_decision': direction})

@app.route('/api/command', methods=['POST'])
def command():
    mensagemUser = request.json.get('command')

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mensagemUser}
    ]
    print("iniciando IA\n")
    for i in range (10):
        print(f"-------tentativa {i+1}-------\n")

        response = llm.invoke(messages)
        respostaIA = response.content.strip()
        print(respostaIA)

        if "Final Answer:" in respostaIA:
            break
        
        if "Action:" in respostaIA:
            resultadoFerramenta = call_tool(respostaIA)
            print(f"Resultado da ferramenta: {resultadoFerramenta}\n")
            historico_turno = respostaIA + "\nResultado da ferramenta: " + str(resultadoFerramenta) +"\n"
            messages.append({"role": "assistant", "content": historico_turno})
        else:
            print("IA não retornou uma ação válida. Encerrando o loop.")
            break
    else:
        print("IA não chegou a uma resposta final após 10 tentativas.")
    

def get_user_info():
    return jsonify({
        "position": person.posicao,
        "has_arrow": person.has_arrow,
        "has_gold": person.has_gold
    })

def call_tool(response: str) -> str:
    tool_call = loads(response.split("Action:")[1])
    kwargs = tool_call["action_input"]
    match tool_call["action"]:
        case "move":
            return move(**kwargs)
        case "get_user_info":
            return get_user_info()
        case "borrow_book":
            return 
        case "return_book":
            return 
        case _:
            return f'A ferramenta "{tool_call["action"]}" não existe. Confirme as funções disponíveis.'

if __name__ == '__main__':
    print("Servidor iniciando em http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)