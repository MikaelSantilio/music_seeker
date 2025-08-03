# 🎵 MusicSeeker API Documentation

> **Busca semântica de músicas usando inteligência artificial**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 🚀 Visão Geral

O **MusicSeeker** é uma API REST que permite buscar músicas usando **linguagem natural** e **inteligência artificial**. Em vez de procurar por palavras-chave exatas, você pode descrever o **sentimento**, **mood** ou **tema** que procura!

### ✨ Principais Funcionalidades

- 🔍 **Busca Semântica**: "nostalgia and lost love" → encontra "Memories" do Maroon 5
- 🤖 **IA Integrada**: Powered by OpenAI text-embedding-3-small
- ⚡ **Ultra Rápido**: Respostas em milissegundos usando pgvector
- 🛡️ **Seguro**: Rate limiting, validação robusta, headers de segurança
- 📊 **Analytics**: Estatísticas detalhadas da biblioteca musical

### 📈 Dados Disponíveis

- **5,949 músicas** com letras completas
- **21 artistas** populares (Ed Sheeran, Taylor Swift, Maroon 5, etc.)
- **100% cobertura** de embeddings vetoriais
- **Busca por similaridade** com scores de 0.0 a 1.0

## 🎯 Como Usar

### 1. 📖 Documentação Interativa

Acesse a documentação Swagger interativa:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. 🔍 Busca Semântica

**Endpoint**: `POST /api/v1/search`

#### Exemplos de Consulta

```json
{
  "query": "nostalgia and lost love",
  "limit": 10,
  "similarity_threshold": 0.3
}
```

#### Tipos de Busca que Funcionam Bem

| Consulta | Descrição | Exemplo de Resultado |
|----------|-----------|---------------------|
| `"nostalgia and lost love"` | Sentimentos melancólicos | "Memories" - Maroon 5 |
| `"party vibes and celebration"` | Músicas animadas | "Uptown Funk" - Bruno Mars |
| `"heartbreak and sadness"` | Baladas emotivas | "Someone Like You" - Adele |
| `"summer and freedom"` | Hits de verão | "California Gurls" - Katy Perry |
| `"motivation and strength"` | Músicas inspiradoras | "Stronger" - Kelly Clarkson |

### 3. 📊 Estatísticas

**Endpoint**: `GET /api/v1/stats`

Obtenha informações sobre:
- Total de músicas e artistas
- Cobertura de embeddings
- Top artistas por número de músicas
- Distribuição por ano
- Média de tamanho das letras

### 4. 🎵 Gestão de Músicas

**Endpoints**: 
- `GET /api/v1/songs` - Listar músicas
- `GET /api/v1/songs/{id}` - Obter música específica
- `POST /api/v1/songs` - Adicionar nova música

## 🔧 Configuração e Instalação

### 1. Pré-requisitos

```bash
# Python 3.13+
python --version

# PostgreSQL com pgvector
sudo apt install postgresql postgresql-contrib
```

### 2. Instalação

```bash
# Clonar repositório
git clone <repository-url>
cd music_seeker_v2

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\\Scripts\\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar configurações
nano .env
```

**Variáveis de Ambiente**:

```properties
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-YOUR_API_KEY_HERE

# Database Configuration  
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/musicseeker

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Debug
DEBUG=false
```

### 4. Banco de Dados

```bash
# Criar banco PostgreSQL
sudo -u postgres createdb musicseeker

# Instalar pgvector
sudo -u postgres psql musicseeker -c "CREATE EXTENSION vector;"

# Executar migrações (aplicação faz automaticamente)
python -c "from app.db.database import create_tables; create_tables()"
```

### 5. Executar

```bash
# Modo desenvolvimento
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Modo produção
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🛡️ Segurança

### Implementações de Segurança

- ✅ **Rate Limiting**: 10 requests/minuto por IP
- ✅ **Input Validation**: Proteção contra SQL injection
- ✅ **Security Headers**: X-Frame-Options, CSP, XSS Protection
- ✅ **CORS Restritivo**: Origens específicas apenas
- ✅ **Request Size Limits**: Máximo 1MB por request
- ✅ **Suspicious Pattern Detection**: Monitoramento de ataques
- ✅ **Secure Logging**: Filtragem de dados sensíveis

### Auditoria de Segurança

```bash
# Executar script de auditoria
./security_audit.py

# Resultado esperado
✅ NO CRITICAL SECURITY ISSUES FOUND!
🎉 Your MusicSeeker installation appears secure!
```

## 📊 Performance

### Benchmarks

- **Busca Semântica**: ~50-100ms por consulta
- **Throughput**: 600+ requests/minuto (com rate limiting)
- **Embedding Generation**: ~$0.0001 por música
- **Storage**: ~2KB por embedding (1536 dimensões)

### Otimizações

- **pgvector**: Índices vetoriais para busca rápida
- **Connection Pooling**: SQLAlchemy com pool de conexões
- **Caching**: Headers de cache para respostas estáticas
- **Compression**: Gzip automático para responses grandes

## 🐳 Docker

### Desenvolvimento

```bash
# Construir e executar
docker-compose up --build

# Apenas serviços (sem build)
docker-compose up
```

### Produção

```bash
# Build da imagem
docker build -t musicseeker:latest .

# Executar container
docker run -d \
  --name musicseeker \
  -p 8000:8000 \
  --env-file .env \
  musicseeker:latest
```

## 🧪 Testes

### Executar Testes

```bash
# Testes unitários
pytest tests/

# Testes de integração
pytest tests/integration/

# Testes de segurança
./security_audit.py

# Teste completo do sistema
python scripts/test_system.py
```

### Coverage

```bash
# Gerar relatório de cobertura
pytest --cov=app tests/
coverage html
```

## 🚀 Deploy em Produção

### 1. Preparação

```bash
# Atualizar dependências
pip freeze > requirements.txt

# Executar auditoria de segurança
./security_audit.py

# Testes completos
pytest tests/
```

### 2. Variáveis de Ambiente Produção

```properties
DEBUG=false
OPENAI_API_KEY=sk-proj-PRODUCTION_KEY
DATABASE_URL=postgresql+psycopg://user:secure_password@prod_host:5432/musicseeker
```

### 3. Servidor

```bash
# Com Gunicorn (recomendado)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Com Nginx (proxy reverso)
# Configurar nginx.conf apropriadamente
```

## 📚 API Reference

### Busca Semântica

```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "nostalgia and lost love",
  "limit": 10,
  "similarity_threshold": 0.3
}
```

**Response:**
```json
{
  "query": "nostalgia and lost love",
  "results": [
    {
      "song": {
        "id": 1,
        "track_name": "Memories",
        "artist_name": "Maroon 5",
        "album": "Jordi",
        "year": 2019,
        "lyrics": "Here's to the ones that we got..."
      },
      "similarity": 0.85
    }
  ],
  "total_results": 1,
  "processing_time_ms": 45.2
}
```

### Estatísticas

```http
GET /api/v1/stats
```

**Response:**
```json
{
  "total_songs": 5949,
  "total_artists": 21,
  "songs_with_embeddings": 5949,
  "embedding_coverage": 100.0,
  "top_artists": [
    {"artist": "Ed Sheeran", "count": 150},
    {"artist": "Taylor Swift", "count": 140}
  ],
  "year_range": {"min": 1950, "max": 2024}
}
```

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Crie** uma branch feature (`git checkout -b feature/amazing-feature`)
3. **Commit** suas mudanças (`git commit -m 'Add amazing feature'`)
4. **Push** para a branch (`git push origin feature/amazing-feature`)
5. **Abra** um Pull Request

### Guidelines

- Siga o padrão de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação
- Execute a auditoria de segurança

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

### Problemas Comuns

**1. API não encontra resultados**
- Verifique se os embeddings foram gerados
- Execute: `python scripts/generate_embeddings.py`

**2. Erro de conexão com banco**
- Verifique se PostgreSQL está rodando
- Confirme as credenciais no `.env`

**3. Rate limit exceeded**
- Aguarde 1 minuto entre muitas requisições
- Em produção, considere aumentar o limite

### Contato

- **GitHub Issues**: [Reportar bugs](https://github.com/musicseeker/issues)
- **Email**: contact@musicseeker.com
- **Documentação**: http://localhost:8000/docs

---

**🎵 Desenvolvido com ❤️ para amantes de música e tecnologia!**
