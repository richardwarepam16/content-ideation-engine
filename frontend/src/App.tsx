import React, { useState, useEffect } from 'react';
import { Sparkles, TrendingUp, Users, Lightbulb, Play, Loader2, CheckCircle2 } from 'lucide-react';
import { useIdeationSocket } from './hooks/useIdeationSocket';
import 'reactflow/dist/style.css'; // This import is not strictly needed anymore, but keeping it for now

// Define the shape of the data you expect from the WebSocket
interface AgentMessage {
  agent_name: string;
  message: string;
}

interface ContentIdea {
  id: string;
  format: string;
  icon: string; // Assuming the backend sends an icon or we map it
  title: string;
  description: string;
  structure: string;
  keywords: string[];
  confidence: number;
  trending: boolean;
  estimated_engagement: string;
}

interface FinalResult {
  ideas: ContentIdea[];
}

const agentNamesMap = {
  researcher: 'Trend Researcher',
  analyst: 'Audience Analyst',
  writer: 'Creative Writer'
};

const getAgentIcon = (agentId: string) => {
  const icons = {
    researcher: <TrendingUp className="w-5 h-5" />,
    analyst: <Users className="w-5 h-5" />,
    writer: <Lightbulb className="w-5 h-5" />
  };
  return icons[agentId as keyof typeof icons];
};

const getAgentColor = (state: string) => {
  const colors = {
    pending: 'border-gray-200 bg-white text-gray-400',
    running: 'border-blue-300 bg-blue-100 text-blue-600 animate-pulse',
    completed: 'border-green-300 bg-green-100 text-green-600',
    error: 'border-red-300 bg-red-100 text-red-600'
  };
  return colors[state] || colors.pending;
};

const App: React.FC = () => {
  const [industry, setIndustry] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [contentTypes, setContentTypes] = useState({
    blog: true,
    video: true,
    social: true
  });

  const { isConnected, activeAgent, finalResult, error, startIdeation } = useIdeationSocket();
  const [isRunning, setIsRunning] = useState(false);
  
  const [agentStates, setAgentStates] = useState({
    researcher: 'pending',
    analyst: 'pending',
    writer: 'pending'
  });

  // Effect to update isRunning state based on WebSocket activity
  useEffect(() => {
    if (activeAgent) {
      setIsRunning(true);
      setAgentStates(prev => ({ ...prev, [activeAgent]: 'running' }));
    } else if (!finalResult && !error) {
      // Not running, no final result, no error -> initial state or reset
      setIsRunning(false);
      setAgentStates({ researcher: 'pending', analyst: 'pending', writer: 'pending' });
    }
  }, [activeAgent, finalResult, error]);

  // Effect to mark agent as completed or error
  useEffect(() => {
    if (activeAgent) {
      Object.keys(agentStates).forEach(agentId => {
        if (agentId !== activeAgent && agentStates[agentId] === 'running') {
          setAgentStates(prev => ({ ...prev, [agentId]: 'completed' }));
        }
      });
    }
  }, [activeAgent]);

  // Handle final result or error
  useEffect(() => {
    if (finalResult) {
      Object.keys(agentStates).forEach(agentId => {
        if (agentStates[agentId] === 'running') {
          setAgentStates(prev => ({ ...prev, [agentId]: 'completed' }));
        }
      });
      setIsRunning(false);
    } else if (error) {
      Object.keys(agentStates).forEach(agentId => {
        if (agentStates[agentId] === 'running') {
          setAgentStates(prev => ({ ...prev, [agentId]: 'error' }));
        }
      });
      setIsRunning(false);
    }
  }, [finalResult, error]);


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!industry.trim() || !targetAudience.trim() || !isConnected || isRunning) return;

    // Reset states for a new run
    setAgentStates({ researcher: 'pending', analyst: 'pending', writer: 'pending' });
    
    const selectedContentTypes = Object.keys(contentTypes).filter(k => contentTypes[k]);

    startIdeation({
      industry,
      target_audience: targetAudience,
      content_types: selectedContentTypes,
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans text-gray-900">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm mb-4 border border-gray-100">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <span className="text-sm font-semibold text-gray-700">Multi-Agent AI System</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Content Ideation Engine
          </h1>
          <p className="text-lg text-gray-600">
            LangGraph + a2a Protocol • 3 Specialized Agents • Infinite Ideas
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column: Configuration */}
          <div className="lg:col-span-1 space-y-8">
            {/* Input Form */}
            <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
              <h2 className="text-xl font-semibold mb-5 text-gray-800">Configuration</h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Industry/Niche
                  </label>
                  <input
                    type="text"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    placeholder="e.g., Technology, Marketing, Finance"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={isRunning || !isConnected}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Audience
                  </label>
                  <input
                    type="text"
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                    placeholder="e.g., B2B Founders, Content Creators"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={isRunning || !isConnected}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content Formats
                  </label>
                  <div className="space-y-2">
                    {Object.keys(contentTypes).map(type => (
                      <label key={type} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={contentTypes[type as keyof typeof contentTypes]}
                          onChange={(e) => setContentTypes(prev => ({
                            ...prev,
                            [type]: e.target.checked
                          }))}
                          className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                          disabled={isRunning || !isConnected}
                        />
                        <span className="text-sm text-gray-700 capitalize">{type} Posts</span>
                      </label>
                    ))}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isRunning || !industry || !targetAudience || !isConnected}
                  className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isRunning ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      {isConnected ? 'Generate Ideas' : 'Connecting...'}
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Agent Status */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Agent Pipeline</h2>
              
              <div className="space-y-3">
                {['researcher', 'analyst', 'writer'].map((agentId, idx) => {
                  
                  const agentState = agentStates[agentId as keyof typeof agentStates];

                  return (
                    <div
                      key={agentId}
                      className={`p-4 rounded-lg border-2 transition-all ${getAgentColor(agentState)}`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white">
                            {getAgentIcon(agentId)}
                          </div>
                          <div>
                            <div className="font-semibold text-sm">{agentNamesMap[agentId as keyof typeof agentNamesMap]}</div>
                            <div className="text-xs opacity-75">Agent {idx + 1}</div>
                          </div>
                        </div>
                        {agentState === 'completed' && (
                          <CheckCircle2 className="w-5 h-5 text-green-600" />
                        )}
                        {agentState === 'running' && (
                          <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                        )}
                        {agentState === 'error' && (
                          <span className="text-red-600">Error!</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Results & Logs */}
          <div className="lg:col-span-2 space-y-6">
            {/* Activity Log - NOTE: This requires backend to stream detailed logs */}
            {/* {
              agentLogs.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold mb-4 text-gray-800">
                  Agent Communication (a2a Protocol)
                </h2>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {agentLogs.map((log, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-gray-50 rounded-lg text-sm border-l-4 border-purple-400"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-purple-700 capitalize">
                          {log.agent}
                        </span>
                        <span className="text-xs text-gray-500">{
                            log.timestamp
                          }</span>
                      </div>
                      <div className="text-gray-700">{log.message}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
             */}

            {/* Results */}
            {finalResult && finalResult.ideas && finalResult.ideas.length > 0 ? (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-800">
                    Generated Content Ideas
                  </h2>
                  <span className="text-sm text-gray-600">
                    {finalResult.ideas.length} ideas
                  </span>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  {finalResult.ideas.map((idea) => (
                    <div
                      key={idea.id}
                      className="p-5 border-2 border-gray-200 rounded-xl hover:border-purple-400 hover:shadow-md transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {idea.icon && <span className="text-2xl">{idea.icon}</span>}
                          <span className="text-sm font-semibold text-purple-600">
                            {idea.format}
                          </span>
                        </div>
                        {idea.trending && (
                          <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full font-medium">
                            🔥 Trending
                          </span>
                        )}
                      </div>
                      
                      <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">
                        {idea.title}
                      </h3>
                      
                      <p className="text-sm text-gray-600 mb-3 line-clamp-3">
                        {idea.description}
                      </p>
                      
                      <div className="pt-3 border-t border-gray-100">
                        <div className="text-xs text-gray-500 mb-2">
                          <strong>Structure:</strong> {idea.structure}
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-gradient-to-r from-purple-500 to-indigo-500 h-2 rounded-full"
                              style={{ width: `${idea.confidence}%` }}
                            />
                          </div>
                          <span className="text-xs font-semibold text-gray-600">
                            {idea.confidence}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : error ? (
                <div className="bg-white rounded-xl shadow-lg p-12 text-center text-red-500">
                    <p className="font-semibold text-lg">Error during ideation:</p>
                    <p>{error}</p>
                </div>
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Ready to Generate Ideas
                </h3>
                <p className="text-gray-500">
                  Configure your parameters and click "Generate Ideas" to start the multi-agent pipeline
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Architecture Info */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">
            System Architecture
          </h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="font-semibold text-purple-900 mb-2">LangGraph Orchestration</div>
              <div className="text-purple-700">
                State machine managing agent execution flow, handoffs, and error recovery
              </div>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="font-semibold text-blue-900 mb-2">a2a Protocol</div>
              <div className="text-blue-700">
                Structured agent-to-agent communication enabling context sharing and refinement
              
              </div>
            </div>
            <div className="p-4 bg-indigo-50 rounded-lg">
              <div className="font-semibold text-indigo-900 mb-2">Claude API Integration</div>
              <div className="text-indigo-700">
                Each agent powered by Claude for reasoning, analysis, and creative generation
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;