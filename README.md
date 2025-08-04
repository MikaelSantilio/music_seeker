# MusicSeeker 🎵

  ![MusicSeeker Interface](/static/thumb.png)

**MusicSeeker** é uma API que permite buscar músicas usando **busca semântica baseada em embeddings da OpenAI**, feita utilizando vibe coding, que usa um dataset local de letras de músicas.

## Características

- **Busca Semântica**: Encontre músicas por significado, não apenas palavras exatas
- **Dataset Local**: 21 artistas populares com centenas de músicas
- **PostgreSQL + pgvector**: Busca vetorial eficiente
- **Docker**: Fácil deploy e desenvolvimento

## Estrutura do Projeto

```
music_seeker_v2/
├── app/
│   ├── __init__.py
│   ├── api/          # Endpoints da API
│   ├── db/           # Configuração do banco
│   ├── models/       # Modelos SQLAlchemy
│   └── services/     # Lógica de negócio
├── scripts/          # Scripts de configuração
├── tests/           # Testes automatizados
├── data/            # Dataset de letras (21 artistas)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup Desenvolvimento

### 1. Clonar e preparar ambiente

```bash
git clone <repo-url>
cd music_seeker_v2

# Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com sua API key da OpenAI
```

### 3. Subir com Docker Compose

```bash
docker-compose up -d
```

Isso irá subir:
- **API**: http://localhost:8000
- **Banco PostgreSQL**: localhost:5432
- **pgAdmin**: http://localhost:8080

## Preparar Dados

### 1. Carregar dataset no banco

```bash
python scripts/load_data.py
```

### 2. Gerar embeddings

```bash
python scripts/generate_embeddings.py
```

## Usando a API

### Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Exemplos de Uso

#### Listar músicas
```bash
curl "http://localhost:8000/songs?limit=10"
```

#### Busca semântica
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "love and heartbreak", "limit": 5}'
```

#### Estatísticas
```bash
curl "http://localhost:8000/stats"
```

## Artistas no Dataset

O dataset inclui letras de 21 artistas populares:
- Taylor Swift, Drake, BTS, Ariana Grande
- Beyoncé, Billie Eilish, Ed Sheeran, Eminem
- E mais 13 artistas...

## Testes

```bash
pytest tests/ -v
```

## Licença

MIT License - veja LICENSE para detalhes.

---
