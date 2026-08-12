import { useState, useEffect } from 'react';
import { Database, Network, CheckCircle2, XCircle } from 'lucide-react';
import axios from 'axios';
import ChatBox from './components/ChatBox';
import GraphVisualizer from './components/GraphVisualizer';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

function App() {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const res = await axios.get(`${API_URL}/ping`);
        if (res.data.status === 'ok') setIsConnected(true);
      } catch (err) {
        setIsConnected(false);
      }
    };
    checkConnection();
    // Poll every 10s to keep status updated
    const interval = setInterval(checkConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <header className="header glass">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
          <Database size={32} color="var(--primary-color)" />
          <h1>Tech Ecosystem GraphRAG</h1>
        </div>
        <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? (
            <><CheckCircle2 size={16} color="#10b981" /> <span>Connected to app</span></>
          ) : (
            <><XCircle size={16} color="#ef4444" /> <span>Disconnected</span></>
          )}
        </div>
      </header>

      <main className="main-content">
        <section className="chat-section glass">
          <ChatBox setGraphData={setGraphData} />
        </section>

        <section className="graph-section glass">
          {graphData.nodes.length > 0 ? (
            <GraphVisualizer data={graphData} />
          ) : (
            <div className="graph-placeholder">
              <Network size={64} opacity={0.2} style={{ marginBottom: '1rem', display: 'block', margin: '0 auto' }} />
              <p>Ask a question to visualize the graph connections.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
