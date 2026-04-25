# 📚 Documentation & Testing

This folder contains all guides for testing, development, and deployment.

---

## 📖 Guides

### For Production Deployment
- **PRODUCTION_DEPLOYMENT.md** - Server deployment (Nginx, Docker, systemd, etc.)

### For Understanding the Architecture  
- **ARCHITECTURE.md** - How production and testing are separated
- **QUICKSTART.md** - 5-minute quick reference

### For Testing & Development
- **colab-testing/** - All testing files
  - `COLAB_TESTING.ipynb` - Interactive Google Colab notebook
  - `colab_launcher.py` - CLI testing script
  - `model_testing.py` - Testing framework
  - `prompt_manager.py` - Prompt version management
  - `dev_testing.py` - Additional test scenarios

---

## 🚀 Getting Started

**Choose your path:**

### Path 1: Run Production Locally
```bash
cd ..
cp .env.production.example .env.production
# Edit .env.production
python app.py
```

### Path 2: Test in Google Colab
```
1. Download: colab-testing/COLAB_TESTING.ipynb
2. Upload to Google Colab
3. Run setup section
4. Test scenarios 1 & 2
5. Review results
6. Update production config
```

### Path 3: Deploy to Server
See: `PRODUCTION_DEPLOYMENT.md`

---

## 🧪 Testing Workflow

**Quick overview:**

1. **Test models** - Compare different LLMs
2. **Test prompts** - Find best prompt version
3. **Review results** - Check metrics
4. **Update config** - Lock best settings
5. **Deploy** - Run production app

See `QUICKSTART.md` for detailed steps.

---

## 📂 File Structure

```
docs/
├── README.md                           # This file
├── ARCHITECTURE.md                     # System architecture
├── QUICKSTART.md                       # Quick reference
├── PRODUCTION_DEPLOYMENT.md            # Server deployment
└── colab-testing/                      # Testing code
    ├── COLAB_TESTING.ipynb            # Colab notebook
    ├── colab_launcher.py              # Testing CLI
    ├── model_testing.py               # Test framework
    ├── prompt_manager.py              # Prompt versions
    └── dev_testing.py                 # Dev tests
```

---

## ✅ Checklist

### Before First Production Deploy
- [ ] Read: `QUICKSTART.md`
- [ ] Review: `ARCHITECTURE.md`
- [ ] Set up: `.env.production` in root
- [ ] Test locally: `python app.py`

### Before Server Deployment
- [ ] Test in Colab: `colab-testing/COLAB_TESTING.ipynb`
- [ ] Review: `PRODUCTION_DEPLOYMENT.md`
- [ ] Choose deployment option (Gunicorn/Docker/Systemd)
- [ ] Set up environment variables

---

## 💡 Tips

- **Testing?** Start with `colab-testing/COLAB_TESTING.ipynb`
- **Deploying?** Follow `PRODUCTION_DEPLOYMENT.md`
- **Confused?** Read `QUICKSTART.md` first
- **Need details?** Check `ARCHITECTURE.md`

---

## 🆘 Quick Help

| Problem | Solution |
|---------|----------|
| "How do I test models?" | See `colab-testing/` |
| "How do I deploy?" | See `PRODUCTION_DEPLOYMENT.md` |
| "How does it work?" | See `ARCHITECTURE.md` |
| "Quick overview?" | See `QUICKSTART.md` |

---

**Start here:** `QUICKSTART.md` → `ARCHITECTURE.md` → Get testing!
