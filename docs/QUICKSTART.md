# ⚡ Quick Start

Choose your path:

---

## 🧪 Option A: Testing in Google Colab

**Goal:** Find the best model and prompt

### Step 1: Upload Notebook
1. Go to [Google Colab](https://colab.research.google.com)
2. Upload `COLAB_TESTING.ipynb` from this repo
3. Open it

### Step 2: Setup
Run the "Setup" section (installs packages, clones repo)

### Step 3: Test Models
Run "Scenario 1: Test Different Models"
- Tests multiple LLM models
- Measures quality & speed
- Shows best model → Update production config with this

### Step 4: Test Prompts
Run "Scenario 2: Test Different Prompts"
- Tests multiple prompts with your chosen model
- Measures response quality
- Shows best prompt → Update production config with this

### Step 5: Push Results
```bash
git add metrics/
git commit -m "Test results: best model and prompt"
git push origin development
```

---

## 🚀 Option B: Running Production Locally

**Goal:** Deploy the production app with locked settings

### Step 1: Environment
```bash
# Copy template and fill in your settings
cp .env.production.example .env.production

# Edit .env.production with your values
# Most important:
#   PROD_LLM_PROVIDER=unsloth
#   PROD_MODEL_NAME=meta-llama/Llama-2-7b-hf  (from testing)
#   DATABASE_URL=your_db
```

### Step 2: Install
```bash
cd Fabricators_ai
pip install -r requirements.txt
```

### Step 3: Run
```bash
# Production mode
export ENVIRONMENT=production
python app.py

# App runs on http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Step 4: Deploy
When ready for production:
```bash
# Using gunicorn (recommended)
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Or Docker
docker build -t fabricators-ai .
docker run -p 8000:8000 fabricators-ai
```

---

## 🔄 Workflow: Test → Update → Deploy

### After Testing in Colab:

1. **Review metrics** in `metrics/model_comparison.json`
   - Which model had best quality score?
   - Which model was fast enough?

2. **Update config**:
   ```bash
   # Edit config/production.py
   PROD_MODEL_NAME = "your_best_model"
   ```

3. **Update prompt**:
   ```bash
   # Edit instructions/fabrication_assistant.md
   # Replace with best prompt version from testing
   ```

4. **Commit changes**:
   ```bash
   git add config/production.py instructions/fabrication_assistant.md
   git commit -m "Production: best model + prompt from testing"
   git push
   ```

5. **Deploy**:
   ```bash
   git pull
   python app.py  # Runs with new settings
   ```

---

## 📊 File Structure

### For Production
- `app.py` - Main application
- `config/production.py` - Production settings (LOCKED)
- `instructions/fabrication_assistant.md` - Best prompt (LOCKED)
- `.env.production` - Your deployment secrets

### For Testing
- `COLAB_TESTING.ipynb` - Colab notebook
- `development/colab_launcher.py` - Testing launcher
- `development/model_testing.py` - Testing framework
- `metrics/` - Test results

---

## 🎯 What Each Does

| Script | Purpose | Run Where |
|--------|---------|-----------|
| `COLAB_TESTING.ipynb` | Interactive testing notebook | Google Colab |
| `development/colab_launcher.py` | CLI testing menu | Colab terminal or local |
| `app.py` | Production app | Local (development) or Server (production) |

---

## ✅ Checklist

### Before First Production Deploy
- [ ] Ran all test scenarios in Colab
- [ ] Got test results in `metrics/`
- [ ] Updated `config/production.py` with best model
- [ ] Updated `instructions/fabrication_assistant.md` with best prompt
- [ ] `.env.production` is filled in
- [ ] Committed all changes
- [ ] Verified `app.py` starts: `python app.py`

### Before Each Production Deployment
- [ ] Pulled latest `main` branch
- [ ] Ran tests locally: `pytest tests/`
- [ ] App starts without errors
- [ ] Environment variables are set
- [ ] Database is available

---

## 🆘 Common Issues

### "Can't find Colab notebook"
→ It's at `COLAB_TESTING.ipynb` - download and upload to Colab

### "App won't start in production"
→ Check: `.env.production` exists, all variables set, database is running

### "Old model still loading"
→ Check: `config/production.py` is updated, app was restarted

### "Metrics not saving in Colab"
→ Check: `metrics/` folder exists, you have write permissions

---

## 🚀 Next Steps

**New to the project?**
1. Read `ARCHITECTURE.md` (detailed guide)
2. Try testing in Colab (`COLAB_TESTING.ipynb`)
3. Review results in `metrics/`

**Ready to deploy?**
1. Run all test scenarios
2. Update production config with best settings
3. Follow "Workflow" section above
4. Deploy with confidence! 🎉

---

**Questions?** Check `ARCHITECTURE.md` for detailed explanations.
