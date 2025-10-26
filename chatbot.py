# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
HF_KEY = os.getenv('HF_API_KEY')

def _openai_reply(message, mood):
    try:
        import openai
        openai.api_key = OPENAI_KEY
        prompt = f'You are PlanPal Bot. Mood: {mood}. User: {message}\nReply with a friendly emoji-rich suggestion and 2 short options.'
        resp = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[{'role':'user','content':prompt}], max_tokens=150)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return None

def _hf_reply(message, mood):
    try:
        import requests
        if not HF_KEY:
            return None
        headers = {'Authorization': f'Bearer {HF_KEY}'}
        api = 'https://api-inference.huggingface.co/models/gpt2'  # lightweight fallback
        payload = {'inputs': f'PlanPal Bot. Mood: {mood}. {message}'}
        r = requests.post(api, headers=headers, json=payload, timeout=10)
        if r.ok:
            out = r.json()
            if isinstance(out, list) and len(out)>0:
                return out[0].get('generated_text','').strip()
            if isinstance(out, dict) and 'error' in out:
                return None
        return None
    except Exception:
        return None

def _local_reply(message, mood):
    # Very small deterministic fallback so the app still works offline.
    mood_map = {
        'chill': 'Let\'s do something chill 😎 — movie night or cozy café ☕️',
        'adventurous': 'Adventure time! 🚴‍♂️ How about a hike or cycling trip? 🏞️',
        'foodie': 'Foodie mood 🍕🍣 — try a popular local café or street-food crawl!'
    }
    base = mood_map.get((mood or '').lower(), 'Hey! How about a movie night or a café meetup?')
    return base + ' (PlanPal Bot fallback)'

def get_chatbot_response(message, mood=None):
    # prefer OpenAI if key present
    if OPENAI_KEY:
        r = _openai_reply(message, mood)
        if r:
            return r
    if HF_KEY:
        r = _hf_reply(message, mood)
        if r:
            return r
    return _local_reply(message, mood)
