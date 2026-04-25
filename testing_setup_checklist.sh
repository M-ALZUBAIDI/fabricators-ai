#!/bin/bash
# TESTING SETUP CHECKLIST
# Copy this and run through it step by step

echo "
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                 TESTING SETUP CHECKLIST                                   ║
║                                                                            ║
║              Start here - Follow each step in order                       ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"

echo "
STEP 1: CHECK PYTHON VERSION
═══════════════════════════════════════════════════════════════════════════
"
python --version
echo "✓ Need: Python 3.9 or higher"
echo ""

echo "
STEP 2: CHECK DISK SPACE
═══════════════════════════════════════════════════════════════════════════
"
df -h | grep -E "^/dev"
echo "✓ Need: At least 50GB free"
echo ""

echo "
STEP 3: NAVIGATE TO PROJECT
═══════════════════════════════════════════════════════════════════════════
"
echo "Run this command:"
echo "cd /Users/mohammed_alz/Desktop/Fabricators_ai"
echo ""
echo "Verify you're in the right place:"
pwd
echo ""
echo "Check files exist:"
ls -la | grep -E "(requirements.txt|app.py|development)"
echo ""

echo "
STEP 4: INSTALL DEPENDENCIES
═══════════════════════════════════════════════════════════════════════════
"
echo "Run this command (takes 5-15 minutes):"
echo "pip install -r requirements.txt"
echo ""

echo "
STEP 5: CREATE .env FILE
═══════════════════════════════════════════════════════════════════════════
"
echo "Run this command:"
echo "cp .env.example .env"
echo ""
echo "Verify .env was created:"
ls -la .env
echo ""

echo "
STEP 6: VERIFY INSTALLATION
═══════════════════════════════════════════════════════════════════════════
"
echo "Run this command:"
echo "python -c \"import torch; print('PyTorch version:', torch.__version__)\""
echo ""
echo "Run this command:"
echo "python -c \"import unsloth; print('Unsloth installed!')\""
echo ""

echo "
STEP 7: START TESTING
═══════════════════════════════════════════════════════════════════════════
"
echo "Run this command:"
echo "python development/dev_testing.py"
echo ""
echo "When prompted, choose:"
echo "  4 (Mock test first - fast verification)"
echo ""

echo "
SUCCESS CHECKLIST
═══════════════════════════════════════════════════════════════════════════
"
echo "✓ Python 3.9+ installed"
echo "✓ 50GB+ disk space available"
echo "✓ In correct directory (/Users/mohammed_alz/Desktop/Fabricators_ai)"
echo "✓ requirements.txt installed"
echo "✓ .env file created"
echo "✓ PyTorch working"
echo "✓ Unsloth installed"
echo "✓ development/dev_testing.py can be run"
echo ""

echo "
READY TO TEST!
═══════════════════════════════════════════════════════════════════════════
"
echo "Run: python development/dev_testing.py"
echo ""
echo "Choose: 4 (Mock test - verify system works)"
echo "Then: 1 (Test different models)"
echo "Then: 2 (Test different prompts)"
echo "Then: 3 (End-to-end test)"
echo ""
echo "Results will be saved to: metrics/"
echo ""
