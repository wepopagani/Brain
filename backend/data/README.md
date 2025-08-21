# 📊 Dati delle Startup per brAIn

## 🎯 Come Caricare i Tuoi Dati

### 1. **Posiziona il tuo CSV qui:**
```
backend/data/startup_data.csv
```

### 2. **Formato CSV Supportato**

Il sistema riconosce automaticamente queste colonne (in qualsiasi ordine):

| Campo | Possibili Nomi Colonne | Esempio |
|-------|-------------------------|---------|
| **Nome** | `name`, `company`, `startup_name`, `azienda` | TechStart SRL |
| **Settore** | `sector`, `industry`, `vertical`, `categoria` | Fintech |
| **Finanziamenti** | `funding`, `investment`, `raised`, `capital` | 2.5M, €2,500,000 |
| **Round** | `round`, `funding_round`, `stage`, `serie` | Series A |
| **Posizione** | `location`, `country`, `city`, `luogo`, `sede` | Milano |
| **Descrizione** | `description`, `summary`, `about`, `desc` | Piattaforma di pagamenti... |
| **Anno** | `year`, `founded`, `anno_fondazione`, `date` | 2022 |
| **Dipendenti** | `employees`, `team_size`, `people`, `staff` | 25 |

### 3. **Formati Finanziamenti Supportati**
- **Con suffisso**: `1.5M`, `500K`, `2.3B`
- **Numerico**: `1500000`, `500000`
- **Con valuta**: `€1.5M`, `$500K`
- **Con separatori**: `1,500,000`

### 4. **Settori Automaticamente Normalizzati**
Il sistema raggruppa automaticamente i settori simili:

- **Fintech**: fintech, finance, banking, payments
- **Healthtech**: health, medical, healthcare, biotech  
- **Cleantech**: clean, energy, renewable, green, sustainability
- **Mobility**: mobility, transport, automotive, ev, electric
- **Edtech**: education, learning, edtech
- **Foodtech**: food, agriculture, agtech
- **Proptech**: real estate, property, construction
- **AI**: ai, artificial intelligence, machine learning, ml
- **SaaS**: saas, software, b2b, enterprise

### 5. **Esempio File CSV**

Vedi `startup_data_example.csv` per un template completo.

### 6. **Verifica dei Dati**

Dopo aver caricato il CSV, puoi verificare che tutto funzioni:

```bash
# Nel backend
curl http://localhost:8001/api/data/status

# Risposta attesa:
{
  "csv_loaded": true,
  "csv_path": "data/startup_data.csv", 
  "row_count": 990,
  "columns": ["nome", "settore", "finanziamenti", ...]
}
```

### 7. **API Disponibili**

Una volta caricato il CSV, avrai accesso a:

- `GET /api/startups?limit=100` - Lista startup
- `GET /api/analytics/sectors` - Analisi per settore  
- `GET /api/analytics/funding` - Analisi finanziamenti
- `POST /api/search/startups` - Ricerca startup
- `GET /api/data/status` - Stato dei dati

### 🚀 **Quick Start**

1. Rinomina il tuo CSV in `startup_data.csv`
2. Copialo in `backend/data/`
3. Riavvia il backend: `uvicorn app:app --host 0.0.0.0 --port 8001`
4. Le tue 990 startup saranno immediatamente disponibili!

### ⚡ **Note Tecniche**

- **Formato**: CSV con separatore virgola
- **Encoding**: UTF-8 (per caratteri italiani)
- **Dimensioni**: Testato fino a 10,000+ startup
- **Performance**: Caricamento automatico all'avvio 