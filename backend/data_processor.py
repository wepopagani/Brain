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
        """Normalizza e pulisce i dati del CSV in base alle categorie trovate"""
        if self.original_df is None:
            return
        
        # Mapping diretto basato sulla struttura CSV osservata
        # I nomi delle colonne sono in realtà i valori della prima startup
        name_col = self.original_df.columns[1] if len(self.original_df.columns) > 1 else None  # "Mae"
        location_col = self.original_df.columns[6] if len(self.original_df.columns) > 6 else None  # "Berlin, Germany"
        markets_col = self.original_df.columns[7] if len(self.original_df.columns) > 7 else None  # "Cultural Experience..."
        funding_col = self.original_df.columns[52] if len(self.original_df.columns) > 52 else None  # "EUR 100000"
        description_col = self.original_df.columns[50] if len(self.original_df.columns) > 50 else None  # Descrizione lunga
        founded_col = self.original_df.columns[48] if len(self.original_df.columns) > 48 else None  # "Oct '24"
        employees_col = None  # Non identificato direttamente
        
        # Log delle colonne identificate
        self.logger.info(f"Colonne identificate: nome={name_col}, location={location_col}, markets={markets_col}, funding={funding_col}")
        
        # Crea DataFrame normalizzato
        normalized_data = {}
        
        # Campi principali
        normalized_data['nome'] = self._extract_column_data(name_col, [f"Startup_{i}" for i in range(len(self.original_df))])
        normalized_data['location'] = self._extract_column_data(location_col, "Europe")
        normalized_data['settore'] = self._extract_markets_data(markets_col)
        normalized_data['finanziamenti'] = self._extract_funding_data(funding_col)
        normalized_data['descrizione'] = self._extract_column_data(description_col, "Startup innovativa")
        normalized_data['anno'] = self._extract_year_data(founded_col)
        normalized_data['dipendenti'] = self._extract_numeric_data(employees_col, 10)
        
        # Aggiungi informazioni sui founder
        normalized_data['founders'] = self._extract_founders_data()
        
        # Aggiungi link social
        normalized_data['social_links'] = self._extract_social_data()
        
        # Aggiungi stato e pipeline
        normalized_data['status'] = self._extract_column_data(self._find_best_column(['status']), "Active")
        normalized_data['pipeline'] = self._extract_column_data(self._find_best_column(['pipeline']), "Unknown")
        
        # Mantieni anche tutti i dati originali come JSON
        normalized_data['raw_data'] = self.original_df.to_dict('records')
        
        self.df = pd.DataFrame({
            'nome': normalized_data['nome'],
            'location': normalized_data['location'],
            'settore': normalized_data['settore'],
            'finanziamenti': normalized_data['finanziamenti'],
            'descrizione': normalized_data['descrizione'],
            'anno': normalized_data['anno'],
            'dipendenti': normalized_data['dipendenti'],
            'status': normalized_data['status'],
            'pipeline': normalized_data['pipeline'],
            'founders': normalized_data['founders'],
            'social_links': normalized_data['social_links']
        })
        
        # Pulisci i dati
        self._clean_funding_data()
        self._clean_sector_data()
        
        self.logger.info(f"Dati normalizzati: {len(self.df)} startup processate")
    
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
        """Cerca startup in base a una query"""
        if self.df is None:
            return []
        
        # Cerca in nome, settore, descrizione e founders
        mask = (
            self.df['nome'].str.contains(query, case=False, na=False) |
            self.df['settore'].str.contains(query, case=False, na=False) |
            self.df['descrizione'].str.contains(query, case=False, na=False) |
            self.df['founders'].str.contains(query, case=False, na=False)
        )
        
        filtered_df = self.df[mask].head(limit)
        return self.get_startup_data_from_df(filtered_df)
    
    def get_startup_data_from_df(self, df_subset) -> List[Dict[str, Any]]:
        """Helper per convertire DataFrame in lista di startup"""
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

# Istanza globale del processore
startup_processor = StartupDataProcessor() 