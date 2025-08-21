import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { BrainNode, BrainConnection } from '../types';

interface BrainVisualizationProps {
  width?: number;
  height?: number;
  interactive?: boolean;
  onNodeClick?: (node: BrainNode) => void;
  showLabels?: boolean;
}

const BrainVisualization: React.FC<BrainVisualizationProps> = ({
  width = 800,
  height = 600,
  interactive = true,
  onNodeClick,
  showLabels = false
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [nodes, setNodes] = useState<BrainNode[]>([]);
  const [connections, setConnections] = useState<BrainConnection[]>([]);

  // Generate brain-like network structure
  const generateBrainNetwork = useCallback(() => {
    const nodeCount = Math.min(180, Math.max(120, Math.floor((width * height) / 4000)));
    const newNodes: BrainNode[] = [];
    const newConnections: BrainConnection[] = [];

    // Create central hub nodes in brain-like structure
    const centralNodes = showLabels ? [
      { id: 'mobility', label: 'Mobility', type: 'main' as const },
      { id: 'funding', label: 'Funding', type: 'main' as const },
      { id: 'electric-vehicles', label: 'Electric Vehicles', type: 'main' as const },
      { id: 'startups', label: 'Startups', type: 'main' as const },
      { id: 'europe', label: 'Europe', type: 'main' as const },
    ] : [
      { id: 'mobility', label: 'Mobility', type: 'main' as const },
      { id: 'funding', label: 'Funding', type: 'main' as const },
      { id: 'startups', label: 'Startups', type: 'main' as const },
      { id: 'technology', label: 'Technology', type: 'main' as const },
      { id: 'europe', label: 'Europe', type: 'main' as const },
    ];

    // Create brain positioned higher on screen
    const brainRegions = [
      { centerX: width * 0.35, centerY: height * 0.3, size: 0.22 }, // Left lobe
      { centerX: width * 0.65, centerY: height * 0.3, size: 0.22 }, // Right lobe
      { centerX: width * 0.5, centerY: height * 0.25, size: 0.18 }, // Front lobe
      { centerX: width * 0.5, centerY: height * 0.4, size: 0.16 },  // Back lobe
      { centerX: width * 0.4, centerY: height * 0.2, size: 0.14 },  // Upper left
      { centerX: width * 0.6, centerY: height * 0.2, size: 0.14 },  // Upper right
    ];

    // Position central nodes in brain regions
    centralNodes.forEach((node, i) => {
      const region = brainRegions[i % brainRegions.length];
      const angle = Math.random() * 2 * Math.PI;
      const distance = Math.random() * Math.min(width, height) * region.size * 0.3;
      
      newNodes.push({
        ...node,
        x: region.centerX + Math.cos(angle) * distance,
        y: region.centerY + Math.sin(angle) * distance,
        radius: 12 + Math.random() * 3,
        connections: []
      });
    });

    // Generate very dense neural network filling the screen
    for (let i = centralNodes.length; i < nodeCount; i++) {
      let x, y;
      
      // 70% distributed in brain regions, 30% connecting tissue
      if (Math.random() > 0.3) {
        // Dense clustering in brain regions
        const region = brainRegions[Math.floor(Math.random() * brainRegions.length)];
        const angle = Math.random() * 2 * Math.PI;
        const distance = Math.random() * Math.min(width, height) * region.size * 0.8;
        x = region.centerX + Math.cos(angle) * distance;
        y = region.centerY + Math.sin(angle) * distance;
      } else {
        // Connecting tissue between regions
        const regionA = brainRegions[Math.floor(Math.random() * brainRegions.length)];
        const regionB = brainRegions[Math.floor(Math.random() * brainRegions.length)];
        const t = Math.random();
        x = regionA.centerX + t * (regionB.centerX - regionA.centerX) + (Math.random() - 0.5) * 80;
        y = regionA.centerY + t * (regionB.centerY - regionA.centerY) + (Math.random() - 0.5) * 80;
      }

             // Create organic brain shape - positioned higher
       const centerX = width * 0.5;
       const centerY = height * 0.3;
       const maxRadiusX = width * 0.32;
       const maxRadiusY = height * 0.25;
      
      // Create elliptical brain shape
      const normalizedX = (x - centerX) / maxRadiusX;
      const normalizedY = (y - centerY) / maxRadiusY;
      const distanceFromCenter = Math.sqrt(normalizedX * normalizedX + normalizedY * normalizedY);
      
      if (distanceFromCenter > 1) {
        x = centerX + (normalizedX / distanceFromCenter) * maxRadiusX * 0.95;
        y = centerY + (normalizedY / distanceFromCenter) * maxRadiusY * 0.95;
      }

      newNodes.push({
        id: `node-${i}`,
        x: x,
        y: y,
        radius: Math.random() * 2 + 0.8,
        type: Math.random() > 0.85 ? 'secondary' : 'connection',
        connections: []
      });
    }

    // Create optimized neural connections for better performance
    newNodes.forEach((node, i) => {
      // Reduced connections for better performance
      const connectionCount = node.type === 'main' ? 
        Math.floor(Math.random() * 8 + 6) :  // 6-14 connections for main nodes
        Math.floor(Math.random() * 5 + 3);   // 3-8 connections for others
      
      // Find nearest neighbors for more realistic connections
      const nearbyNodes = newNodes
        .map((target, index) => ({
          node: target,
          index: index,
          distance: Math.sqrt(
            Math.pow(node.x - target.x, 2) + Math.pow(node.y - target.y, 2)
          )
        }))
        .filter(item => item.index !== i)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, connectionCount * 2); // Get twice as many candidates

      // Connect to nearby nodes with preference for closer ones
      for (let j = 0; j < Math.min(connectionCount, nearbyNodes.length); j++) {
        const targetInfo = nearbyNodes[j];
        
        // Higher probability for closer nodes
        const probability = node.type === 'main' ? 0.8 : 
          (j < connectionCount * 0.6) ? 0.7 : 0.4;
          
        if (Math.random() < probability) {
          const maxDistance = node.type === 'main' ? 
            Math.min(width, height) * 0.4 : 
            Math.min(width, height) * 0.2;
            
          if (targetInfo.distance < maxDistance) {
            newConnections.push({
              source: node.id,
              target: targetInfo.node.id,
              strength: Math.max(0.2, 1 - (targetInfo.distance / maxDistance))
            });
            node.connections.push(targetInfo.node.id);
          }
        }
      }
    });

    setNodes(newNodes);
    setConnections(newConnections);
  }, [width, height]);

  useEffect(() => {
    generateBrainNetwork();
  }, [width, height, generateBrainNetwork]);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Create gradient and filter definitions
    const defs = svg.append('defs');
    
    // Main gradient
    const gradient = defs.append('linearGradient')
      .attr('id', 'brain-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '100%');

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#00b4d8');

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#90e0ef');
    
    // Glow filter
    const filter = defs.append('filter')
      .attr('id', 'glow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    filter.append('feGaussianBlur')
      .attr('stdDeviation', '3')
      .attr('result', 'coloredBlur');

    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Draw connections with animated effects
    const connectionGroup = svg.append('g').attr('class', 'connections');
    
    connections.forEach((connection, index) => {
      const sourceNode = nodes.find(n => n.id === connection.source);
      const targetNode = nodes.find(n => n.id === connection.target);
      
      if (sourceNode && targetNode) {
        const line = connectionGroup.append('line')
          .attr('x1', sourceNode.x)
          .attr('y1', sourceNode.y)
          .attr('x2', targetNode.x)
          .attr('y2', targetNode.y)
          .attr('class', 'connection-line')
          .style('opacity', 0)
          .style('stroke', '#00b4d8')
          .style('stroke-width', 1);

        // Animate line appearance (optimized)
        line.transition()
          .delay(index * 3)
          .duration(400)
          .style('opacity', connection.strength * 0.3);

        // Flowing effects disabled for performance
      }
    });

    // Draw nodes
    const nodeGroup = svg.append('g').attr('class', 'nodes');
    
    nodes.forEach((node, index) => {
      const nodeElement = nodeGroup.append('circle')
        .attr('cx', node.x)
        .attr('cy', node.y)
        .attr('r', 0)
        .attr('class', 'neuron-node')
        .style('fill', node.type === 'main' ? 'url(#brain-gradient)' : '#00b4d8')
        .style('opacity', 0)
        .style('filter', node.type === 'main' ? 'url(#glow)' : 'none');

      // Animate node appearance (optimized)
      nodeElement.transition()
        .delay(index * 4)
        .duration(400)
        .attr('r', node.radius)
        .style('opacity', node.type === 'main' ? 1 : 0.8);

      if (interactive) {
        nodeElement
          .style('cursor', 'pointer')
          .on('click', () => onNodeClick?.(node))
          .on('mouseover', function() {
            d3.select(this)
              .transition()
              .duration(200)
              .attr('r', node.radius * 1.5)
              .style('opacity', 1)
              .style('filter', 'url(#glow)');
          })
          .on('mouseout', function() {
            d3.select(this)
              .transition()
              .duration(200)
              .attr('r', node.radius)
              .style('opacity', node.type === 'main' ? 1 : 0.7)
              .style('filter', node.type === 'main' ? 'url(#glow)' : 'none');
          });
      }

      // Add labels for main nodes
      if (node.label && node.type === 'main') {
        const textElement = nodeGroup.append('text')
          .attr('x', node.x)
          .attr('y', node.y + node.radius + 20)
          .attr('text-anchor', 'middle')
          .attr('class', showLabels ? 'text-sm font-medium text-brain-cyan' : 'text-xs font-medium text-brain-cyan')
          .style('opacity', 0)
          .style('filter', 'url(#glow)')
          .style('pointer-events', 'none')
          .text(node.label);

        // Animate text appearance
        textElement.transition()
          .delay(index * 8 + 800)
          .duration(500)
          .style('opacity', showLabels ? 1 : 0.9);
      }
    });

    // Simplified pulsing animation (performance optimized)
    const pulse = () => {
      svg.selectAll('.neuron-node')
        .filter(function(d, i) { 
          const node = nodes[i];
          return node && node.type === 'main';
        })
        .transition()
        .duration(4000)
        .style('opacity', 0.9)
        .transition()
        .duration(4000)
        .style('opacity', 1)
        .on('end', pulse);
    };
    
    setTimeout(pulse, 3000);

  }, [nodes, connections, interactive, onNodeClick]);

  return (
    <div className="brain-visualization relative">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="overflow-visible"
      />
    </div>
  );
};

export default BrainVisualization; 