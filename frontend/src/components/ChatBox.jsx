import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Loader2, Code2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './ChatBox.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export default function ChatBox({ setGraphData }) {
  const [messages, setMessages] = useState([
    { id: 1, type: 'bot', text: 'Hello! I am your Tech Ecosystem GraphRAG assistant. Ask me anything about startups, investors, or markets!' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { id: Date.now(), type: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat/`, {
        message: userMessage
      });

      const { answer, cypher_query, graph_data } = response.data;

      // Update graph
      if (graph_data && graph_data.nodes && graph_data.edges) {
        setGraphData(graph_data);
      }

      // Add bot response
      setMessages(prev => [
        ...prev,
        { id: Date.now(), type: 'bot', text: answer, cypher: cypher_query }
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        { id: Date.now(), type: 'error', text: 'Sorry, I encountered an error connecting to the database or LLM.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages-area">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`message-wrapper ${msg.type}`}
            >
              <div className="avatar">
                {msg.type === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="message-content">
                <p>{msg.text}</p>
                {msg.cypher && (
                  <div className="cypher-block">
                    <div className="cypher-header">
                      <Code2 size={14} /> <span>Generated Cypher</span>
                    </div>
                    <code>{msg.cypher}</code>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="message-wrapper bot">
               <div className="avatar"><Bot size={18} /></div>
               <div className="message-content loading">
                 <Loader2 size={18} className="spinner" /> 
                 <span>Traversing the graph...</span>
               </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about companies, investors..."
          disabled={isLoading}
        />
        <button type="submit" disabled={!input.trim() || isLoading}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
