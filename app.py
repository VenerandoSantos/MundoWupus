from flask import Flask, render_template, jsonify, request
import random
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
from json import loads

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

from langchain_groq import ChatGroq

status_linhas = []

llm = ChatGroq(
    model="qwen/qwen3-32b",
    api_key=os.getenv('GROQ_API_KEY'),
    temperature=0.0,
    reasoning_format="parsed"
)

app = Flask(__name__)

SYSTEM_PROMPT =""""
Voce eh um agente inteligente que deve coletar o ouro e sair da arena. A arena é um grid 4x4, seus movimentos sao decido com base em sentidos do ambiente,por isso voce deve explorar o ambiente , onde cada célula pode conter:
0: Célula vazia
1: Buraco (obstáculo)  deve ser evitado
2: Wumpus (monstro) deve ser evitado 
3: Agente (sua posição atual)
5: Ouro (objetivo) objetivo principal caso nao usuario nao especifique outra missao


Você tem acesso às seguintes ferramentas:
move(direcao): Move o agente para uma casa adjacente válida. As direções podem ser 'up', 'down', 'left' ou 'right'. e retorna uma consequência do movimento (ex: 'moved', 'bumped', 'falled').
getSentidos(): checa o ambiente atual do agente, como brilho do ouro na posição atual, fedor do wumpus no espaço vizinho e vento de buraco em uma area vizinha
pegar_ouro(): Coleta o ouro quando você está na mesma posição que ele (quando getSentidos retorna brilho=true na sua posição).

Nao invente nenhum cenario, Caso voce nao receba nada no getSentido(), Me envie um Final Answer: Sentido Perdido.

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

Sempre Um Comando de Cada vez.
O passa a passo de interação deve ser SEMPRE: 
Thought: Com base nas informações disponíveis, o que você acha que deveria fazer?
Action: (o bloco JSON acima)
Observation: (o resultado da ferramenta que eu te passarei)
Next: (o proximo passo do ciclo)
Final Answer: As observações e pensamentos não vão ficar disponíveis para o usuário. Crie uma resposta final em linguagem natural para ser apresentada ao usuário. Apenas escreva Final Answer quando tiver terminado tudo.

NUNCA, mas em  hiptese NENHUMA, invente resultado da ferramenta, é proibido.
"""

# Inicializar a arena 4x4
arena = [[0 for _ in range(4)] for _ in range(4)]

# Armazenar posições de objetos separadamente para não serem sobrescritos
objetos = {
    'ouro': None,      # Posição do ouro (x, y)
    'buraco': None,    # Posição do buraco (x, y)
    'wumpus': None     # Posição do Wumpus (x, y)
}

def getSentidos():
    global person, objetos
    row, col = person.posicao
    brilho = False
    fedor = False
    vento = False

    # Verificar se tem ouro na posição e somente na atual
    if objetos['ouro'] is not None:
        ouro_x, ouro_y = objetos['ouro']
        # Ouro na posição atual
        if ouro_x == row and ouro_y == col:
            brilho = True

    # Verificar buraco nas vizinhas
    if objetos['buraco'] is not None:
        buraco_x, buraco_y = objetos['buraco']
        if (abs(buraco_x - row) == 1 and buraco_y == col) or (abs(buraco_y - col) == 1 and buraco_x == row):
            vento = True
    
    # Verificar Wumpus nas vizinhas
    if objetos['wumpus'] is not None:
        wumpus_x, wumpus_y = objetos['wumpus']
        if (abs(wumpus_x - row) == 1 and wumpus_y == col) or (abs(wumpus_y - col) == 1 and wumpus_x == row):
            fedor = True

    sentidos = {
        "brilho": brilho,
        "fedor": fedor,
        "vento": vento
    }

    return sentidos

class agente:
    def __init__(self):
        self.posicao = [1, 1]  # Posição inicial do agente
        self.has_arrow = True
        self.has_gold = False

#inicializar a arena com obstáculos e alvos
def initialize_game():
    global arena, person, objetos
    person = agente()

    arena = [[0 for _ in range(4)] for _ in range(4)]
    arena[person.posicao[0]][person.posicao[1]] = 3  # Posição inicial do agente

    #adiciona Buraco
    while True:
        x, y = random.randint(0, 3), random.randint(0, 3)
        if (x, y) != tuple(person.posicao) and arena[x][y] == 0:
            arena[x][y] = 1  # Buraco
            objetos['buraco'] = (x, y)
            break

    # Adiciona Wumpus
    while True:
        x, y = random.randint(0, 3), random.randint(0, 3)
        if (x, y) != tuple(person.posicao) and arena[x][y] == 0:
            arena[x][y] = 2  # Wumpus
            objetos['wumpus'] = (x, y)
            break
    
    # Adiciona Ouro
    while True:
        x, y = random.randint(0, 3), random.randint(0, 3)
        if (x, y) != tuple(person.posicao) and arena[x][y] == 0:
            arena[x][y] = 5  # Ouro
            objetos['ouro'] = (x, y)
            break

@app.route('/')
def index():
    initialize_game()
    return render_template('index.html')

def render_arena_display():
    """Renderiza a arena incluindo todos os objetos sem sobrescrever o agente"""
    arena_display = [[arena[i][j] for j in range(4)] for i in range(4)]
    global person

    if person.posicao is not None:
        row, col = person.posicao
        arena_display[row][col] = 3
    
    # Recolocar buraco se não foi coletado/destruído
    if objetos['buraco'] is not None:
        x, y = objetos['buraco']
        if arena_display[x][y] == 0:
            arena_display[x][y] = 1
    
    # Recolocar Wumpus se não foi destruído
    if objetos['wumpus'] is not None:
        x, y = objetos['wumpus']
        if arena_display[x][y] == 0:
            arena_display[x][y] = 2
    
    # Adicionar ouro se não foi coletado
    if objetos['ouro'] is not None:
        x, y = objetos['ouro']
        if arena_display[x][y] == 0:
            arena_display[x][y] = 5
    
    return [list(row) for row in arena_display]


@app.route('/api/arena')
def get_arena():
    arena_display = render_arena_display()
    return jsonify(arena_display)


@app.route('/api/reset')
def reset_arena():
    initialize_game()
    arena_display = render_arena_display()
    return jsonify({'arena': arena_display})


@app.route('/api/move', methods=['POST'])
def move(direcao=None, direction=None):
    # Se chamado pela IA (função Python) com parâmetro direcao
    if direcao:
        direction = direcao
    # Se chamado via POST (API REST)
    elif direction is None:
        try:
            data = request.get_json()
            direction = data.get('direction')
        except:
            direction = None
    
    if direction is None:
        return jsonify({'consequence': 'invalid', 'direction': direction, 'arena': render_arena_display()})
    
    result = move_logic({'direction': direction})
    return jsonify(result)

def move_logic(data):
    """Lógica de movimento extraída da função move() para reutilização"""
    global arena, person, status_linhas
    
    direction = data.get('direction')
    consequence = 'invalid'  # Valor padrão
    
    # Validar direção
    if direction not in ['up', 'down', 'left', 'right']:
        return {'arena': render_arena_display(), 'consequence': consequence, 'direction': direction}
    
    # Encontrar posição do agente
    row, col = person.posicao

    if direction == 'up':
        status_linhas.append(f"Intenção de Movimento de Subida {row} {col} ")
        if row == 0:
            status_linhas.append("parede a cima")
            consequence = 'bumped'
        elif arena[row - 1][col] == 1:  # Verifica se é buraco
            person.posicao = [row - 1, col]  # Atualiza posição mesmo caindo
            arena[row][col] = 0
            consequence = 'falled'
            status_linhas.append("caiu no buraco")
        else:
            arena[row][col] = 0
            arena[row - 1][col] = 3
            person.posicao = [row - 1, col]  # Atualiza a posição do agente
            consequence = 'moved'
            status_linhas.append(f" para {person.posicao[0]} {person.posicao[1]}")

    elif direction == 'down':
        status_linhas.append(f"Intenção de Movimento de Baixo {row} {col} ")  
        if row == 3:
            consequence = 'bumped'
            status_linhas.append("parede a baixo")
        elif arena[row + 1][col] == 1:
            person.posicao = [row + 1, col]  # Atualiza posição mesmo caindo
            arena[row][col] = 0
            consequence = 'falled'
            status_linhas.append("caiu no buraco")
        else:
            arena[row][col] = 0
            arena[row + 1][col] = 3
            person.posicao = [row + 1, col]  # Atualiza a posição do agente
            consequence = 'moved'
            status_linhas.append(f" para {person.posicao[0]} {person.posicao[1]}")


    elif direction == 'left':
        status_linhas.append(f"Intenção de Movimento de Esquerda {row} {col} ")
        if col == 0:
            status_linhas.append("parede a esquerda")
            consequence = 'bumped'
        elif arena[row][col - 1] == 1:
            person.posicao = [row, col - 1]  # Atualiza posição mesmo caindo
            arena[row][col] = 0
            consequence = 'falled'
            status_linhas.append("caiu no buraco")
        else:
            arena[row][col] = 0
            arena[row][col - 1] = 3
            person.posicao = [row, col - 1]  # Atualiza a posição do agente
            consequence = 'moved'
            status_linhas.append(f" para {person.posicao[0]} {person.posicao[1]}")

    elif direction == 'right':
        status_linhas.append(f"Intenção de Movimento de Direita {row} {col} ")
        if col == 3:
            consequence = 'bumped'
            status_linhas.append("parede a direita")
        elif arena[row][col + 1] == 1:
            person.posicao = [row, col + 1]  # Atualiza posição mesmo caindo
            arena[row][col] = 0
            consequence = 'falled'
            status_linhas.append("caiu no buraco")
        else:
            arena[row][col] = 0
            arena[row][col + 1] = 3
            person.posicao = [row, col + 1]  # Atualiza a posição do agente
            consequence = 'moved'
            status_linhas.append(f" para {person.posicao[0]} {person.posicao[1]}")
    
    # Retornar dicionário (será convertido em JSON pela chamadora)
    arena_display = render_arena_display()
    result = {'arena': arena_display, 'consequence': consequence, 'direction': direction}
    return result

@app.route('/api/command', methods=['POST'])
def command():
    global person, arena, status_linhas
    
    # Resetar o histórico de status para cada comando
    status_linhas.clear()
    
    # Inicializar o jogo se ainda não foi inicializado
    if 'person' not in globals():
        initialize_game()
    
    mensagemUser = request.json.get('command')
    arena_history = []  # Histórico de estados da arena

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mensagemUser}
    ]
    print("iniciando IA\n")
    print(mensagemUser + "\n")
    print("\n");
    for i in range (20):
        print(f"-------tentativa {i+1}-------\n")

        response = llm.invoke(messages)
        respostaIA = response.content.strip()
        print(f"{i} + {respostaIA}")

        if "Final Answer:" in respostaIA:
            print("IA chegou a uma resposta final. Encerrando o loop.")
            arena_history.append(render_arena_display())
            status_linhas.append(f"rmais u dia feliz ebaa")
            break
        
        if "Action:" in respostaIA:
            resultadoFerramenta = call_tool(respostaIA)
            print(f"Resultado da ferramenta: {resultadoFerramenta}\n")
            print("charava")
            
            # Adicionar estado atual ao histórico após a ação
            arena_history.append(render_arena_display())
            
            historico_turno = respostaIA + "\nResultado da ferramenta: " + str(resultadoFerramenta) +"\n"
            messages.append({"role": "assistant", "content": historico_turno})
        else:
            print("IA não retornou uma ação válida. Encerrando os loops.")
            print(respostaIA)
            # Adicionar estado atual mesmo quando há erro
            arena_history.append(render_arena_display())
            break
    else:
        print("IA não chegou a uma resposta final após 10 tentativas.")
        # Adicionar estado final após max tentativas
        arena_history.append(render_arena_display())
    
    # Se o histórico estiver vazio, adicionar pelo menos o estado atual
    if not arena_history:
        arena_history.append(render_arena_display())
    
    # Usar o último estado do histórico
    final_arena = arena_history[-1] if arena_history else render_arena_display()
    print(f"\n{'='*60}")
    print(f"DEBUG: Arena sendo retornada: {final_arena}")
    print(f"DEBUG: Histórico tem {len(arena_history)} estados")
    print(f"DEBUG: posiçao do agente: {person.posicao}")
    print(f"\n--- STATUS DO MOVIMENTO ---")
    for i, status in enumerate(status_linhas, 1):
        print(f"{i}. {status}")
    print(f"{'='*60}\n")
    
    return jsonify({
        'arena': final_arena,
        'arena_history': arena_history,  # Novo: histórico de todos os estados
        'position': person.posicao,
        'has_arrow': person.has_arrow,
        'has_gold': person.has_gold,
        'status_movimentos': status_linhas  # Adicionado ao JSON para visualização
    })

def get_user_info():
    return jsonify({
        "position": person.posicao,
        "has_arrow": person.has_arrow,
        "has_gold": person.has_gold
    })

#`pegar_ouro()`: Coleta o ouro se estiver na mesma casa.
def pegar_ouro():
    global person, objetos
    row, col = person.posicao
    # Se o ouro está na posição do agente, coletá-lo
    if objetos['ouro'] is not None:
        ouro_x, ouro_y = objetos['ouro']
        if ouro_x == row and ouro_y == col:
            objetos['ouro'] = None  # Remove o ouro
            person.has_gold = True  # Marca que o agente tem o ouro

def call_tool(response: str) -> str:
    try:
        # Extrair o JSON após "Action:"
        action_text = response.split("Action:")[1].strip()
        
        # Encontrar o primeiro '{' e o último '}'
        start_idx = action_text.find('{')
        end_idx = action_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_str = action_text[start_idx:end_idx+1]
            tool_call = loads(json_str)
        else:
            return "Erro: Não consegui extrair o JSON da resposta da IA"
        
        kwargs = tool_call["action_input"]
        match tool_call["action"]:
            case "move":
                status_linhas.append(f"Açao de movimento")
                result = move(**kwargs)
                # Se for um Response do Flask, extrair JSON
                if hasattr(result, 'get_json'):
                    data = result.get_json()
                else:
                    data = result
                direction = data.get('direction', '?')
                consequence = data.get('consequence', 'unknown')
                return f"Movimento para {direction}: {consequence}"
            case "getSentidos":
                return f"Sentidos: {getSentidos()}"
            case "pegar_ouro":
                pegar_ouro()
                return "Ouro coletado com sucesso!"
            case "borrow_book":
                return 
            case "return_book":
                return 
            case _:
                return f'A ferramenta "{tool_call["action"]}" não existe. Confirme as funções disponíveis.'
    except Exception as e:
        return f"Erro ao processar ação da IA: {str(e)}"

if __name__ == '__main__':
    print("Servidor iniciando em http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)