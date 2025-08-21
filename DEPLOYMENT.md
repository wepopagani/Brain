# 🚀 brAIn - Deployment Guide

## 📋 Prerequisites

1. **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **GitHub Account**: For code hosting
3. **Netlify Account**: For frontend hosting
4. **Backend Hosting**: Railway, Render, or Heroku

## 🎯 Quick Deploy Steps

### 1. Setup OpenAI API
```bash
# Get your API key from OpenAI
# It should look like: sk-...
```

### 2. Frontend (Netlify)
1. Push code to GitHub
2. Connect Netlify to your GitHub repo
3. Build settings:
   - Build command: `npm run build`
   - Publish directory: `build`
4. Environment variables in Netlify:
   - `REACT_APP_API_URL`: Your backend URL

### 3. Backend (Railway/Render)
1. Deploy the `/backend` folder
2. Set environment variable:
   - `OPENAI_API_KEY`: Your OpenAI key
3. Install requirements: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

## 🔧 Local Development vs Production

### Local (with Ollama)
- Keeps using your local Ollama + DeepSeek
- Fast and free
- No API costs

### Production (with OpenAI)
- Uses OpenAI API when `OPENAI_API_KEY` is set
- Works on any hosting platform
- Small API cost (~$0.002 per search)

## 📱 Demo Mode
For colleagues to test:
1. Frontend works immediately on Netlify
2. Backend can be deployed in 5 minutes
3. Set OpenAI key and it's ready!

## 💡 Architecture
```
Frontend (Netlify) → Backend (Railway) → OpenAI API
                                    ↓
                               CSV Data (990 startups)
```

The AI analysis works identically to your local setup, just uses OpenAI instead of Ollama.
