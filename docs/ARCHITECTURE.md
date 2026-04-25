# 🏗️ Production vs Testing Architecture

This guide explains the clean separation between **Production** code (local) and **Testing** code (Colab).

---

## 📁 Directory Structure

```
Fabricators_ai/
├── app.py                          # 🚀 PRODUCTION: Main app (local only)
├── config/
│   ├── production.py               # 🔒 PRODUCTION: Locked settings
│   ├── development.py              # 📊 TESTING: Dev settings
│   └── settings.py                 # Shared base settings
├── instructions/
│   └── fabrication_assistant.md    # 🔒 PRODUCTION: Best prompt (locked here)
├── development/
│   ├── colab_launcher.py           # 📊 Entry point for testing
│   ├── model_testing.py            # 📊 Testing framework
│   ├── prompt_manager.py           # 📊 Prompt version management
│   └── dev_testing.py              # 📊 Additional test scenarios
├── metrics/                         # 📊 Test results (not in production)
├── services/                        # ✅ Shared: Chat, Reports, Analysis
├── models/                          # ✅ Shared: LLM Providers
└── api/                            # ✅ Shared: API Routes
```

### Legend
- 🚀 **PRODUCTION**: Only in local production setup
- 📊 **TESTING**: Only in Google Colab
- 🔒 **LOCKED**: Updated after testing, then locked
- ✅ **SHARED**: Used by both production and testing

---

## 🔄 The Workflow

### Phase 1: Development/Testing (Google Colab)

```
Upload Colab Notebook (COLAB_TESTING.ipynb)
         ↓
Test Models (Scenario 1)
         ↓
Results → metrics/model_comparison.json
         ↓
Choose Best Model ✓
         ↓
Test Prompts (Scenario 2)
         ↓
Results → metrics/prompt_comparison.json
         ↓
Choose Best Prompt ✓
```

### Phase 2: Update Production (Local VS Code)

```
Review Test Results
         ↓
Update config/production.py
  (PROD_MODEL_NAME = "best_model")
         ↓
Update instructions/fabrication_assistant.md
  (Replace with best prompt)
         ↓
git add & commit
         ↓
git push to main
```

### Phase 3: Deploy (Production)

```
Pull latest main
         ↓
Run app.py
         ↓
app.py reads config/production.py
         ↓
Loads best model + best prompt
         ↓
Service runs with locked settings ✓
```

---

## 📊 Testing in Google Colab

### Setup (First Time)

1. **Open** [Google Colab](https://colab.research.google.com)
2. **Upload** `COLAB_TESTING.ipynb` 
3. **Run** Setup section (clones repo, installs deps)
4. **Test** one scenario

### Run Tests

```python
# Scenario 1: Find best model
await scenario_1_test_models()

# Results saved to: metrics/model_comparison.json
# 🏆 Best model: meta-llama/Llama-2-7b-hf
```

```python
# Scenario 2: Find best prompt
await scenario_2_test_prompts()

# Results saved to: metrics/prompt_comparison.json
# 🏆 Best prompt: v2_detailed
```

### Save & Push Results

```bash
# In Colab terminal
git add metrics/
git commit -m "Test results: models and prompts"
git push origin development
```

---

## 🚀 Production in VS Code

### Setup (First Time)

```bash
cd Fabricators_ai
export ENVIRONMENT=production
python app.py
```

### Configuration

1. **Create** `.env.production` (copy from `.env.production.example`)
2. **Fill in** your settings:
   ```
   PROD_LLM_PROVIDER=unsloth
   PROD_MODEL_NAME=meta-llama/Llama-2-7b-hf    # From testing
   DATABASE_URL=postgresql://...
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Verify** `config/production.py` reads from `.env.production`

### Deploy

```bash
# Set production environment
export ENVIRONMENT=production

# Run app (reads config/production.py)
python app.py

# Or with gunicorn for production
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Update Production Config

After successful testing in Colab:

1. **Open** `config/production.py`
2. **Update** model name:
   ```python
   PROD_MODEL_NAME = "meta-llama/Llama-2-13b-hf"  # Your best model
   ```

3. **Open** `instructions/fabrication_assistant.md`
4. **Replace** with best prompt version

5. **Commit & Push**:
   ```bash
   git add config/production.py instructions/fabrication_assistant.md
   git commit -m "Update production: best model + prompt from testing"
   git push origin main
   ```

---

## 🔑 Key Principles

### ✅ Production Settings Are Locked

- `config/production.py` is the source of truth
- Only update after successful testing
- Never edit production settings for quick fixes
- Always deploy from main branch

### ✅ Testing is Isolated

- All testing happens in Colab (or `development/` locally)
- Test results go to `metrics/` folder
- Doesn't affect production
- Can try anything without risk

### ✅ Single Source of Truth

- One prompt: `instructions/fabrication_assistant.md`
- One model config: `config/production.py`
- One app: `app.py`
- Results in consistent behavior everywhere

### ✅ Shared Code

- `services/`, `models/`, `api/` are used by both testing and production
- Keep them production-quality
- Don't add testing code to shared modules
- Changes here affect both environments

---

## 🔍 Debugging

### "Model not loading in Colab"
- Check `COLAB_TESTING.ipynb` setup section
- Verify Unsloth is installed: `pip list | grep unsloth`
- Check GPU available: `!nvidia-smi`

### "Production app won't start"
- Check `.env.production` exists
- Verify `PROD_LLM_PROVIDER` is valid
- Check logs: `tail -f log.txt`

### "Getting old model in production"
- Verify `config/production.py` is updated
- Check git: `git log config/production.py`
- Restart app after updating config

---

## 📝 Checklist: From Testing to Production

- [ ] Run all 3 test scenarios in Colab
- [ ] Save results to `metrics/`
- [ ] Push results to GitHub
- [ ] Identify best model + prompt
- [ ] Update `config/production.py` with model name
- [ ] Update `instructions/fabrication_assistant.md` with prompt
- [ ] Run `git diff` to review changes
- [ ] Commit with clear message
- [ ] Push to main
- [ ] Deploy to production
- [ ] Verify production works with new settings
- [ ] Monitor logs for issues

---

## 🎯 Tips & Tricks

### Testing Multiple Models Fast
```bash
# Use MockProvider for instant testing
python development/colab_launcher.py
# Choose option 4
```

### Keep Old Test Results
```bash
# Don't delete metrics/ - they show your history
# Rename: mv metrics/model_comparison.json metrics/model_comparison_20260425.json
git add metrics/
git commit -m "Archive test results"
```

### Batch Testing
Create a Colab script that runs multiple scenarios:
```python
await scenario_1_test_models()
await scenario_2_test_prompts()
await scenario_3_complete_workflow()
print("✓ All tests complete!")
```

### Integration Test Before Deploy
```bash
# In local VS Code, test with production config
export ENVIRONMENT=production
python -m pytest tests/
python app.py  # Check it starts
```

---

## 📚 Files to Know

| File | Purpose | Edit? |
|------|---------|-------|
| `app.py` | Production app | ❌ Only if adding endpoints |
| `config/production.py` | Production settings | ✅ After testing |
| `instructions/fabrication_assistant.md` | Production prompt | ✅ After testing |
| `development/colab_launcher.py` | Testing entry point | ✅ Add new test scenarios |
| `metrics/` | Test results | 📊 Reference only |
| `COLAB_TESTING.ipynb` | Colab notebook | ✅ Customize test cases |

---

## 🆘 Getting Help

- **Colab issues?** Check `COLAB_TESTING.ipynb` setup section
- **Production issues?** Check `.env.production` and logs
- **Testing framework?** See `development/model_testing.py` docstrings
- **API questions?** See `api/routes.py`

---

**Remember:** Test aggressively in Colab, deploy carefully to production! 🚀
