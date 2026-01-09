import { useState, useEffect, useCallback } from 'react';

// Define the shape of the data you expect from the WebSocket
interface AgentMessage {
  agent_name: string;
  message: string;
}

interface FinalResult {
  ideas: any[]; // Define a proper type for ideas later
}

type SocketMessage = 
  | { type: 'status'; payload: string }
  | { type: 'agent_update'; payload: AgentMessage }
  | { type: 'final_result'; payload: FinalResult }
  | { type: 'error'; payload: string };

const WEBSOCKET_URL = 'ws://localhost:8000/ws/ideate';

export const useIdeationSocket = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [finalResult, setFinalResult] = useState<FinalResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WEBSOCKET_URL);
    setSocket(ws);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      setError('WebSocket connection failed.');
    };

    ws.onmessage = (event) => {
      try {
        const message: SocketMessage = JSON.parse(event.data);

        switch (message.type) {
          case 'status':
            console.log('Status:', message.payload);
            break;
          case 'agent_update':
            setActiveAgent(message.payload.agent_name);
            break;
          case 'final_result':
            setFinalResult(message.payload);
            setActiveAgent(null); // Reset active agent on completion
            break;
          case 'error':
            setError(message.payload);
            setActiveAgent(null);
            break;
        }
      } catch (e) {
        console.error('Failed to parse socket message:', event.data);
      }
    };

    // Cleanup on unmount
    return () => {
      ws.close();
    };
  }, []);

  const startIdeation = useCallback((requestData: { industry: string; target_audience: string; content_types: string[] }) => {
    if (socket && isConnected) {
      // Reset state for new request
      setActiveAgent(null);
      setFinalResult(null);
      setError(null);
      
      socket.send(JSON.stringify(requestData));
    } else {
      console.error('WebSocket is not connected.');
      setError('Cannot start ideation: WebSocket is not connected.');
    }
  }, [socket, isConnected]);

  return { isConnected, activeAgent, finalResult, error, startIdeation };
};
