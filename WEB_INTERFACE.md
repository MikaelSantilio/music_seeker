# 🎵 MusicSeeker Web Interface

Uma interface web elegante e intuitiva para busca semântica de músicas, similar ao Google!

## 🌟 Características

### 🎨 **Design Inspirado no Google**
- Layout limpo e minimalista
- Gradiente visual moderno
- Animações suaves e responsivas
- Interface totalmente responsiva (mobile-friendly)

### 🔍 **Busca Semântica Inteligente**
- Busque por **significado** e **sentimentos**: "nostalgia e amor perdido"
- **Sugestões automáticas** de consultas populares
- Botão **"Estou com Sorte"** para descobrir músicas aleatórias
- Resultados com **score de similaridade** em tempo real

### ⚡ **Performance e UX**
- Busca em **tempo real** com feedback visual
- Loading states elegantes
- Tratamento de erros amigável
- Atalhos de teclado (`Ctrl+K` para focar, `Esc` para voltar)

## 🚀 Como Usar

### 1. **Iniciar o Servidor**
```bash
# Opção 1: Script automático
./start_web.sh

# Opção 2: Manual
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. **Acessar a Interface**
- **Interface Web**: http://localhost:8000/search
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. **Fazer Buscas**
Digite consultas como:
- **"heartbreak and sadness"** → Encontra músicas tristes
- **"dancing and party vibes"** → Músicas para festa
- **"love and romance"** → Canções românticas
- **"motivation and success"** → Hinos motivacionais
- **"nostalgia and memories"** → Músicas nostálgicas

## 🛠️ Tecnologias

### **Frontend**
- **HTML5/CSS3** com design responsivo
- **JavaScript vanilla** (sem frameworks pesados)
- **Google Fonts** (Inter) para tipografia moderna
- **CSS Grid/Flexbox** para layouts fluidos

### **Backend**
- **FastAPI** com integração de arquivos estáticos
- **SQLAlchemy ORM** para consultas seguras
- **PostgreSQL + pgvector** para busca vetorial
- **OpenAI embeddings** para análise semântica

## 📱 Interface Responsiva

### **Desktop** (1200px+)
- Layout completo com todas as funcionalidades
- Sidebar para filtros (futuro)
- Preview expandido de letras

### **Tablet** (768px-1199px)
- Layout adaptado para touch
- Botões maiores para melhor usabilidade
- Grid de resultados otimizado

### **Mobile** (< 768px)
- Interface compacta e focada
- Menu hamburger para opções
- Busca em tela cheia

## 🎯 Funcionalidades

### ✅ **Implementadas**
- [x] Interface de busca estilo Google
- [x] Integração completa com API
- [x] Resultados com scores de similaridade
- [x] Sugestões de consulta
- [x] Estados de loading e erro
- [x] Design responsivo
- [x] Atalhos de teclado
- [x] Headers de segurança (CSP, XSS Protection)

### 🔮 **Planejadas**
- [ ] Autenticação de usuários
- [ ] Histórico de buscas
- [ ] Playlists personalizadas
- [ ] Compartilhamento de resultados
- [ ] Filtros por artista/ano
- [ ] Player de música integrado
- [ ] Dark/Light theme toggle
- [ ] Analytics de uso

## 🔧 Configuração

### **Arquivos Estáticos**
```
static/
├── index.html      # Interface principal
├── style.css       # Estilos CSS
└── script.js       # Lógica JavaScript
```

### **Configuração do CORS**
```python
allow_origins=[
    "http://localhost:8000",  # Próprio servidor
    "http://localhost:3000",  # React dev
    "http://localhost:8080"   # Vue dev
]
```

### **CSP Headers**
```python
"script-src 'self' 'unsafe-inline' https://fonts.googleapis.com"
"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com"
"font-src 'self' https://fonts.gstatic.com"
```

## 🐛 Solução de Problemas

### **Interface não carrega**
```bash
# Verificar se arquivos estáticos existem
ls -la static/

# Verificar logs do servidor
tail -f logs/app.log
```

### **API não responde**
```bash
# Testar health check
curl http://localhost:8000/health

# Verificar database
python -c "from app.db.database import SessionLocal; SessionLocal().execute('SELECT 1')"
```

### **Busca não funciona**
```bash
# Testar endpoint manualmente
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "love", "limit": 5}'
```

## 📊 Métricas

A interface mostra estatísticas em tempo real:
- **Total de músicas** na base de dados
- **Número de artistas** únicos
- **Tempo de resposta** das buscas
- **Score de similaridade** para cada resultado

## 🔒 Segurança

- **Rate limiting**: 10 requests/minuto por IP
- **Input sanitization** para prevenir XSS
- **CSP headers** rigorosos
- **CORS** configurado apenas para origens específicas
- **SQL injection** prevenido com SQLAlchemy ORM

---

**🎵 Desenvolvido com ❤️ para descoberta musical inteligente!**
