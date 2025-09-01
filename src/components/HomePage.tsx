import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search, ArrowLeft, ChevronUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import BrainVisualization from './BrainVisualization';
import { BrainNode } from '../types';
import { useWindowSize } from '../hooks/useWindowSize';

const HomePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [knowledgeGraph, setKnowledgeGraph] = useState<any>(null);
  const [csvStartups, setCsvStartups] = useState<any[]>([]);
  const [zoomTarget, setZoomTarget] = useState<{x: number, y: number} | null>(null);
  const [showSectorDropdown, setShowSectorDropdown] = useState(false);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { width, height } = useWindowSize();

  // Settori di esempio per la tendina
  const exampleSectors = [
    '🏦 Fintech & Blockchain',
    '🤖 AI & Machine Learning', 
    '💊 Healthtech & Biotech',
    '🌱 Cleantech & Sustainability',
    '🚗 Mobility & EV',
    '🎓 Edtech & Learning',
    '🍽️ Foodtech & AgTech',
    '🏠 Proptech & Real Estate',
    '🛡️ Cybersecurity',
    '🎮 Gaming & Metaverse',
    '🚀 Space Tech',
    '👕 Fashion & Wearables'
  ];

  // Handle direct search from URL params
  useEffect(() => {
    const searchParam = searchParams.get('search');
    if (searchParam) {
      setSearchQuery(searchParam);
      searchWithOllama(searchParam);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowSectorDropdown(false);
    };
    
    if (showSectorDropdown) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showSectorDropdown]);

  const searchWithOllama = async (query: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8001/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setKnowledgeGraph(data.knowledge_graph);
        
        // Cerca anche startup nel CSV locale per settori specifici
        if (searchQuery.toLowerCase().includes('energy') || searchQuery.toLowerCase().includes('energia')) {
          try {
            const csvResponse = await fetch('http://localhost:8001/api/startups/sector/Energy');
            if (csvResponse.ok) {
              const csvData = await csvResponse.json();
              setCsvStartups(csvData.startups || []);
            }
          } catch (error) {
            console.log('CSV search not available');
          }
        } else {
          setCsvStartups([]);
        }
        
        // Set random zoom target for visual effect
        const randomX = Math.random() * width * 0.3 + width * 0.2;
        const randomY = Math.random() * height * 0.3 + height * 0.2;
        setZoomTarget({ x: randomX, y: randomY });
        
        setShowResults(true);
      } else {
        console.error('Search failed');
      }
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      searchWithOllama(searchQuery);
    }
  };

  const handleBack = () => {
    setShowResults(false);
    setKnowledgeGraph(null);
    setCsvStartups([]);
    setZoomTarget(null);
    setSearchQuery('');
  };

  const handleNodeClick = (node: BrainNode) => {
    if (node.label) {
      navigate(`/dashboard?focus=${node.id}`);
    }
  };

  const handleSectorSelect = (sector: string) => {
    // Rimuovi emoji e formatta per la ricerca
    const cleanSector = sector.replace(/[^\w\s&]/g, '').trim();
    setSearchQuery(`${cleanSector} startups 2024`);
    searchWithOllama(`${cleanSector} startups 2024`);
    setShowSectorDropdown(false);
  };

  const useCases = [
    {
      title: "Settori di esempio",
      action: () => setShowSectorDropdown(!showSectorDropdown)
    },
    {
      title: "La tua memoria digitale"
    },
    {
      title: "Radar dei trend"
    }
  ];

  

  return (
    <div className="min-h-screen bg-brain-dark text-white overflow-hidden relative">
      {/* Header - always visible */}
      <motion.header 
        className="relative z-10 pt-8 pb-4"
        animate={{ 
          opacity: showResults ? 0.3 : 1,
          scale: showResults ? 0.8 : 1 
        }}
        transition={{ duration: 0.6 }}
      >
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-6xl font-bold mb-4 brain-gradient bg-clip-text text-transparent">
            brAIn
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Piattaforma di intelligenza strategica alimentata da AI
          </p>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="relative">
        {/* Brain Visualization Background */}
        <motion.div 
          className="absolute inset-0 flex items-center justify-center opacity-90"
          animate={{ 
            scale: showResults ? 1.2 : 1,
            x: showResults ? (zoomTarget ? -width * 0.15 : 0) : 0,
            y: showResults ? (zoomTarget ? -height * 0.1 : 0) : 0
          }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
        >
          <BrainVisualization 
            width={width * 0.9}
            height={height * 0.9}
            onNodeClick={handleNodeClick}
            showLabels={showResults}
          />
        </motion.div>

        {/* Search Interface */}
        <motion.div 
          className="relative z-10 flex flex-col items-center justify-end min-h-[75vh] pb-16"
          animate={{ 
            opacity: showResults ? 0.2 : 1,
            scale: showResults ? 0.8 : 1
          }}
          transition={{ duration: 0.6 }}
        >
          <div className="glass-effect rounded-2xl p-4 max-w-md w-full mx-6 backdrop-blur-xl">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                                  placeholder="Chiedi a brAIn qualsiasi cosa..."
                disabled={isLoading}
                className="w-full px-4 py-2.5 pr-12 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brain-blue focus:border-transparent text-sm disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="absolute right-2.5 top-1/2 transform -translate-y-1/2 p-1.5 text-brain-cyan hover:text-white transition-colors disabled:opacity-50"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-brain-cyan border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
              </button>
            </form>
          </div>
        </motion.div>

        {/* Use Cases with Sector Dropdown */}
        <motion.div 
          className="relative z-10 flex justify-center items-center pb-8"
          animate={{ 
            opacity: showResults ? 0 : 1,
            y: showResults ? 50 : 0
          }}
          transition={{ duration: 0.4 }}
        >
          <div className="flex gap-8 max-w-2xl relative">
            {useCases.map((useCase, index) => (
              <div 
                key={index} 
                className="text-center cursor-pointer relative"
                onClick={useCase.action}
              >
                <h3 className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-1">
                  {useCase.title}
                  {index === 0 && (
                    <ChevronUp 
                      className={`w-4 h-4 transition-transform duration-200 ${
                        showSectorDropdown ? 'rotate-180' : ''
                      }`}
                    />
                  )}
                </h3>
                
                {/* Sector Dropdown */}
                {index === 0 && (
                  <AnimatePresence>
                    {showSectorDropdown && (
                      <motion.div
                        initial={{ opacity: 0, y: -10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -10, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="absolute top-8 left-1/2 transform -translate-x-1/2 w-64 glass-effect rounded-xl p-4 border border-white border-opacity-20"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <div className="grid grid-cols-1 gap-2">
                          {exampleSectors.map((sector, sectorIndex) => (
                            <motion.button
                              key={sectorIndex}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: sectorIndex * 0.03 }}
                              onClick={() => handleSectorSelect(sector)}
                              className="text-left px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white hover:bg-opacity-10 rounded-lg transition-all"
                            >
                              {sector}
                            </motion.button>
                          ))}
                        </div>
                        
                        <div className="mt-3 pt-3 border-t border-white border-opacity-20">
                          <p className="text-xs text-gray-400 text-center">
                            💡 Oppure cerca qualsiasi altro settore
                          </p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </main>

      {/* Results Panel - slides in from right */}
      <AnimatePresence>
        {showResults && knowledgeGraph && (
          <motion.div
            className="fixed top-0 right-0 w-1/2 h-full bg-brain-dark border-l border-gray-800 z-50"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
          >
            {/* Panel Header */}
            <div className="border-b border-gray-800 p-4 flex items-center gap-4">
              <button
                onClick={handleBack}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <h2 className="text-lg font-semibold truncate">{searchQuery}</h2>
            </div>

            {/* Panel Content */}
            <div className="p-6 overflow-y-auto h-full pb-20">
              {/* Summary */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="mb-8"
              >
                <h3 className="text-2xl font-bold mb-4 text-white">
                  Analisi Knowledge Graph
                </h3>
                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4 border-l-4 border-brain-cyan">
                  <p className="text-gray-300 text-sm leading-relaxed">
                    {(knowledgeGraph.summary || "Analisi AI generata basata sulla tua ricerca.").replace(/\*+/g, '').replace(/\n+/g, ' ').trim()}
                  </p>
                </div>
              </motion.div>

              {/* Key Concepts */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mb-8"
              >
                <h4 className="text-lg font-semibold mb-4 text-brain-cyan">Concetti Chiave</h4>
                <div className="grid grid-cols-2 gap-3">
                  {knowledgeGraph.nodes?.map((node: any, index: number) => (
                    <motion.div
                      key={node.id}
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 0.7 + index * 0.1 }}
                      className="bg-gradient-to-r from-brain-blue to-brain-cyan bg-opacity-20 text-white rounded-lg px-4 py-3 text-sm font-medium hover:bg-opacity-30 transition-all cursor-pointer border border-brain-blue border-opacity-30"
                    >
                      {node.label.replace(/\*+/g, '').trim()}
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* Insights */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.8 }}
              >
                <h4 className="text-lg font-semibold mb-4 text-brain-cyan">Insights AI</h4>
                <div className="space-y-4">
                  {knowledgeGraph.insights?.map((insight: string, index: number) => (
                    <motion.div
                      key={index}
                      initial={{ x: 20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 1 + index * 0.15 }}
                      className="bg-gray-800 bg-opacity-30 rounded-lg p-4 border-l-4 border-brain-blue"
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-brain-cyan rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {insight.replace(/\*+/g, '').replace(/\n+/g, ' ').trim()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* CSV Startups (Energy sector) */}
              {csvStartups && csvStartups.length > 0 && (
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 1.2 }}
                  className="mb-8"
                >
                  <h4 className="text-lg font-semibold mb-4 text-brain-cyan">
                    🚀 Startup Energy dal CSV ({csvStartups.length})
                  </h4>
                  <div className="space-y-4">
                    {csvStartups.slice(0, 6).map((startup: any, idx: number) => (
                      <div key={idx} className="bg-gray-800 bg-opacity-30 rounded-lg p-4 border-l-4 border-brain-cyan">
                        <div className="space-y-3">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h5 className="text-white text-base font-semibold mb-1">{startup.name}</h5>
                              <div className="flex items-center gap-3 text-xs text-gray-400">
                                <span className="px-2 py-1 bg-brain-blue bg-opacity-20 rounded-full">{startup.sector}</span>
                                <span>{startup.location}</span>
                                <span className="font-medium text-brain-cyan">{startup.funding_formatted}</span>
                              </div>
                            </div>
                          </div>
                          
                          {startup.description_short && (
                            <p className="text-gray-300 text-sm leading-relaxed">
                              {startup.description_short}
                            </p>
                          )}
                          
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>Founded: {startup.year}</span>
                            <span>Employees: {startup.employees}</span>
                            <span>Status: {startup.status}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Additional Context */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 1.5 }}
                className="mt-8 bg-gradient-to-r from-brain-blue to-brain-cyan bg-opacity-10 rounded-lg p-4 border border-brain-cyan border-opacity-30"
              >
                <h5 className="text-sm font-semibold text-brain-cyan mb-2">💡 Suggerimento</h5>
                <p className="text-gray-300 text-xs leading-relaxed">
                  Clicca sui nodi del cervello per esplorare connessioni specifiche o prova ricerche come "startup fintech 2025" o "tecnologie emergenti AI".
                </p>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HomePage; 