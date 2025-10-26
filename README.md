# PlanPal Backend (Flask)

## Overview
Simple Flask backend providing:
- User registration (token-based)
- Group creation
- Poll creation & voting
- Chat endpoint that uses OpenAI -> HuggingFace -> local fallback

## Setup
1. Create a virtualenv and activate it.
2. Install requirements:
   pip install -r requirements.txt
3. Copy `.env.sample` to `.env` and fill keys (OPENAI_API_KEY, HF_API_KEY, etc).
4. Run:
   python app.py

The backend runs on http://localhost:5000
