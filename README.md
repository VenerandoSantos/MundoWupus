# 🎮 MundoWunpus - Arena 8x8

Aplicação web em Python que simula uma arena 8x8 interativa com visualização em tempo real no navegador.

## 📋 Pré-requisitos

- **Python 3.7+** instalado no seu computador
- **pip** (gerenciador de pacotes Python)

## 🚀 Como Rodar

### 1️⃣ Clonar ou Acessar o Projeto

```bash
git clone https://github.com/VenerandoSantos/MundoWupus
```

### 2️⃣ Instalar as Dependências

```bash
pip install -r requirements.txt
```

Isso irá instalar:
- **Flask** - Framework web Python
- **Werkzeug** - Utilitários para WSGI

### 3️⃣ Executar o Servidor

```bash
python app.py
```

Você verá uma mensagem no terminal:
```
Servidor iniciando em http://localhost:5000
 * Running on http://localhost:5000
```

### 4️⃣ Abrir no Navegador

1. Abra seu navegador favorito (Chrome, Firefox, Edge, etc.)
2. Acesse: **http://localhost:5000**
3. Você verá a arena carregada e interativa!

## 📁 Estrutura do Projeto

```
MundoWunpus/
├── app.py                  # Backend Flask - Lógica da arena
├── requirements.txt        # Dependências Python
├── templates/
│   └── index.html         # Frontend - Interface web
└── README.md              # Este arquivo
```

## 🎯 Recursos da Arena

| Símbolo | Significado |
|---------|------------|
| ⬜ | Célula vazia |
| 🚫 | Obstáculo |
| 🎯 | Alvo |

## 🕹️ Como Usar

- **Visualizar Arena**: A arena aparece automaticamente ao acessar o site
- **Resetar Arena**: Clique no botão "Resetar Arena" para gerar uma nova com elementos aleatórios
- **EmDesenvolvimento**: 

## ⚙️ Configuração

Para alterar a porta ou outras configurações, edite o arquivo `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)  # Altere aqui
```

- `host='localhost'` - Apenas acessível localmente
- `port=5000` - Porta do servidor
- `debug=True` - Modo de desenvolvimento com auto-reload

## 🛑 Para o Servidor

No terminal onde o servidor está rodando, pressione:
- **Ctrl + C** - Interrompe o servidor

## ❓ Troubleshooting

### Porta 5000 já está em uso?
```bash
# Use uma porta diferente editando app.py
app.run(debug=True, host='localhost', port=8000)
```

### Flask não está instalado?
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erro "ModuleNotFoundError: No module named 'flask'"?
Certifique-se de executar o comando `pip install -r requirements.txt` na pasta do projeto.

## 🔧 Próximas Funcionalidades

Você pode expandir o projeto com:
- 🤖 Inteligência Artificial para mover personagens
- 🎮 Sistema de pontuação
- 👾 Múltiplos personagens
- 💾 Salvar/Carregar estado da arena
- 🎨 Temas e customização

## 📝 Licença

Projeto de desenvolvimento livre

---

**Divirta-se explorando o MundoWunpus!** 🚀
