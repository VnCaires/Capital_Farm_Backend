# Free Farm Backend

Backend da aplicação Free Farm desenvolvido com FastAPI.

## Instalação

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/Free_Farm_Backend.git
cd Free_Farm_Backend
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
```

### 3. Ativar ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Instalar dependências
```bash
pip install -r requirements.txt
```

## Executar

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: `http://localhost:8000`
Documentação: `http://localhost:8000/docs`

## Endpoints

- `POST /register` - Registrar novo jogador
- `POST /login` - Fazer login
- `GET /me` - Obter dados do jogador autenticado

## Estrutura do Projeto

```
app/
  ├── __init__.py
  ├── auth.py         # Lógica de autenticação
  ├── crud.py         # Operações de banco de dados
  ├── database.py     # Configuração do banco
  ├── main.py         # Endpoints da API
  ├── models.py       # Modelos SQLAlchemy
  └── schemas.py      # Schemas Pydantic
```
