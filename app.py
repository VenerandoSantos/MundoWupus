from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

# Inicializar a arena 4x4
arena = [[0 for _ in range(4)] for _ in range(4)]

#inicializar a arena com obstáculos e alvos
def initialize_arena():
    global arena
    arena = [[0 for _ in range(4)] for _ in range(4)]
    arena[0][0] = 3  # Posição inicial do agente
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
                arena[x][y] = 2  # wunpu
                break

@app.route('/')
def index():
    initialize_arena()
    return render_template('index.html')

@app.route('/api/arena')
def get_arena():
    return jsonify(arena)

@app.route('/api/reset')
def reset_arena():
    initialize_arena()
    return jsonify({'arena': arena})

@app.route('/api/move', methods=['POST'])
def move():
    data = request.get_json()
    direction = data.get('direction')
    global arena
    
    # Encontrar posição do agente
    agent_pos = None
    for i in range(4):
        for j in range(4):
            if arena[i][j] == 3:
                agent_pos = (i, j)
                break
    
    if agent_pos is None:
        return jsonify({'arena': arena})
    
    row, col = agent_pos
    
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
            consequence = 'moved'
    
    return jsonify({'arena': arena,'consequence': consequence})

if __name__ == '__main__':
    print("Servidor iniciando em http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)