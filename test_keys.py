#!/usr/bin/env python3
"""
Test script to verify API keys are working.
Run this on Replit: python test_keys.py
"""
import os

# Test Groq keys
print("=" * 50)
print("Testing API Keys")
print("=" * 50)

groq_key = os.getenv("GROQ_API_KEY", "")
gemini_key = os.getenv("GEMINI_API_KEY", "")
openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

print(f"\nGROQ_API_KEY: {'SET' if groq_key else 'NOT SET'}")
print(f"  Value preview: {groq_key[:20]}..." if groq_key else "")

print(f"\nGEMINI_API_KEY: {'SET' if gemini_key else 'NOT SET'}")
print(f"  Value preview: {gemini_key[:20]}..." if gemini_key else "")

print(f"\nOPENROUTER_API_KEY: {'SET' if openrouter_key else 'NOT SET'}")
print(f"  Value preview: {openrouter_key[:20]}..." if openrouter_key else "")

# Test comma-separated format
groq_keys = os.getenv("GROQ_API_KEYS", "")
print(f"\nGROQ_API_KEYS: {'SET' if groq_keys else 'NOT SET'}")
if groq_keys:
    key_list = [k.strip() for k in groq_keys.split(",") if k.strip()]
    print(f"  Keys found: {len(key_list)}")
    for i, k in enumerate(key_list[:3]):
        print(f"    Key {i+1}: {k[:20]}...")

gemini_keys = os.getenv("GEMINI_API_KEYS", "")
print(f"\nGEMINI_API_KEYS: {'SET' if gemini_keys else 'NOT SET'}")
if gemini_keys:
    key_list = [k.strip() for k in gemini_keys.split(",") if k.strip()]
    print(f"  Keys found: {len(key_list)}")
    for i, k in enumerate(key_list[:3]):
        print(f"    Key {i+1}: {k[:20]}...")

# Test actual API call
print("\n" + "=" * 50)
print("Testing Groq API Call")
print("=" * 50)

try:
    from groq import Groq
    
    # Get first Groq key
    if groq_keys:
        first_key = [k.strip() for k in groq_keys.split(",") if k.strip()][0]
    elif groq_key:
        first_key = groq_key
    else:
        print("No Groq keys found!")
        first_key = None
    
    if first_key:
        print(f"Testing with key: {first_key[:15]}...")
        client = Groq(api_key=first_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        
        print("✅ Groq API works!")
        print(f"Response: {response.choices[0].message.content}")
    else:
        print("❌ No Groq API key available")
        
except Exception as e:
    print(f"❌ Groq API failed: {e}")

# Test Gemini
print("\n" + "=" * 50)
print("Testing Gemini API Call")
print("=" * 50)

try:
    import google.generativeai as genai
    
    if gemini_keys:
        first_key = [k.strip() for k in gemini_keys.split(",") if k.strip()][0]
    elif gemini_key:
        first_key = gemini_key
    else:
        first_key = None
    
    if first_key:
        print(f"Testing with key: {first_key[:15]}...")
        genai.configure(api_key=first_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hi")
        
        print("✅ Gemini API works!")
        print(f"Response: {response.text[:100]}...")
    else:
        print("❌ No Gemini API key available")
        
except Exception as e:
    print(f"❌ Gemini API failed: {e}")

# Test OpenRouter
print("\n" + "=" * 50)
print("Testing OpenRouter API Call")
print("=" * 50)

try:
    from openai import OpenAI
    
    openrouter_keys = os.getenv("OPENROUTER_API_KEYS", "")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if openrouter_keys:
        first_key = [k.strip() for k in openrouter_keys.split(",") if k.strip()][0]
    elif openrouter_key:
        first_key = openrouter_key
    else:
        first_key = None
    
    if first_key:
        print(f"Testing with key: {first_key[:15]}...")
        client = OpenAI(
            api_key=first_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        
        print("✅ OpenRouter API works!")
        print(f"Response: {response.choices[0].message.content}")
    else:
        print("❌ No OpenRouter API key available")
        
except Exception as e:
    print(f"❌ OpenRouter API failed: {e}")

print("\n" + "=" * 50)