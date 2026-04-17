from flask import Flask, render_template, jsonify
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
    return jsonify(arena)

if __name__ == '__main__':
    print("Servidor iniciando em http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)