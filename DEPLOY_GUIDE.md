# 🚀 Deploy Guide - Digital Ocean

## 📋 **Pré-requisitos**

### 1. **Conta Digital Ocean**
- Acesso ao [Digital Ocean](https://cloud.digitalocean.com)
- Billing configurado
- GitHub account conectado

### 2. **Repositório GitHub**
- Push do código para `MikaelSantilio/music_seeker`
- Branch `master` atualizada

## 🎯 **Configuração do Deploy**

### **Custos Estimados:**
- **App Platform Basic**: $5/mês
- **Database Basic**: $15/mês  
- **Total**: $20/mês

### **Recursos:**
- 1GB RAM, 1 vCPU
- 10GB storage
- PostgreSQL 15 + pgvector
- SSL automático

## 🔧 **Passos para Deploy**

### 1. **Criar Database**

```bash
# No Digital Ocean Console:
1. Databases > Create Database Cluster
2. PostgreSQL version 15
3. Basic plan: db-s-1vcpu-1gb ($15/mês)
4. Region: New York (NYC1)
5. Database name: musicseeker
6. User: musicseeker_user
```

### 2. **Configurar pgvector**

```sql
-- Conectar ao database e executar:
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar instalação:
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 3. **Deploy da Aplicação**

```bash
# No Digital Ocean Console:
1. Apps > Create App
2. GitHub: MikaelSantilio/music_seeker
3. Branch: master
4. Auto-deploy: ✅ Enabled
5. Plan: Basic ($5/mês)
6. Region: New York (NYC1)
```

### 4. **Configurar Variáveis de Ambiente**

```bash
# Na seção Environment Variables:
DATABASE_URL=postgresql://user:pass@host:port/db    # Auto-preenchida
OPENAI_API_KEY=sk-xxx...                           # Sua chave da OpenAI
ENVIRONMENT=production
DEBUG=false
APP_VERSION=2.0.0
```

### 5. **Configurar Domínio (Opcional)**

```bash
# Em Settings > Domains:
1. Add Domain: musicseeker.com
2. Configure DNS: CNAME -> your-app.ondigitalocean.app
3. SSL: Auto-enabled
```

## 📊 **Pós-Deploy**

### **1. Verificar Health Check**
```bash
curl https://your-app.ondigitalocean.app/health
```

### **2. Carregar Dados**
```bash
# Executar localmente (conectado ao DB de produção):
python scripts/load_data.py
python scripts/generate_embeddings.py
```

### **3. Testar API**
```bash
# Testar endpoints principais:
curl https://your-app.ondigitalocean.app/api/v1/stats
curl -X POST https://your-app.ondigitalocean.app/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "love and romance", "limit": 5}'
```

## 🛡️ **Segurança em Produção**

### **Configurações Automáticas:**
- ✅ **HTTPS/SSL** automático
- ✅ **Rate Limiting** (10 req/min)
- ✅ **CORS** restrito
- ✅ **Headers de segurança**
- ✅ **Validação de input**

### **Monitoramento:**
- ✅ **Health checks** (30s interval)
- ✅ **CPU/Memory alerts** (80% threshold)
- ✅ **Error tracking** via logs

## 🔄 **CI/CD Automático**

### **Auto-deploy configurado:**
```bash
git push origin master  # Deploy automático!
```

### **Logs em tempo real:**
```bash
# No Digital Ocean Console:
Apps > Your App > Runtime Logs
```

## 📈 **Métricas e Monitoramento**

### **Dashboards Disponíveis:**
- CPU, Memory, Network usage
- Request rates e latência
- Error rates
- Database connections

### **Alertas Configurados:**
- CPU > 80%
- Memory > 80%
- Error rate > 5%

## 🚀 **URLs de Produção**

```bash
# Principais endpoints:
🏠 Home: https://your-app.ondigitalocean.app/
📖 Docs: https://your-app.ondigitalocean.app/docs
🔍 Search: https://your-app.ondigitalocean.app/search
💻 Health: https://your-app.ondigitalocean.app/health
```

## 🛠️ **Troubleshooting**

### **Build Failures:**
```bash
# Verificar logs de build:
Apps > Your App > Build Logs

# Problemas comuns:
- Python version (usar 3.11.9)
- Missing dependencies
- Database connection
```

### **Runtime Errors:**
```bash
# Verificar runtime logs:
Apps > Your App > Runtime Logs

# Problemas comuns:
- Environment variables
- Database connectivity
- OpenAI API key
```

---

**🎵 Ready for production! Sua API semântica está no ar! 🚀**
