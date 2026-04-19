from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# Inicializar a arena 4x4
arena = [[0 for _ in range(4)] for _ in range(4)]

class agente:
    def __init__(self):
        self.posicao = [1, 1]  # Posição inicial do agente
        self.has_arrow = True
        self.has_gold = False

    def resetar(self):
        self.posicao = [1, 1]
        self.has_arrow = True
        self.has_gold = False

#inicializar a arena com obstáculos e alvos
def initialize_game():
    global arena
    global person
    person = agente()

    arena = [[0 for _ in range(4)] for _ in range(4)]
    arena[person.posicao[0]][person.posicao[1]] = 3  # Posição inicial do agente
    for _ in range(1):
        while True:
            x, y = random.randint(0, 3), random.randint(0, 3)
            if arena[x][y] == 0:
                arena[x][y] = 1  # Obstáculo
                break

    # Adicionar alguns alvos
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
def move():
    data = request.get_json()
    direction = data.get('direction')
    global arena
    
    # Encontrar posição do agente
    row, col = person.posicao
    
    if direction == 'up':
        if row == 0:
            consequence = 'bumbed'
        elif arena[row - 1][col] == 1:  # Verifica se não é obstáculo
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
            consequence = 'bumbed'  
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
            consequence = 'bumbed'
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
            consequence = 'bumbed'
        elif arena[row][col + 1] == 1:
            arena[row][col] = 0
            arena[row][col + 1] = 4  # Marca o agente como morto
            consequence = 'falled'
        else:
            arena[row][col] = 0
            arena[row][col + 1] = 3
            person.posicao = [row, col + 1]  # Atualiza a posição do agente
            consequence = 'moved'
    
    return jsonify({'arena': arena,'consequence': consequence})

#`atirar(direcao)`: Dispara a única flecha na tentativa de matar o Wumpus.

if __name__ == '__main__':
    print("Servidor iniciando em http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)