from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import re
from typing import List, Dict, Any, Optional
import asyncio
from data_processor import startup_processor
import pandas as pd

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchQuery(BaseModel):
    query: str

class KnowledgeNode(BaseModel):
    id: str
    label: str
    type: str
    x: float
    y: float
    description: str
    connections: List[str]

class KnowledgeGraph(BaseModel):
    nodes: List[KnowledgeNode]
    connections: List[Dict[str, Any]]
    insights: List[str]
    summary: str

def query_ai(prompt: str) -> str:
    """Query AI API - supports both OpenAI and Ollama"""
    import os
    
    # Try OpenAI first (for production)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        try:
            headers = {
                'Authorization': f'Bearer {openai_key}',
                'Content-Type': 'application/json'
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenAI failed, trying Ollama: {e}")
    
    # Fallback to Ollama (for local development)
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:1.5b",
                "prompt": prompt,
                "stream": False
            },
            timeout=15
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise HTTPException(status_code=500, detail=f"AI service error: {response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query AI: {str(e)}")

def parse_knowledge_graph(llm_response: str, query: str) -> KnowledgeGraph:
    """Parse LLM response into structured knowledge graph"""
    
    # Clean the response from markdown formatting
    clean_response = llm_response
    
    # Extract key concepts using regex (Italian)
    concepts = re.findall(r'\*\*(.*?)\*\*', llm_response)
    if not concepts:
        # Fallback: extract key Italian terms and meaningful phrases
        italian_keywords = re.findall(r'\b(?:startup|cleantech|tecnologia|energia|finanziamenti|mercato|innovazione|sostenibilità|rinnovabile|idrogeno|venture|capital|ESG|green|deal|stampa|3d|modeling|stereolitografia)\b', llm_response.lower(), re.IGNORECASE)
        concepts = list(set(italian_keywords[:6]))  # Remove duplicates
    
    # Clean concepts from asterisks and extra formatting
    cleaned_concepts = []
    for concept in concepts:
        clean_concept = re.sub(r'\*+', '', concept).strip()
        if clean_concept and len(clean_concept) > 2:
            cleaned_concepts.append(clean_concept)
    
    # Add smart default concepts based on query
    if len(cleaned_concepts) < 4:
        if "3d" in query.lower() or "stampa" in query.lower():
            default_concepts = ["Stampa 3D", "Tecnologia Additiva", "Prototipazione", "Manufacturing", "Materiali Innovativi", "Design Digitale"]
        elif "cleantech" in query.lower():
            default_concepts = ["Cleantech", "Energia Rinnovabile", "Sostenibilità", "Green Tech", "Venture Capital", "ESG"]
        else:
            default_concepts = ["Startup", "Tecnologia", "Innovazione", "Mercato", "Finanziamenti", "Trend"]
        
        needed = 6 - len(cleaned_concepts)
        cleaned_concepts.extend(default_concepts[:needed])
    
    # Create nodes
    nodes = []
    for i, concept in enumerate(cleaned_concepts[:6]):  # Limit to 6 nodes
        node = KnowledgeNode(
            id=f"node_{i}",
            label=concept.strip().title(),
            type="main" if i < 3 else "secondary",
            x=300 + (i % 3) * 200,  # Position nodes in grid
            y=200 + (i // 3) * 150,
            description=f"Concetto chiave: {concept}",
            connections=[]
        )
        nodes.append(node)
    
    # Create connections between nodes
    connections = []
    for i, node in enumerate(nodes):
        for j, other_node in enumerate(nodes):
            if i != j and abs(i - j) <= 2:  # Connect nearby nodes
                connections.append({
                    "source": node.id,
                    "target": other_node.id,
                    "strength": 0.7
                })
                node.connections.append(other_node.id)
    
    # Extract and clean insights (Italian-aware)
    insights = []
    
    # Split by bullet points first, then by sentences
    bullet_sections = re.split(r'\n\s*[\*•-]\s*', llm_response)
    
    for section in bullet_sections:
        # Clean each section from markdown formatting
        clean_section = re.sub(r'\*+', '', section).strip()
        clean_section = re.sub(r'\n+', ' ', clean_section).strip()
        
        # Only include substantial insights
        if (len(clean_section) > 40 and len(clean_section) < 200 and 
            any(word in clean_section.lower() for word in 
               ['startup', 'tecnologia', 'mercato', 'finanziamenti', 'energia', 'innovazione', 'sostenibile', '3d', 'stampa', 'modeling'])):
            
            # Ensure proper sentence ending
            if not clean_section.endswith('.'):
                clean_section += '.'
            insights.append(clean_section)
            
            if len(insights) >= 5:  # Limit to 5 insights
                break
    
    # If no good insights found, extract from sentences
    if len(insights) < 3:
        sentences = llm_response.split('.')
        for sentence in sentences:
            clean_sentence = re.sub(r'\*+', '', sentence).strip()
            clean_sentence = re.sub(r'\n+', ' ', clean_sentence).strip()
            
            if (len(clean_sentence) > 40 and len(clean_sentence) < 150 and 
                any(word in clean_sentence.lower() for word in 
                   ['startup', 'tecnologia', 'mercato', 'settore', 'innovazione'])):
                
                if not clean_sentence.endswith('.'):
                    clean_sentence += '.'
                insights.append(clean_sentence)
                
                if len(insights) >= 5:
                    break
    
    # Create clean summary
    summary_lines = []
    for line in llm_response.split('\n')[:4]:
        clean_line = re.sub(r'\*+', '', line).strip()
        if len(clean_line) > 30 and not clean_line.startswith('#'):
            summary_lines.append(clean_line)
    
    summary = ' '.join(summary_lines) if summary_lines else f"Analisi AI del settore richiesto: {query}"
    
    # Final cleanup of summary
    summary = re.sub(r'\*+', '', summary).strip()
    summary = re.sub(r'\n+', ' ', summary).strip()
    
    return KnowledgeGraph(
        nodes=nodes,
        connections=connections,
        insights=insights,
        summary=summary
    )

@app.post("/api/search")
async def search_and_analyze(query: SearchQuery):
    """Process search query and return knowledge graph"""
    
    # Construct dynamic prompt for Ollama in Italian - works for ANY sector
    prompt = f"""
    Analizza questa richiesta su startup, tecnologia e business: "{query.query}"
    
    Fornisci un'analisi comprensiva che includa:
    1. **Concetti chiave** ed entità principali (marca con **)
    2. **Trend di mercato** attuali e emergenti
    3. **Tecnologie** innovative del settore
    4. **Opportunità di business** e modelli
    5. **Panorama dei finanziamenti** e investimenti
    6. **Considerazioni geografiche** e mercati principali
    7. **Player chiave** e startup innovative
    8. **Sfide** e barriere del settore
    
    Adatta l'analisi al settore specifico richiesto. Esempi:
    - **Fintech**: pagamenti, DeFi, RegTech, InsurTech, lending, crypto
    - **Healthtech**: diagnostica AI, telemedicina, biotech, farmaceutica digitale
    - **Mobility**: veicoli elettrici, mobilità condivisa, autonomous driving, logistica
    - **Cleantech**: energie rinnovabili, storage, efficienza energetica, carbon capture
    - **AI/ML**: computer vision, NLP, robotica, edge computing, quantum
    - **Edtech**: e-learning, VR/AR education, skill assessment, corporate training
    - **Foodtech**: agricoltura digitale, alternative proteins, food delivery, sostenibilità
    - **Proptech**: smart buildings, real estate digitale, property management
    - **Gaming**: esports, metaverso, Web3 gaming, mobile gaming
    - **Fashion**: moda sostenibile, e-commerce fashion, manufacturing digitale
    
    Concentrati su insights azionabili, pattern emergenti e dati specifici del settore.
    Risposta massimo 500 parole in italiano.
    """
    
    try:
        # Query AI (OpenAI or Ollama)
        llm_response = query_ai(prompt)
        
        # Parse into knowledge graph
        knowledge_graph = parse_knowledge_graph(llm_response, query.query)
        
        return {
            "status": "success",
            "query": query.query,
            "knowledge_graph": knowledge_graph.model_dump(),
            "raw_response": llm_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test AI connection
        test_response = query_ai("Say 'OK' if you're working")
        return {
            "status": "healthy",
            "ollama": "connected",
            "test_response": test_response
        }
    except:
        return {
            "status": "unhealthy",
            "ollama": "disconnected"
        }

# Nuove API per i dati delle startup
@app.get("/api/startups")
async def get_startups(limit: Optional[int] = 100):
    """Ottieni lista delle startup dal CSV"""
    try:
        if not startup_processor.df is not None or startup_processor.load_csv():
            startup_processor.normalize_data()
            startups = startup_processor.get_startup_data(limit=limit)
            
            return {
                "status": "success",
                "count": len(startups),
                "total": len(startup_processor.df) if startup_processor.df is not None else 0,
                "startups": startups
            }
        else:
            return {
                "status": "no_data",
                "message": "CSV file not found. Please upload your startup data to backend/data/startup_data.csv",
                "startups": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/sectors")
async def get_sector_analytics():
    """Analisi per settore"""
    try:
        if startup_processor.df is not None or startup_processor.load_csv():
            startup_processor.normalize_data()
            analytics = startup_processor.get_sector_analytics()
            return {
                "status": "success",
                "analytics": analytics
            }
        else:
            return {"status": "no_data", "analytics": {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/funding")
async def get_funding_analytics():
    """Analisi dei finanziamenti"""
    try:
        if startup_processor.df is not None or startup_processor.load_csv():
            startup_processor.normalize_data()
            analytics = startup_processor.get_funding_analytics()
            return {
                "status": "success", 
                "analytics": analytics
            }
        else:
            return {"status": "no_data", "analytics": {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search/startups")
async def search_startups(query: SearchQuery):
    """Cerca startup specifiche"""
    try:
        if startup_processor.df is not None or startup_processor.load_csv():
            startup_processor.normalize_data()
            startups = startup_processor.search_startups(query.query)
            
            return {
                "status": "success",
                "query": query.query,
                "count": len(startups),
                "startups": startups
            }
        else:
            return {
                "status": "no_data",
                "query": query.query,
                "startups": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/startups/sector/{sector_name}")
async def get_startups_by_sector(sector_name: str, limit: Optional[int] = 100):
    """Ottieni tutte le startup di un settore specifico dal CSV (senza duplicati)"""
    try:
        import pandas as pd
        import os
        
        # Leggi direttamente il CSV
        csv_path = os.path.join(os.path.dirname(__file__), "data", "startup_data.csv")
        if not os.path.exists(csv_path):
            return {"status": "error", "message": "CSV non trovato"}
        
        # Leggi il CSV saltando le prime righe di header
        df = pd.read_csv(csv_path, skiprows=2)
        
        # Cerca la colonna Markets (settore)
        markets_col = None
        for col in df.columns:
            if 'markets' in col.lower():
                markets_col = col
                break
        
        if not markets_col:
            return {"status": "error", "message": "Colonna Markets non trovata"}
        
        # Filtra per settore Energy (case-insensitive)
        sector_startups = df[
            df[markets_col].str.lower().str.contains('energy', na=False)
        ]
        
        if len(sector_startups) == 0:
            return {
                "status": "no_matches",
                "sector": sector_name,
                "message": f"No startups found in sector: {sector_name}",
                "startups": []
            }
        
        # Deduplica per Startup ID se disponibile, altrimenti per nome
        id_col = None
        for col in df.columns:
            if 'startup id' in col.lower():
                id_col = col
                break
        
        if id_col:
            sector_startups = sector_startups.drop_duplicates(subset=[id_col], keep='first')
            print(f"DEBUG: Deduplicato per {id_col}, rimanenti: {len(sector_startups)}")
        else:
            # Fallback: deduplica per nome
            name_col = None
            for col in df.columns:
                if 'item name' in col.lower():
                    name_col = col
                    break
            
            if name_col:
                sector_startups = sector_startups.drop_duplicates(subset=[name_col], keep='first')
                print(f"DEBUG: Deduplicato per {name_col}, rimanenti: {len(sector_startups)}")
        
        # Converti in formato startup
        startups = []
        for idx, row in sector_startups.head(limit).iterrows():
            # Estrai i campi principali
            name = str(row.get('Item Name', 'Unknown')) if 'Item Name' in row else 'Unknown'
            location = str(row.get('Location', 'Europe')) if 'Location' in row else 'Europe'
            description = str(row.get('Description', 'Startup innovativa')) if 'Description' in row else 'Startup innovativa'
            
            # Parsing finanziamenti
            funding = 0.0
            if 'Total Funding' in row and pd.notna(row['Total Funding']):
                try:
                    funding = float(str(row['Total Funding']).replace('€', '').replace(',', ''))
                except:
                    funding = 0.0
            
            startup = {
                "id": str(row.get(id_col, f"startup_{idx}")) if id_col else f"startup_{idx}",
                "name": name,
                "sector": sector_name,
                "funding": funding,
                "location": location,
                "description": description,
                "year": 2023,  # Default
                "employees": 10,  # Default
                "status": "Active",
                "pipeline": "Unknown",
                "founders": "Unknown",
                "social_links": {},
                "funding_formatted": f"€{funding:,.0f}" if funding > 0 else "€0",
                "description_short": description[:200] + ('...' if len(description) > 200 else ''),
                "has_website": False,
                "has_linkedin": False
            }
            startups.append(startup)
        
        return {
            "status": "success",
            "sector": sector_name,
            "count": len(startups),
            "total_in_sector": len(sector_startups),
            "startups": startups
        }
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sectors/list")
async def get_all_sectors():
    """Mostra tutti i settori disponibili nel CSV con conteggi"""
    try:
        if startup_processor.df is not None or startup_processor.load_csv():
            startup_processor.normalize_data()
            
            # Ottieni settori unici e conta le startup per settore
            sector_counts = startup_processor.df['settore'].value_counts()
            
            sectors = []
            for sector, count in sector_counts.items():
                if pd.notna(sector) and str(sector).strip():
                    sectors.append({
                        "name": str(sector).strip(),
                        "count": int(count)
                    })
            
            # Ordina per numero di startup (decrescente)
            sectors.sort(key=lambda x: x['count'], reverse=True)
            
            return {
                "status": "success",
                "total_sectors": len(sectors),
                "sectors": sectors
            }
        else:
            return {"status": "no_data", "sectors": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/startups/sector-direct/{sector_name}")
async def get_startups_by_sector_direct(sector_name: str, limit: Optional[int] = 100):
    """Endpoint diretto per ottenere startup Energy dal CSV (bypass data_processor)"""
    try:
        import pandas as pd
        import os
        
        # Leggi direttamente il CSV
        csv_path = os.path.join(os.path.dirname(__file__), "data", "startup_data.csv")
        if not os.path.exists(csv_path):
            return {"status": "error", "message": "CSV non trovato"}
        
        # Leggi il CSV saltando le prime righe di header
        df = pd.read_csv(csv_path, skiprows=2)
        print(f"DEBUG: CSV caricato con {len(df)} righe e colonne: {list(df.columns)}")
        
        # Cerca la colonna Markets (settore)
        markets_col = None
        for col in df.columns:
            if 'markets' in col.lower():
                markets_col = col
                break
        
        if not markets_col:
            return {"status": "error", "message": f"Colonna Markets non trovata. Colonne disponibili: {list(df.columns)}"}
        
        print(f"DEBUG: Usando colonna Markets: {markets_col}")
        
        # Filtra per settore Energy (case-insensitive)
        sector_startups = df[
            df[markets_col].str.lower().str.contains('energy', na=False)
        ]
        
        print(f"DEBUG: Trovate {len(sector_startups)} startup con 'energy' in {markets_col}")
        
        if len(sector_startups) == 0:
            return {
                "status": "no_matches",
                "sector": sector_name,
                "message": f"No startups found in sector: {sector_name}",
                "startups": []
            }
        
        # Deduplica per Startup ID se disponibile, altrimenti per nome
        id_col = None
        for col in df.columns:
            if 'startup id' in col.lower():
                id_col = col
                break
        
        if id_col:
            print(f"DEBUG: Deduplicazione per colonna ID: {id_col}")
            sector_startups = sector_startups.drop_duplicates(subset=[id_col], keep='first')
            print(f"DEBUG: Dopo deduplicazione per ID: {len(sector_startups)} startup")
        else:
            # Fallback: deduplica per nome
            name_col = None
            for col in df.columns:
                if 'item name' in col.lower():
                    name_col = col
                    break
            
            if name_col:
                print(f"DEBUG: Deduplicazione per colonna nome: {name_col}")
                sector_startups = sector_startups.drop_duplicates(subset=[name_col], keep='first')
                print(f"DEBUG: Dopo deduplicazione per nome: {len(sector_startups)} startup")
        
        # Converti in formato startup
        startups = []
        for idx, row in sector_startups.head(limit).iterrows():
            # Estrai i campi principali
            name = str(row.get('Item Name', 'Unknown')) if 'Item Name' in row else 'Unknown'
            location = str(row.get('Location', 'Europe')) if 'Location' in row else 'Europe'
            description = str(row.get('Description', 'Startup innovativa')) if 'Description' in row else 'Startup innovativa'
            
            # Parsing finanziamenti
            funding = 0.0
            if 'Total Funding' in row and pd.notna(row['Total Funding']):
                try:
                    funding = float(str(row['Total Funding']).replace('€', '').replace(',', ''))
                except:
                    funding = 0.0
            
            startup = {
                "id": str(row.get(id_col, f"startup_{idx}")) if id_col else f"startup_{idx}",
                "name": name,
                "sector": sector_name,
                "funding": funding,
                "location": location,
                "description": description,
                "year": 2023,  # Default
                "employees": 10,  # Default
                "status": "Active",
                "pipeline": "Unknown",
                "founders": "Unknown",
                "social_links": {},
                "funding_formatted": f"€{funding:,.0f}" if funding > 0 else "€0",
                "description_short": description[:200] + ('...' if len(description) > 200 else ''),
                "has_website": False,
                "has_linkedin": False
            }
            startups.append(startup)
        
        return {
            "status": "success",
            "sector": sector_name,
            "count": len(startups),
            "total_in_sector": len(sector_startups),
            "startups": startups
        }
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/status")
async def get_data_status():
    """Verifica lo stato dei dati"""
    try:
        has_data = startup_processor.load_csv()
        if has_data:
            startup_processor.normalize_data()
            
        return {
            "csv_loaded": has_data,
            "csv_path": str(startup_processor.csv_path),
            "row_count": len(startup_processor.df) if startup_processor.df is not None else 0,
            "columns": list(startup_processor.df.columns) if startup_processor.df is not None else []
        }
    except Exception as e:
        return {
            "csv_loaded": False,
            "csv_path": str(startup_processor.csv_path),
            "error": str(e)
        }

@app.get("/api/data/columns")
async def get_columns_info():
    """Mostra come sono state categorizzate le colonne del CSV"""
    try:
        has_data = startup_processor.load_csv()
        if has_data:
            columns_info = startup_processor.get_all_columns_info()
            return {
                "status": "success",
                "data": columns_info,
                "message": f"Analizzate {columns_info.get('total_columns', 0)} colonne in {len(columns_info.get('column_categories', {}))} categorie"
            }
        else:
            return {
                "status": "no_data",
                "message": "CSV non trovato. Carica il file in backend/data/startup_data.csv"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port) 