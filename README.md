# brAIn - AI-Powered Strategic Intelligence Platform

Un agente AI che genera report strategici su trend, competitor e startup, usando solo dati pubblici e visualizzabili in modo interattivo.

## 🧠 Caratteristiche Principali

- **Visualizzazione Cervello Interattiva**: Network neurale animato con D3.js
- **Analisi Trend Real-time**: Identificazione automatica di trend di mercato
- **Report AI-Generated**: Sintesi strategiche generate con GPT
- **Dashboard Interattiva**: Esplorazione visual dei dati
- **Design Minimal**: UI/UX moderna e pulita

## 🚀 Quick Start

### 🖥️ Local Development (con Ollama)

**Prerequisiti:**
- Node.js 16.x o superiore
- Python 3.9+
- Ollama installato

```bash
# Clone repository
git clone https://github.com/wepopagani/BrAIn.git
cd BrAIn

# Frontend
npm install
npm start

# Backend (in altra terminal)
cd backend
pip install -r requirements.txt
python app.py

# Ollama (in altra terminal)
ollama serve
ollama pull deepseek-r1:1.5b
```

L'applicazione sarà disponibile su `http://localhost:3000`

### 🌐 Production Deployment

**Per demo pubbliche:**

1. **Frontend su Netlify**: Deploy automatico da GitHub
2. **Backend su Railway/Render**: Con OpenAI API key
3. **Vedi**: [DEPLOYMENT.md](./DEPLOYMENT.md) per istruzioni complete

**Environment Variables:**
```bash
OPENAI_API_KEY=your_key_here  # Per produzione
REACT_APP_API_URL=your_backend_url  # URL backend
```

## 🏗️ Architettura

### Frontend
- **React 18** con TypeScript
- **D3.js** per visualizzazioni interattive
- **Tailwind CSS** per styling
- **Framer Motion** per animazioni
- **Lucide React** per icone

### Struttura del Progetto

```
src/
├── components/
│   ├── BrainVisualization.tsx  # Componente principale del cervello
│   ├── HomePage.tsx            # Homepage con search
│   └── Dashboard.tsx           # Dashboard con analisi
├── types/
│   └── index.ts               # Definizioni TypeScript
├── App.tsx                    # Componente principale
└── index.tsx                  # Entry point
```

### Componenti Chiave

#### BrainVisualization
Crea una rete neurale interattiva con:
- Nodi centrali per categorie principali
- Nodi periferici per connessioni
- Animazioni fluide e hover effects
- Click handling per navigazione

#### HomePage
- Visualizzazione del cervello a schermo intero
- Barra di ricerca centrale
- Use cases cards
- Navigazione verso dashboard

#### Dashboard
- Visualizzazione dual-panel
- Brain visualization a sinistra
- Informazioni startup a destra
- Mock data per Electra Motors

## 🎨 Customizzazione

### Colori del Tema
```css
brain-blue: #00b4d8
brain-cyan: #90e0ef
brain-dark: #0a0a0a
brain-gray: #1a1a1a
```

### Animazioni
- Pulse lento per nodi
- Glow effects
- Smooth transitions

## 📊 Prossimi Step

1. **Backend Integration**: FastAPI per data processing
2. **AI Integration**: OpenAI GPT-4 per report generation
3. **Data Sources**: 
   - Crunchbase API
   - Dealroom data
   - EU funding databases
4. **Knowledge Graph**: Neo4j per relationships
5. **Real-time Updates**: WebSocket connections

## 🛠️ Sviluppo

### Comandi Disponibili

```bash
npm start      # Development server
npm build      # Build produzione
npm test       # Test suite
npm run dev    # Development con hot reload
```

### Environment Variables

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_OPENAI_KEY=your_openai_key
```

## 🚀 Deployment

Il progetto è configurato per deployment su:
- Vercel (raccomandato)
- Netlify
- Docker

### Docker
```bash
# Build image
docker build -t brain-ai .

# Run container
docker run -p 3000:3000 brain-ai
```

## 📈 Roadmap MVP (6 settimane)

| Settimana | Obiettivo |
|-----------|-----------|
| 1 | ✅ UI/UX Base + Brain Visualization |
| 2 | Backend API + Data normalization |
| 3 | AI Report Generation |
| 4 | Dashboard completa |
| 5 | Testing + UX improvements |
| 6 | Demo + feedback iteration |

## 🤝 Contributing

1. Fork il progetto
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**brAIn** - Trasforming strategic intelligence through AI and beautiful visualizations. 