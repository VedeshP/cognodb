import { useRef, useEffect, useState, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

export default function GraphVisualizer({ data }) {
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.offsetWidth,
        height: containerRef.current.offsetHeight
      });
    }
    
    const handleResize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const getNodeColor = (node) => {
    switch (node.label) {
      case 'Company': return '#3b82f6';
      case 'Investor': return '#8b5cf6';
      case 'Market': return '#10b981';
      case 'Region': return '#f59e0b';
      default: return '#94a3b8';
    }
  };

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
      <ForceGraph2D
        width={dimensions.width}
        height={dimensions.height}
        graphData={{ nodes: data.nodes, links: data.edges }}
        nodeLabel={(node) => `${node.label}: ${node.properties.name || node.id}`}
        nodeColor={getNodeColor}
        nodeRelSize={6}
        linkColor={() => 'rgba(255,255,255,0.2)'}
        linkWidth={1.5}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        backgroundColor="transparent"
      />
    </div>
  );
}
