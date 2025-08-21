export interface BrainNode {
  id: string;
  x: number;
  y: number;
  radius: number;
  label?: string;
  type: 'main' | 'secondary' | 'connection';
  connections: string[];
  data?: any;
}

export interface BrainConnection {
  source: string;
  target: string;
  strength: number;
}

export interface Startup {
  id: string;
  name: string;
  sector: string;
  funding: number;
  round: string;
  location: string;
  description: string;
  collaborations: string[];
}

export interface TrendData {
  id: string;
  title: string;
  description: string;
  growth: number;
  startups: Startup[];
} 