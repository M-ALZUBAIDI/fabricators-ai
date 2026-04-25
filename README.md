# 🚀 Fabricators AI - Production

AI-powered fabrication platform with LLM integration.

---

## ⚡ Quick Start

### Setup
```bash
# Create production environment file
cp .env.production.example .env.production

# Edit with your settings
nano .env.production

# Install dependencies
pip install -r requirements.txt
```

### Run
```bash
export ENVIRONMENT=production
python app.py

# App: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

### Deploy
```bash
# Using gunicorn
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# See docs/PRODUCTION_DEPLOYMENT.md for full guide
```

---

## 📁 Structure

```
├── app.py                  # Production app
├── config/                 # Configuration
├── requirements.txt        # Dependencies
├── .env.production         # Your settings (create from .env.production.example)
├── api/                    # API routes
├── services/               # Business logic
├── models/                 # LLM providers
├── utils/                  # Utilities
└── docs/                   # Documentation & testing
```

---

## 🔧 Configuration

Edit `.env.production`:

```env
ENVIRONMENT=production
PROD_LLM_PROVIDER=unsloth
PROD_MODEL_NAME=meta-llama/Llama-2-7b-hf
DATABASE_URL=postgresql://user:pass@localhost/db
CORS_ORIGINS=https://yourdomain.com
```

---

## 📚 Documentation

All guides are in `/docs/`:

- **QUICKSTART.md** - Quick reference
- **ARCHITECTURE.md** - How it works  
- **PRODUCTION_DEPLOYMENT.md** - Server deployment
- **colab-testing/** - Testing & development guides

---

## 🧪 Testing

For testing models/prompts: See `docs/colab-testing/`

Upload `COLAB_TESTING.ipynb` to Google Colab to:
1. Test different models
2. Test different prompts
3. Compare results
4. Update production with best settings

---

## 🔄 Workflow

```
1. Test in Colab → Review Results → 2. Update Config → 3. Deploy
```

**Detailed guides in `/docs/`**

---

## 💻 API Endpoints

- `POST /api/chat` - Send question
- `GET /api/chat/{session_id}` - Get history
- `POST /api/report` - Generate report
- `GET /health` - Health check
- `GET /docs` - API documentation

---

## 🆘 Support

See detailed guides in `/docs/` folder for:
- Troubleshooting
- Server deployment
- Configuration
- Testing & development
