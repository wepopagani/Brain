import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import re
import logging

class StartupDataProcessor:
    """Processore avanzato per i dati delle startup con categorizzazione automatica delle colonne"""
    
    def __init__(self, csv_path: str = "data/startup_data.csv"):
        self.csv_path = Path(csv_path)
        self.df = None
        self.original_df = None
        self.processed_data = None
        self.column_categories = {}
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Categorie per l'analisi automatica delle colonne
        self.category_patterns = {
            'identity': ['startup id', 'item name', 'company name', 'name', 'nome', 'azienda', 'startup'],
            'basic_info': ['tagline', 'description', 'descrizione', 'about', 'differentiators', 'interfaces'],
            'founders': ['founder', 'ceo', 'cto', 'fondatore', 'role'],
            'location': ['location', 'sede', 'city', 'città', 'country', 'paese', 'italia', 'estero'],
            'business': ['markets', 'sector', 'settore', 'industry', 'revenue model', 'tema', 'tecnologia'],
            'funding': ['funding', 'finanziamenti', 'investment', 'valuation', 'runway', 'rounds', 'f6s', 'amount', 'currency'],
            'metrics': ['score', 'employees', 'dipendenti', 'clients', 'revenue', 'rev'],
            'social': ['website', 'linkedin', 'twitter', 'facebook', 'github', 'angellist', 'google plus'],
            'dates': ['founded', 'fondato', 'incorporated', 'contact', 'updated', 'finalize', 'start'],
            'status': ['status', 'pipeline', 'stage', 'milestone', 'bootcamp', 'selection'],
            'media': ['videos', 'decks', 'files'],
            'notes': ['notes', 'tags', 'analyst', 'evaluators', 'msg', 'assigned'],
            'sources': ['source', 'type']
        }
        
    def load_csv(self) -> bool:
        """Carica il CSV delle startup con analisi automatica delle colonne"""
        try:
            if not self.csv_path.exists():
                self.logger.error(f"File CSV non trovato: {self.csv_path}")
                return False
            
            # Leggi il CSV saltando le righe vuote iniziali
            self.original_df = pd.read_csv(self.csv_path, skiprows=2)  # Salta le prime 2 righe di header
            
            # Pulisci i nomi delle colonne
            self.original_df.columns = [col.strip() for col in self.original_df.columns]
            
            # Rimuovi righe completamente vuote
            self.original_df = self.original_df.dropna(how='all')
            
            self.logger.info(f"Caricato CSV con {len(self.original_df)} startup e {len(self.original_df.columns)} colonne")
            
            # Analizza e categorizza le colonne
            self._analyze_columns()
            
            # Normalizza i dati
            self.normalize_data()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Errore nel caricamento CSV: {e}")
            return False
    
    def _analyze_columns(self):
        """Analizza e categorizza automaticamente tutte le colonne del CSV"""
        self.column_categories = {category: [] for category in self.category_patterns.keys()}
        self.column_categories['other'] = []
        
        for column in self.original_df.columns:
            column_lower = column.lower().strip()
            categorized = False
            
            # Categorizza in base ai pattern
            for category, patterns in self.category_patterns.items():
                if any(pattern in column_lower for pattern in patterns):
                    self.column_categories[category].append(column)
                    categorized = True
                    break
            
            if not categorized:
                self.column_categories['other'].append(column)
        
        # Log delle categorie trovate
        for category, columns in self.column_categories.items():
            if columns:
                self.logger.info(f"Categoria '{category}': {len(columns)} colonne")
    
    def normalize_data(self) -> None:
        """Normalizza e pulisce i dati del CSV in base alle colonne reali"""
        if self.original_df is None:
            return
        
        # Usa i nomi reali delle colonne del CSV
        self.df = self.original_df.copy()
        
        # Rinomina le colonne per facilitare l'uso
        column_mapping = {
            'Startup ID': 'startup_id',
            'Item Name': 'nome',
            'Location': 'location', 
            'Markets': 'settore',
            'Description': 'descrizione',
            'Founded': 'anno',
            'Number of employees': 'dipendenti',
            'Total Funding': 'finanziamenti',
            'Founder 1 Name': 'founder1',
            'Founder 2 Name': 'founder2',
            'Website 1': 'website',
            'Linkedin': 'linkedin',
            'Status': 'status',
            'Pipeline': 'pipeline'
        }
        
        # Rinomina solo le colonne che esistono
        for old_name, new_name in column_mapping.items():
            if old_name in self.df.columns:
                self.df = self.df.rename(columns={old_name: new_name})
        
        # Pulisci i dati
        self.df = self.df.dropna(subset=['nome'])  # Rimuovi righe senza nome
        
        # Normalizza il settore - prendi solo il primo se ce ne sono più
        if 'settore' in self.df.columns:
            self.df['settore'] = self.df['settore'].apply(
                lambda x: str(x).split(',')[0].strip() if pd.notna(x) else 'Technology'
            )
        
        # Normalizza l'anno di fondazione
        if 'anno' in self.df.columns:
            self.df['anno'] = self.df['anno'].apply(self._extract_year_from_string)
        
        # Normalizza i finanziamenti
        if 'finanziamenti' in self.df.columns:
            self.df['finanziamenti'] = self.df['finanziamenti'].apply(self._parse_funding)
        
        # Normalizza i dipendenti
        if 'dipendenti' in self.df.columns:
            self.df['dipendenti'] = self.df['dipendenti'].apply(self._extract_employees_from_string)
        
        # Aggiungi campi mancanti con valori di default
        if 'status' not in self.df.columns:
            self.df['status'] = 'Active'
        if 'pipeline' not in self.df.columns:
            self.df['pipeline'] = 'Unknown'
        
        # Crea campo founders combinato
        founder_cols = [col for col in self.df.columns if 'founder' in col.lower()]
        if founder_cols:
            self.df['founders'] = self.df[founder_cols].apply(
                lambda row: ', '.join([str(val) for val in row if pd.notna(val) and str(val).strip()]), 
                axis=1
            )
        else:
            self.df['founders'] = 'Unknown'
        
        # Crea campo social_links
        social_cols = [col for col in self.df.columns if col in ['website', 'linkedin']]
        if social_cols:
            self.df['social_links'] = self.df[social_cols].apply(
                lambda row: {col: str(val) for col, val in row.items() if pd.notna(val) and str(val).strip()}, 
                axis=1
            )
        else:
            self.df['social_links'] = [{}] * len(self.df)
        
        # Deduplicazione: rimuovi startup duplicate basandosi su startup_id
        if 'startup_id' in self.df.columns:
            initial_count = len(self.df)
            self.df = self.df.drop_duplicates(subset=['startup_id'], keep='first')
            final_count = len(self.df)
            if initial_count != final_count:
                self.logger.info(f"Deduplicazione: rimosse {initial_count - final_count} startup duplicate")
        else:
            # Fallback: deduplica per nome se startup_id non è disponibile
            initial_count = len(self.df)
            self.df = self.df.drop_duplicates(subset=['nome'], keep='first')
            final_count = len(self.df)
            if initial_count != final_count:
                self.logger.info(f"Deduplicazione fallback per nome: rimosse {initial_count - final_count} startup duplicate")
        
        self.logger.info(f"Normalizzati {len(self.df)} startup")
    
    def _extract_year_from_string(self, value) -> int:
        """Estrae l'anno da una stringa di data"""
        if pd.isna(value) or value == '':
            return 2023
        
        str_val = str(value).strip()
        
        # Cerca pattern di anno (19xx o 20xx)
        year_match = re.search(r'\b(19|20)\d{2}\b', str_val)
        if year_match:
            return int(year_match.group())
        
        # Se non trova anno, ritorna 2023
        return 2023
    
    def _extract_employees_from_string(self, value) -> int:
        """Estrae il numero di dipendenti da una stringa"""
        if pd.isna(value) or value == '':
            return 10
        
        str_val = str(value).strip()
        
        # Cerca numeri nella stringa
        numbers = re.findall(r'\d+', str_val)
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                return 10
        
        return 10
    
    def _find_best_column(self, preferred_names: List[str]) -> Optional[str]:
        """Trova la migliore colonna corrispondente dai nomi preferiti"""
        for pref in preferred_names:
            for col in self.original_df.columns:
                if pref.lower() in col.lower():
                    return col
        return None
    
    def _extract_column_data(self, column_name: Optional[str], default_value: Any):
        """Estrae dati da una colonna specifica o usa valori di default"""
        if column_name and column_name in self.original_df.columns:
            if isinstance(default_value, list):
                return self.original_df[column_name].fillna(pd.Series(default_value))
            else:
                return self.original_df[column_name].fillna(default_value)
        else:
            if isinstance(default_value, list):
                return default_value
            else:
                return [default_value] * len(self.original_df)
    
    def _extract_markets_data(self, markets_col: Optional[str]) -> List[str]:
        """Estrae e normalizza i dati dei settori/markets"""
        if markets_col and markets_col in self.original_df.columns:
            markets_data = []
            for value in self.original_df[markets_col]:
                if pd.notna(value):
                    # Estrai il primo settore se ce ne sono diversi separati da virgola
                    sectors = str(value).split(',')
                    markets_data.append(sectors[0].strip())
                else:
                    markets_data.append("Technology")
            return markets_data
        else:
            return ["Technology"] * len(self.original_df)
    
    def _extract_funding_data(self, funding_col: Optional[str]) -> List[float]:
        """Estrae e normalizza i dati di finanziamento"""
        if funding_col and funding_col in self.original_df.columns:
            return self.original_df[funding_col].apply(self._parse_funding)
        else:
            return [0.0] * len(self.original_df)
    
    def _extract_year_data(self, year_col: Optional[str]) -> List[int]:
        """Estrae dati dell'anno di fondazione"""
        if year_col and year_col in self.original_df.columns:
            years = []
            for value in self.original_df[year_col]:
                if pd.notna(value):
                    # Estrai anno da vari formati
                    year_match = re.search(r'\b(19|20)\d{2}\b', str(value))
                    if year_match:
                        years.append(int(year_match.group()))
                    else:
                        years.append(2023)
                else:
                    years.append(2023)
            return years
        else:
            return [2023] * len(self.original_df)
    
    def _extract_numeric_data(self, col: Optional[str], default: int) -> List[int]:
        """Estrae dati numerici da una colonna"""
        if col and col in self.original_df.columns:
            numeric_data = []
            for value in self.original_df[col]:
                if pd.notna(value) and str(value).strip() not in ['', '.', 'nan']:
                    # Estrai numeri dalla stringa
                    numbers = re.findall(r'\d+', str(value))
                    if numbers:
                        try:
                            numeric_data.append(int(numbers[0]))
                        except ValueError:
                            numeric_data.append(default)
                    else:
                        numeric_data.append(default)
                else:
                    numeric_data.append(default)
            return numeric_data
        else:
            return [default] * len(self.original_df)
    
    def _extract_founders_data(self) -> List[str]:
        """Estrae informazioni sui founder"""
        founder_cols = self.column_categories.get('founders', [])
        founders_data = []
        
        for idx in range(len(self.original_df)):
            founders = []
            for col in founder_cols:
                if 'name' in col.lower():
                    value = self.original_df.iloc[idx][col]
                    if pd.notna(value) and str(value).strip():
                        founders.append(str(value).strip())
            
            if founders:
                founders_data.append(", ".join(founders[:3]))  # Max 3 founders
            else:
                founders_data.append("Unknown")
        
        return founders_data
    
    def _extract_social_data(self) -> List[Dict[str, str]]:
        """Estrae link social media"""
        social_cols = self.column_categories.get('social', [])
        social_data = []
        
        for idx in range(len(self.original_df)):
            social_links = {}
            for col in social_cols:
                value = self.original_df.iloc[idx][col]
                if pd.notna(value) and str(value).strip():
                    platform = col.lower().replace(' ', '_')
                    social_links[platform] = str(value).strip()
            
            social_data.append(social_links)
        
        return social_data
    
    def _parse_funding(self, value):
        """Parsing avanzato dei dati di finanziamento"""
        if pd.isna(value) or value == '' or str(value).strip() == '':
            return 0.0
        
        # Converti in stringa e pulisci
        str_val = str(value).lower().replace(',', '').replace(' ', '').replace('€', '').replace('$', '')
        
        # Se è solo un punto o vuoto, ritorna 0
        if str_val == '.' or str_val == '' or str_val == 'nan':
            return 0.0
        
        # Estrai numeri e moltiplicatori
        multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000}
        
        # Cerca pattern come "1.5M", "500K", etc.
        for suffix, mult in multipliers.items():
            if suffix in str_val:
                number = re.findall(r'\d+\.?\d*', str_val)
                if number:
                    try:
                        return float(number[0]) * mult
                    except ValueError:
                        continue
        
        # Se non trova moltiplicatori, prova a estrarre il numero
        numbers = re.findall(r'\d+\.?\d*', str_val)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        
        return 0.0
    
    def _clean_funding_data(self):
        """Pulisce e normalizza i dati di finanziamento"""
        if 'finanziamenti' in self.df.columns:
            self.df['finanziamenti'] = self.df['finanziamenti'].apply(self._parse_funding)
    
    def _clean_sector_data(self):
        """Normalizza i settori"""
        if 'settore' not in self.df.columns:
            return
            
        # Expanded mapping for multi-sector recognition
        sector_mapping = {
            'Fintech': ['fintech', 'finance', 'banking', 'payments', 'financial', 'blockchain', 'crypto', 'defi', 'insurtech', 'wealthtech', 'regtech', 'lending'],
            'Healthtech': ['health', 'medical', 'healthcare', 'biotech', 'pharma', 'medtech', 'telemedicine', 'digital health', 'diagnostics', 'therapeutics'],
            'Cleantech': ['clean', 'energy', 'renewable', 'green', 'sustainability', 'solar', 'wind', 'carbon', 'climate', 'environmental', 'circular economy'],
            'Mobility': ['mobility', 'transport', 'automotive', 'ev', 'electric', 'logistics', 'autonomous', 'micromobility', 'shared mobility', 'delivery'],
            'Edtech': ['education', 'learning', 'edtech', 'training', 'e-learning', 'mooc', 'skill development', 'certification'],
            'Foodtech': ['food', 'agriculture', 'agtech', 'farming', 'foodservice', 'alternative protein', 'precision agriculture', 'vertical farming'],
            'Proptech': ['real estate', 'property', 'construction', 'housing', 'proptech', 'smart buildings', 'facility management'],
            'AI/ML': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'data', 'computer vision', 'nlp', 'robotics', 'automation'],
            'Gaming': ['gaming', 'games', 'esports', 'metaverse', 'virtual reality', 'augmented reality', 'entertainment'],
            'Fashion': ['fashion', 'apparel', 'clothing', 'textile', 'luxury', 'wearables', 'sustainable fashion'],
            'Cybersecurity': ['cybersecurity', 'security', 'cyber', 'privacy', 'encryption', 'identity', 'compliance'],
            'Logistics': ['logistics', 'supply chain', 'fulfillment', 'warehousing', 'shipping', 'delivery', '3pl'],
            'Manufacturing': ['manufacturing', 'industry 4.0', 'iot', 'industrial', 'automation', 'robotics', '3d printing'],
            'Media': ['media', 'content', 'streaming', 'digital media', 'creator economy', 'advertising', 'marketing'],
            'Web3': ['web3', 'blockchain', 'nft', 'dao', 'defi', 'crypto', 'metaverse', 'decentralized'],
            'SaaS': ['saas', 'software', 'b2b', 'enterprise', 'platform', 'productivity', 'workflow'],
            'Social': ['social', 'networking', 'community', 'cultural', 'dating', 'communication'],
            'Travel': ['travel', 'tourism', 'hospitality', 'booking', 'accommodation', 'transportation'],
            'Space': ['space', 'aerospace', 'satellite', 'launch', 'space technology', 'earth observation'],
            'Biotech': ['biotech', 'biotechnology', 'life sciences', 'genomics', 'synthetic biology', 'drug discovery']
        }
        
        def normalize_sector(sector):
            if pd.isna(sector):
                return "Technology"
            
            sector_lower = str(sector).lower()
            for normalized, keywords in sector_mapping.items():
                if any(keyword in sector_lower for keyword in keywords):
                    return normalized
            
            return str(sector).title()
        
        self.df['settore'] = self.df['settore'].apply(normalize_sector)

    def get_all_columns_info(self) -> Dict[str, Any]:
        """Restituisce informazioni su tutte le colonne del CSV originale"""
        if self.original_df is None:
            return {}
        
        return {
            "total_columns": len(self.original_df.columns),
            "total_rows": len(self.original_df),
            "column_categories": {
                category: len(columns) 
                for category, columns in self.column_categories.items() 
                if columns
            },
            "sample_columns": {
                category: columns[:5]  # Prime 5 colonne per categoria
                for category, columns in self.column_categories.items() 
                if columns
            }
        }
    
    def get_startup_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Restituisce i dati delle startup come lista di dizionari"""
        if self.df is None:
            return []
        
        df_subset = self.df.head(limit) if limit else self.df
        
        startups = []
        for idx, row in df_subset.iterrows():
            startup = {
                "id": f"startup_{idx}",
                "name": str(row.get('nome', 'Unknown')),
                "sector": str(row.get('settore', 'Technology')),
                "funding": float(row.get('finanziamenti', 0)),
                "location": str(row.get('location', 'Europe')),
                "description": str(row.get('descrizione', 'Startup innovativa')),
                "year": int(row.get('anno', 2023)),
                "employees": int(row.get('dipendenti', 10)),
                "status": str(row.get('status', 'Active')),
                "pipeline": str(row.get('pipeline', 'Unknown')),
                "founders": str(row.get('founders', 'Unknown')),
                "social_links": row.get('social_links', {}),
                "funding_formatted": self._format_funding(row.get('finanziamenti', 0))
            }
            startups.append(startup)
        
        return startups
    
    def _format_funding(self, amount: float) -> str:
        """Formatta l'importo del finanziamento in modo leggibile"""
        if amount >= 1000000000:
            return f"€{amount/1000000000:.1f}B"
        elif amount >= 1000000:
            return f"€{amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"€{amount/1000:.0f}K"
        else:
            return f"€{amount:.0f}"
    
    def get_sector_analytics(self) -> Dict[str, Any]:
        """Analisi per settore"""
        if self.df is None:
            return {}
        
        sector_stats = self.df.groupby('settore').agg({
            'nome': 'count',
            'finanziamenti': ['sum', 'mean', 'median'],
            'dipendenti': 'mean'
        }).round(2)
        
        # Converte in formato più leggibile
        result = {}
        for sector in sector_stats.index:
            result[sector] = {
                "count": int(sector_stats.loc[sector, ('nome', 'count')]),
                "total_funding": float(sector_stats.loc[sector, ('finanziamenti', 'sum')]),
                "avg_funding": float(sector_stats.loc[sector, ('finanziamenti', 'mean')]),
                "median_funding": float(sector_stats.loc[sector, ('finanziamenti', 'median')]),
                "avg_employees": float(sector_stats.loc[sector, ('dipendenti', 'mean')])
            }
        
        return result
    
    def get_funding_analytics(self) -> Dict[str, Any]:
        """Analisi dei finanziamenti"""
        if self.df is None:
            return {}
        
        return {
            "total_funding": float(self.df['finanziamenti'].sum()),
            "average_funding": float(self.df['finanziamenti'].mean()),
            "median_funding": float(self.df['finanziamenti'].median()),
            "top_funded": self.df.nlargest(10, 'finanziamenti')[['nome', 'finanziamenti', 'settore']].to_dict('records'),
            "funding_by_sector": self.df.groupby('settore')['finanziamenti'].sum().to_dict()
        }
    
    def search_startups(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Cerca startup in base a una query (ottimizzata per evitare duplicati)"""
        if self.df is None:
            return []
        
        query_lower = query.lower().strip()
        
        # Cerca in nome, settore, descrizione e founders
        mask = (
            self.df['nome'].str.contains(query_lower, case=False, na=False) |
            self.df['settore'].str.contains(query_lower, case=False, na=False) |
            self.df['descrizione'].str.contains(query_lower, case=False, na=False) |
            self.df['founders'].str.contains(query_lower, case=False, na=False)
        )
        
        filtered_df = self.df[mask]
        
        # Rimuovi duplicati basandosi su nome + settore + location
        filtered_df = filtered_df.drop_duplicates(subset=['nome', 'settore', 'location'])
        
        # Ordina per finanziamenti (più alti prima) e limita i risultati
        filtered_df = filtered_df.sort_values('finanziamenti', ascending=False).head(limit)
        
        return self.get_startup_data_from_df(filtered_df)
    
    def get_startup_data_from_df(self, df_subset) -> List[Dict[str, Any]]:
        """Helper per convertire DataFrame in lista di startup"""
        startups = []
        for idx, row in df_subset.iterrows():
            startup = {
                "id": str(row.get('startup_id', f"startup_{idx}")),
                "name": str(row.get('nome', 'Unknown')),
                "sector": str(row.get('settore', 'Technology')),
                "funding": float(row.get('finanziamenti', 0)),
                "location": str(row.get('location', 'Europe')),
                "description": str(row.get('descrizione', 'Startup innovativa')),
                "year": int(row.get('anno', 2023)),
                "employees": int(row.get('dipendenti', 10)),
                "status": str(row.get('status', 'Active')),
                "pipeline": str(row.get('pipeline', 'Unknown')),
                "founders": str(row.get('founders', 'Unknown')),
                "social_links": row.get('social_links', {}),
                "funding_formatted": self._format_funding(row.get('finanziamenti', 0)),
                "description_short": str(row.get('descrizione', 'Startup innovativa'))[:200].replace('\n', ' ').strip() + ('...' if len(str(row.get('descrizione', ''))) > 200 else ''),
                "has_website": bool(row.get('social_links', {}).get('website', False)),
                "has_linkedin": bool(row.get('social_links', {}).get('linkedin', False))
            }
            startups.append(startup)
        
        return startups

# Istanza globale del processore
startup_processor = StartupDataProcessor() 