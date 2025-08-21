import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import BrainVisualization from './BrainVisualization';
import { Startup, TrendData, BrainNode } from '../types';

const Dashboard: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [, setSelectedStartup] = useState<Startup | null>(null);
  const [trendData, setTrendData] = useState<TrendData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Mock data - in production this would come from your API
  useEffect(() => {
    const mockStartup: Startup = {
      id: 'electra-motors',
      name: 'Electra Motors',
      sector: 'Mobility & EV',
      funding: 15000000,
      round: 'Series A',
      location: 'Europe',
      description: 'Electra Motors is a startup focused on electric vehicle manufacturing and battery technology.',
      collaborations: ['Solaris Tech', 'Orion Charge']
    };

    const mockTrendData: TrendData = {
      id: 'mobility-ev',
      title: 'Startups Working on Mobility & EV in Europe with Funding in the Last 12 Months',
      description: 'A recent surge in startups focused on electric vehicles and advanced mobility solutions.',
      growth: 15,
      startups: [mockStartup]
    };

    setTimeout(() => {
      setSelectedStartup(mockStartup);
      setTrendData(mockTrendData);
      setIsLoading(false);
    }, 1000);
  }, [searchParams]);

  const handleNodeClick = (node: BrainNode) => {
    // Handle brain node interactions
    console.log('Node clicked:', node);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-brain-dark flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-brain-blue border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white">Analyzing data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brain-dark text-white">
      {/* Header */}
      <header className="border-b border-gray-800 p-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1 className="text-lg text-white">
            Show me all startups working on Mobility and EV in Europe that got funding in the last 12 months
          </h1>
        </div>
      </header>

      <div className="flex h-screen">
        {/* Left Panel - Brain Visualization */}
        <div className="w-1/2 p-6 border-r border-gray-800">
          <div className="h-full bg-brain-dark">
            <BrainVisualization 
              width={600}
              height={600}
              onNodeClick={handleNodeClick}
              showLabels={true}
            />
          </div>
        </div>

        {/* Right Panel - Information */}
        <div className="w-1/2 p-6 overflow-y-auto bg-brain-dark">
          {trendData && (
            <div className="space-y-6">
              {/* Main Title */}
              <div className="mb-6">
                <h2 className="text-2xl font-bold mb-4 text-white">
                  Mobility and EV Startups<br/>in Europe
                </h2>
                <p className="text-gray-300 text-sm leading-relaxed">
                  A recent surge in startups focused on electric vehicles, autonomous driving, and advanced mobility solutions.
                </p>
              </div>

              {/* Key Insights */}
              <div className="space-y-4">
                <div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    An underpinings mult y focused on electric vehicles e CNd ediviCInG.
                  </p>
                </div>
                
                <div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    Autonomous driving technologies, such as AutonombuTesh and B...
                  </p>
                </div>
                
                <div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    Charging infrastructure startups like ChargeNow building networks across cities,
                  </p>
                </div>
                
                <div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    Sustainable transportation solutions, like EcoRide and UrbanMotion.
                  </p>
                </div>
                
                <div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    Funding rounds have exceeded =30M in the past year
                  </p>
                </div>
              </div>


            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 