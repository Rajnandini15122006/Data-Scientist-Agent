// import React, { useState, useEffect, useRef } from 'react';
// // FIX: Corrected the icon name from 'FaCogs' to the modern 'FaGears' to resolve the import error.
// import { FaRobot, FaUpload, FaPaperPlane, FaSpinner, FaDownload, FaGears, FaChartPie } from 'react-icons/fa6';

// // --- Main App Component ---
// function App() {
//   const [messages, setMessages] = useState([]);
//   const [userInput, setUserInput] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const [conversationState, setConversationState] = useState({ next_state: 'AWAITING_FILE' });
//   const [choices, setChoices] = useState([]);
//   const fileInputRef = useRef(null);
//   const chatWindowRef = useRef(null);

//   // API Backend URL
//   const API_URL = 'http://localhost:8000';

//   useEffect(() => {
//     // Greet the user on initial load
//     setMessages([{ sender: 'agent', text: "Hello! I'm ready to analyze your data. Please upload a CSV or Excel file to get started." }]);
//   }, []);

//   useEffect(() => {
//     // Auto-scroll to the latest message
//     if (chatWindowRef.current) {
//       chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
//     }
//   }, [messages]);

//   const addMessage = (sender, text, isHtml = false) => {
//     setMessages(prev => [...prev, { sender, text, isHtml }]);
//   };

//   const handleFileUpload = async (event) => {
//     const file = event.target.files[0];
//     if (!file) return;

//     addMessage('user', `Uploaded: ${file.name}`);
//     setIsLoading(true);
//     setConversationState({ next_state: 'ANALYZING' });

//     const formData = new FormData();
//     formData.append('file', file);

//     try {
//       const response = await fetch(`${API_URL}/start_analysis`, {
//         method: 'POST',
//         body: formData,
//       });
//       const data = await response.json();

//       if (response.ok) {
//         data.agent_messages.forEach(msg => addMessage('agent', msg, true));
//         setConversationState({ next_state: data.next_state });
//       } else {
//         addMessage('agent', `Error from backend: ${data.error || 'Unknown error'}`);
//         setConversationState({ next_state: 'AWAITING_FILE' });
//       }
//     } catch (error) {
//       addMessage('agent', `Network Error: Could not connect to the backend. Please ensure it's running on ${API_URL}.`);
//       setConversationState({ next_state: 'AWAITING_FILE' });
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleUserResponse = async (text) => {
//     addMessage('user', text);
//     setIsLoading(true);

//     const endpoint = conversationState.next_state === 'AWAITING_OUTPUT_CHOICE'
//         ? `${API_URL}/generate_output`
//         : `${API_URL}/continue_conversation`;

//     try {
//         const response = await fetch(endpoint, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ message: text, state: conversationState })
//         });

//         if (endpoint.includes('generate_output')) {
//             if (response.ok) {
//                 const blob = await response.blob();
//                 const url = window.URL.createObjectURL(blob);
//                 const contentDisposition = response.headers.get('content-disposition');
//                 let fileName = 'analysis_output';
//                 if (contentDisposition) {
//                     const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
//                     if (fileNameMatch && fileNameMatch.length === 2) fileName = fileNameMatch[1];
//                 }

//                 addMessage('agent', `Your file is ready!`);
//                 setMessages(prev => [...prev, { sender: 'agent', isDownload: true, link: url, name: fileName }]);
//                 setConversationState({ next_state: 'COMPLETE' });

//             } else {
//                  const data = await response.json();
//                  addMessage('agent', `Error: ${data.error || 'Failed to generate file.'}`);
//             }
//         } else {
//             const data = await response.json();
//             if (response.ok) {
//                 data.agent_messages.forEach(msg => addMessage('agent', msg, true));
//                 setConversationState({ next_state: data.next_state });
//                 setChoices(data.choices || []);
//             } else {
//                  addMessage('agent', `Error: ${data.error || 'An unknown error occurred.'}`);
//             }
//         }
//     } catch (error) {
//         addMessage('agent', `Network Error: Could not connect to the backend.`);
//     } finally {
//         setIsLoading(false);
//         setUserInput('');
//     }
//   };

//   const renderInput = () => {
//     if (isLoading) {
//       return <div className="flex justify-center items-center p-2"><FaSpinner className="animate-spin text-slate-500" /><p className="ml-2 text-slate-500 italic">Agent is thinking...</p></div>;
//     }

//     switch (conversationState.next_state) {
//       case 'AWAITING_FILE':
//         return (
//           <div className="flex items-center justify-center">
//             <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".csv,.xlsx,.xls" />
//             <button onClick={() => fileInputRef.current.click()} className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md flex items-center transition-all">
//               <FaUpload className="mr-2" /> Choose a File
//             </button>
//           </div>
//         );
//       case 'AWAITING_TARGET':
//         return (
//           <div className="flex">
//             <input type="text" value={userInput} onChange={(e) => setUserInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleUserResponse(userInput)} className="flex-grow border rounded-l-lg p-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="Enter the target column name..." />
//             <button onClick={() => handleUserResponse(userInput)} className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-r-lg"><FaPaperPlane /></button>
//           </div>
//         );
//       case 'AWAITING_OUTPUT_CHOICE':
//         return (
//            <div className="flex justify-center gap-4">
//                 {choices.map(choice => (
//                     <button key={choice} onClick={() => handleUserResponse(choice)} className="bg-slate-200 hover:bg-slate-300 text-slate-700 font-semibold py-2 px-4 rounded-lg transition-all">
//                         {choice.charAt(0).toUpperCase() + choice.slice(1)}
//                     </button>
//                 ))}
//             </div>
//         );
//       case 'COMPLETE':
//         return <div className="text-center text-green-600 font-semibold p-2"><i className="fas fa-check-circle mr-2"></i>Analysis Complete!</div>;
//       default:
//         return null;
//     }
//   };

//   return (
//     <div className="w-full max-w-5xl bg-white rounded-2xl shadow-2xl flex flex-col md:flex-row overflow-hidden" style={{ height: '95vh' }}>
//       <div className="w-full md:w-1/3 bg-slate-800 p-8 text-white flex flex-col">
//         <div className="flex items-center mb-6">
//           <FaRobot className="text-3xl text-indigo-400" />
//           <h1 className="text-2xl font-bold ml-4">AI Data Scientist</h1>
//         </div>
//         <p className="text-slate-300 mb-6 font-light text-sm">
//           Welcome! I am an autonomous AI agent designed to help you analyze your data. I will guide you through a simple conversation to understand your goals and will generate a professional-grade analysis for you.
//         </p>
//          <div className="mt-8 space-y-4 text-sm">
//              <div className="flex items-start"><FaUpload className="text-indigo-400 mt-1 mr-3 flex-shrink-0" /><span>Start by uploading any CSV or Excel file.</span></div>
//              <div className="flex items-start"><FaPaperPlane className="text-indigo-400 mt-1 mr-3 flex-shrink-0" /><span>Answer a few simple questions to clarify your goal.</span></div>
//              <div className="flex items-start"><FaGears className="text-indigo-400 mt-1 mr-3 flex-shrink-0" /><span>Choose your desired output.</span></div>
//              <div className="flex items-start"><FaChartPie className="text-indigo-400 mt-1 mr-3 flex-shrink-0" /><span>Receive a beautiful, data-driven deliverable.</span></div>
//          </div>
//         <div className="mt-auto"><p className="text-xs text-slate-400">Full-Stack Agent Architecture</p></div>
//       </div>
//       <div className="w-full md:w-2/3 flex flex-col p-6 bg-slate-50">
//         <div ref={chatWindowRef} className="flex-grow overflow-y-auto pr-4 mb-4 space-y-4 flex flex-col">
//           {messages.map((msg, index) => (
//             <div key={index} className={`p-4 max-w-md w-fit rounded-2xl shadow ${msg.sender === 'agent' ? 'bg-slate-200 text-slate-800 self-start rounded-bl-none' : 'bg-indigo-600 text-white self-end rounded-br-none'}`}>
//               {msg.isHtml ? <div dangerouslySetInnerHTML={{ __html: msg.text }} /> : msg.isDownload ? <a href={msg.link} download={msg.name} className="flex items-center font-semibold text-indigo-100 hover:text-white"><FaDownload className="mr-2" /> Download {msg.name}</a> : msg.text}
//             </div>
//           ))}
//         </div>
//         <div className="mt-auto border-t border-slate-200 pt-4">
//           {renderInput()}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App;

import React, { useState, useEffect, useRef } from "react";
import {
  Bot,
  Upload,
  Send,
  Loader2,
  Download,
  BarChart3,
  Lightbulb,
  Brain,
  CheckCircle,
} from "lucide-react";

const API_URL = "http://localhost:8000";

function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentState, setCurrentState] = useState("initial");
  const [analysis, setAnalysis] = useState(null);
  const [preview, setPreview] = useState(null);
  const [choices, setChoices] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(null);
  const [modelComparison, setModelComparison] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [showSessionHistory, setShowSessionHistory] = useState(false);
  const [savedSessions, setSavedSessions] = useState([]);

  const fileInputRef = useRef(null);
  const chatWindowRef = useRef(null);

  // Load saved session from localStorage on mount
  useEffect(() => {
    let hasInitialized = false;
    
    const savedSession = localStorage.getItem('aiDataScientistSession');
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession);
        const sessionAge = Date.now() - parsed.timestamp;
        
        // Only restore if session is less than 24 hours old
        if (sessionAge < 24 * 60 * 60 * 1000 && parsed.messages && parsed.messages.length > 0) {
          setMessages(parsed.messages);
          setSessionId(parsed.sessionId || null);
          setCurrentState(parsed.currentState || "initial");
          setAnalysis(parsed.analysis || null);
          setPreview(parsed.preview || null);
          setModelComparison(parsed.modelComparison || null);
          hasInitialized = true;
          
          // Add welcome back message only if not already in messages
          const hasWelcomeBack = parsed.messages.some(m => m.text.includes("Welcome back"));
          if (!hasWelcomeBack) {
            setMessages(prev => [...prev, {
              sender: "agent",
              text: "👋 Welcome back! I've restored your previous session.",
              timestamp: new Date().toLocaleTimeString()
            }]);
          }
          return;
        } else {
          // Clear old session
          localStorage.removeItem('aiDataScientistSession');
        }
      } catch (error) {
        console.error("Failed to restore session:", error);
        localStorage.removeItem('aiDataScientistSession');
      }
    }
    
    // Start fresh session only if not initialized
    if (!hasInitialized) {
      setMessages([{
        sender: "agent",
        text: "👋 Hello! I'm your AI Data Scientist. Upload a CSV or Excel file to begin your analysis journey!",
        timestamp: new Date().toLocaleTimeString()
      }]);
    }
  }, []);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages]);

  // Auto-save session to localStorage whenever important state changes
  useEffect(() => {
    if (messages.length > 1) { // Don't save initial greeting only
      const sessionData = {
        messages,
        sessionId,
        currentState,
        analysis,
        preview,
        modelComparison,
        timestamp: Date.now()
      };
      localStorage.setItem('aiDataScientistSession', JSON.stringify(sessionData));
    }
  }, [messages, sessionId, currentState, analysis, preview, modelComparison]);

  const addMessage = (sender, text, data = null) => {
    setMessages((prev) => [
      ...prev,
      {
        sender,
        text,
        data,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
  };

  const exportChatHistory = () => {
    const chatText = messages.map(msg => {
      const sender = msg.sender === 'agent' ? 'AI Assistant' : 'You';
      return `[${msg.timestamp}] ${sender}: ${msg.text}`;
    }).join('\n\n');

    const fullExport = `AI Data Scientist - Chat History
Generated: ${new Date().toLocaleString()}
Session ID: ${sessionId || 'N/A'}
Current State: ${currentState}

${'='.repeat(60)}

${chatText}

${'='.repeat(60)}

Session Summary:
- Total Messages: ${messages.length}
- Analysis Complete: ${analysis ? 'Yes' : 'No'}
- Model Comparison: ${modelComparison ? 'Yes' : 'No'}
`;

    const blob = new Blob([fullExport], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-history-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    addMessage("agent", "✅ Chat history exported successfully!");
  };

  const clearSession = () => {
    if (window.confirm("Are you sure you want to clear the current session? This cannot be undone.")) {
      localStorage.removeItem('aiDataScientistSession');
      setMessages([{
        sender: "agent",
        text: "🔄 Session cleared! Upload a new file to start fresh.",
        timestamp: new Date().toLocaleTimeString()
      }]);
      setSessionId(null);
      setCurrentState("initial");
      setAnalysis(null);
      setPreview(null);
      setModelComparison(null);
      setChoices([]);
      setProgress(null);
      setIsComparing(false);
    }
  };

  const saveCurrentSession = () => {
    if (!sessionId || messages.length < 2) {
      addMessage("agent", "⚠️ No active session to save.");
      return;
    }

    const sessionName = prompt("Enter a name for this session:", `Analysis ${new Date().toLocaleDateString()}`);
    if (!sessionName) return;

    // Extract dataset name from messages if available
    const uploadMessage = messages.find(m => m.text.includes('Uploaded:'));
    const datasetName = uploadMessage ? uploadMessage.text.replace('📄 Uploaded: ', '').trim() : 'Unknown Dataset';

    const sessionData = {
      name: sessionName,
      sessionId,
      messages,
      currentState,
      analysis,
      preview,
      modelComparison,
      timestamp: Date.now(),
      date: new Date().toLocaleString(),
      datasetName,
      targetColumn: analysis?.potential_targets?.[0] || 'N/A',
      bestModel: modelComparison?.best_model || 'N/A',
      accuracy: modelComparison?.best_accuracy || preview?.accuracy || 'N/A'
    };

    // Get existing saved sessions
    const existing = JSON.parse(localStorage.getItem('aiDataScientist_savedSessions') || '[]');
    existing.push(sessionData);
    
    // Keep only last 15 sessions
    const limited = existing.slice(-15);
    localStorage.setItem('aiDataScientist_savedSessions', JSON.stringify(limited));
    setSavedSessions(limited);

    addMessage("agent", `✅ Session "${sessionName}" saved successfully!`);
  };

  const loadSavedSessions = () => {
    const saved = JSON.parse(localStorage.getItem('aiDataScientist_savedSessions') || '[]');
    setSavedSessions(saved.reverse()); // Show newest first
    setShowSessionHistory(true);
  };

  const restoreSession = (session) => {
    setMessages(session.messages);
    setSessionId(session.sessionId);
    setCurrentState(session.currentState);
    setAnalysis(session.analysis);
    setPreview(session.preview);
    setModelComparison(session.modelComparison);
    setShowSessionHistory(false);
    
    addMessage("agent", `🔄 Restored session: "${session.name}"`);
  };

  const deleteSavedSession = (index) => {
    const updated = savedSessions.filter((_, i) => i !== index);
    localStorage.setItem('aiDataScientist_savedSessions', JSON.stringify(updated.reverse()));
    setSavedSessions(updated);
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    const validTypes = [".csv", ".xlsx", ".xls"];
    const fileExt = "." + file.name.split(".").pop().toLowerCase();

    if (!validTypes.includes(fileExt)) {
      addMessage(
        "agent",
        "❌ Invalid file type. Please upload a CSV or Excel file."
      );
      return;
    }

    addMessage("user", `📄 Uploaded: ${file.name}`);
    setIsLoading(true);
    setCurrentState("uploading");
    
    // Reset model comparison for new upload
    setModelComparison(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Upload response:", data);

        // FIXED: Set session ID and state together
        setSessionId(data.session_id);

        // FIXED: Check if we have analysis data
        if (data.analysis && data.state === "analyzed") {
          setAnalysis(data.analysis);
          setCurrentState("analyzed");

          addMessage("agent", data.message, {
            type: "analysis",
            analysis: data.analysis,
          });
        } else {
          // If no analysis yet, set the state from backend
          setCurrentState(data.state || "initial");
          addMessage("agent", data.message || "✅ File uploaded successfully!");
        }
      } else {
        addMessage("agent", `❌ Error: ${data.error || "Upload failed"}`);
        setCurrentState("initial");
      }
    } catch (error) {
      addMessage(
        "agent",
        `❌ Network Error: Could not connect to backend at ${API_URL}. Make sure the backend is running.`
      );
      console.error("Upload error:", error);
      setCurrentState("initial");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileInputChange = (event) => {
    const file = event.target.files[0];
    if (file) handleFileUpload(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleSendMessage = async (text = userInput) => {
    if (!text.trim()) return;

    if (!sessionId) {
      addMessage("agent", "❌ Please upload a file first to start a session.");
      return;
    }

    addMessage("user", text);
    setUserInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
        }),
      });

      const data = await response.json();
      console.log("Chat response:", data);

      if (response.ok) {
        console.log("Chat response state:", data.state);
        console.log("Model comparison exists:", !!modelComparison);
        setCurrentState(data.state);

        if (data.state === "target_set") {
          setPreview(data.preview);
          setChoices(data.choices || []);
          console.log("Setting choices:", data.choices);
          addMessage("agent", data.response, {
            type: "preview",
            preview: data.preview,
          });
        } else if (data.state === "generating") {
          addMessage("agent", data.response);
          setTimeout(() => generateOutput(), 1500);
        } else {
          addMessage("agent", data.response);
        }
      } else {
        addMessage("agent", `❌ Error: ${data.error || "Request failed"}`);
      }
    } catch (error) {
      addMessage("agent", "❌ Network Error: Could not connect to backend.");
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const compareModels = async () => {
    if (!sessionId) {
      addMessage("agent", "❌ No active session. Please upload a file first.");
      return;
    }

    setIsComparing(true);
    addMessage("agent", "🤖 Comparing 6 different ML models... This may take a minute.");

    try {
      const response = await fetch(`${API_URL}/api/compare-models`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setModelComparison(data.comparison);
        addMessage("agent", "✅ Model comparison complete!", {
          type: "model_comparison",
          comparison: data.comparison,
        });
      } else {
        addMessage(
          "agent",
          `❌ Error: ${data.error || "Failed to compare models"}`
        );
      }
    } catch (error) {
      addMessage("agent", "❌ Network Error: Could not compare models.");
      console.error("Model comparison error:", error);
    } finally {
      setIsComparing(false);
    }
  };

  const generateOutput = async () => {
    if (!sessionId) {
      addMessage("agent", "❌ No active session. Please upload a file first.");
      return;
    }

    setIsLoading(true);
    setProgress({ percentage: 0, message: "Starting...", step: "initializing" });
    addMessage("agent", "⏳ Generating your file... This may take a moment.");

    // Start listening to progress updates via SSE
    const eventSource = new EventSource(`${API_URL}/api/progress/${sessionId}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data);
      console.log("Progress update:", data);
    };

    eventSource.addEventListener("progress", (event) => {
      const data = JSON.parse(event.data);
      setProgress(data);
    });

    eventSource.addEventListener("complete", (event) => {
      console.log("Generation complete!");
      eventSource.close();
    });

    eventSource.onerror = (error) => {
      console.error("SSE Error:", error);
      eventSource.close();
    };

    try {
      const response = await fetch(`${API_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const contentDisposition = response.headers.get("content-disposition");
        let fileName = "analysis_output";

        if (contentDisposition) {
          const fileNameMatch = contentDisposition.match(
            /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
          );
          if (fileNameMatch && fileNameMatch[1]) {
            fileName = fileNameMatch[1].replace(/['"]/g, "");
          }
        }

        const url = window.URL.createObjectURL(blob);

        addMessage("agent", "✅ Your file is ready!", {
          type: "download",
          url: url,
          filename: fileName,
        });

        setCurrentState("completed");
        setProgress(null);
      } else {
        const data = await response.json();
        addMessage(
          "agent",
          `❌ Error: ${data.error || "Failed to generate file"}`
        );
        setProgress(null);
      }
    } catch (error) {
      addMessage("agent", "❌ Network Error: Could not generate file.");
      console.error("Generate error:", error);
      setProgress(null);
    } finally {
      setIsLoading(false);
      eventSource.close();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderAnalysisCard = (analysisData) => {
    if (!analysisData) return null;

    return (
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4 mt-2 border border-indigo-200">
        <div className="flex items-center mb-3">
          <BarChart3 className="text-indigo-600 text-xl mr-2" />
          <h3 className="font-bold text-gray-800">Dataset Overview</h3>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-2xl font-bold text-indigo-600">
              {analysisData.stats.rows.toLocaleString()}
            </div>
            <div className="text-xs text-gray-600">Total Rows</div>
          </div>
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-2xl font-bold text-purple-600">
              {analysisData.stats.columns}
            </div>
            <div className="text-xs text-gray-600">Columns</div>
          </div>
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-2xl font-bold text-green-600">
              {analysisData.stats.numerical_features}
            </div>
            <div className="text-xs text-gray-600">Numerical</div>
          </div>
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-2xl font-bold text-orange-600">
              {analysisData.stats.categorical_features}
            </div>
            <div className="text-xs text-gray-600">Categorical</div>
          </div>
        </div>

        {analysisData.suggestions && analysisData.suggestions.length > 0 && (
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="flex items-center mb-2">
              <Lightbulb className="text-yellow-500 mr-2" />
              <span className="font-semibold text-sm text-gray-700">
                Smart Insights
              </span>
            </div>
            <ul className="space-y-1 text-xs text-gray-600">
              {analysisData.suggestions.slice(0, 3).map((suggestion, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="mr-1">•</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysisData.potential_targets &&
          analysisData.potential_targets.length > 0 && (
            <div className="mt-3 p-2 bg-indigo-100 rounded-lg">
              <div className="text-xs font-semibold text-indigo-800 mb-1">
                Recommended Targets:
              </div>
              <div className="flex flex-wrap gap-1">
                {analysisData.potential_targets.slice(0, 5).map((col, idx) => (
                  <span
                    key={idx}
                    className="bg-indigo-200 text-indigo-800 text-xs px-2 py-1 rounded-full"
                  >
                    {col}
                  </span>
                ))}
              </div>
            </div>
          )}
      </div>
    );
  };

  const renderPreviewCard = (previewData) => {
    if (!previewData) return null;

    return (
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 mt-2 border border-green-200">
        <div className="flex items-center mb-3">
          <Brain className="text-green-600 text-xl mr-2" />
          <h3 className="font-bold text-gray-800">Model Preview</h3>
        </div>

        <div className="grid grid-cols-3 gap-3 mb-3">
          <div className="bg-white rounded-lg p-3 shadow-sm text-center">
            <div className="text-2xl font-bold text-green-600">
              {previewData.accuracy}%
            </div>
            <div className="text-xs text-gray-600">Est. Accuracy</div>
          </div>
          <div className="bg-white rounded-lg p-3 shadow-sm text-center">
            <div className="text-2xl font-bold text-blue-600">
              {previewData.n_classes}
            </div>
            <div className="text-xs text-gray-600">Classes</div>
          </div>
          <div className="bg-white rounded-lg p-3 shadow-sm text-center">
            <div className="text-2xl font-bold text-purple-600">
              {previewData.sample_size.toLocaleString()}
            </div>
            <div className="text-xs text-gray-600">Samples</div>
          </div>
        </div>

        {previewData.top_features && previewData.top_features.length > 0 && (
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <div className="text-xs font-semibold text-gray-700 mb-2">
              Top Features:
            </div>
            <div className="space-y-1">
              {previewData.top_features.slice(0, 3).map((feature, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between text-xs"
                >
                  <span className="text-gray-600">{feature.name}</span>
                  <div className="flex items-center">
                    <div className="w-20 h-2 bg-gray-200 rounded-full mr-2">
                      <div
                        className="h-2 bg-green-500 rounded-full"
                        style={{ width: `${feature.importance}%` }}
                      ></div>
                    </div>
                    <span className="text-green-600 font-semibold">
                      {feature.importance}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderModelComparisonCard = (comparisonData) => {
    if (!comparisonData) return null;

    const getModelColor = (index) => {
      const colors = ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#6366F1'];
      return colors[index % colors.length];
    };

    return (
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 mt-2 border border-blue-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center">
            <BarChart3 className="text-blue-600 text-xl mr-2" />
            <h3 className="font-bold text-gray-800">Model Comparison Results</h3>
          </div>
          <div className="bg-yellow-100 px-3 py-1 rounded-full">
            <span className="text-xs font-bold text-yellow-800">
              🏆 Best: {comparisonData.best_model}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg p-3 shadow-sm mb-3">
          <div className="text-sm font-semibold text-gray-700 mb-2">
            Accuracy Comparison:
          </div>
          <div className="space-y-2">
            {comparisonData.models.slice(0, 6).map((model, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-gray-700">{model.name}</span>
                  <span className="font-bold" style={{ color: getModelColor(idx) }}>
                    {model.accuracy}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-500"
                    style={{
                      width: `${model.accuracy}%`,
                      backgroundColor: getModelColor(idx),
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="bg-white rounded-lg p-2 shadow-sm text-center">
            <div className="text-lg font-bold text-green-600">
              {comparisonData.best_accuracy}%
            </div>
            <div className="text-xs text-gray-600">Best Accuracy</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow-sm text-center">
            <div className="text-lg font-bold text-blue-600">
              {comparisonData.models.length}
            </div>
            <div className="text-xs text-gray-600">Models Tested</div>
          </div>
        </div>

        {comparisonData.models[0] && (
          <div className="mt-3 bg-gradient-to-r from-green-100 to-emerald-100 rounded-lg p-3">
            <div className="text-xs font-semibold text-gray-700 mb-2">
              🏆 Winner: {comparisonData.models[0].name}
            </div>
            <div className="grid grid-cols-4 gap-2 text-xs">
              <div>
                <div className="font-bold text-green-700">{comparisonData.models[0].accuracy}%</div>
                <div className="text-gray-600">Accuracy</div>
              </div>
              <div>
                <div className="font-bold text-blue-700">{comparisonData.models[0].precision}%</div>
                <div className="text-gray-600">Precision</div>
              </div>
              <div>
                <div className="font-bold text-purple-700">{comparisonData.models[0].recall}%</div>
                <div className="text-gray-600">Recall</div>
              </div>
              <div>
                <div className="font-bold text-orange-700">{comparisonData.models[0].f1_score}%</div>
                <div className="text-gray-600">F1-Score</div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderDownloadCard = (downloadData) => {
    return (
      <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-4 mt-2 border border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <CheckCircle className="text-green-500 text-2xl mr-3" />
            <div>
              <div className="font-bold text-gray-800">File Ready!</div>
              <div className="text-xs text-gray-600">
                {downloadData.filename}
              </div>
            </div>
          </div>
          <a
            href={downloadData.url}
            download={downloadData.filename}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg flex items-center transition-all shadow-md hover:shadow-lg"
          >
            <Download className="mr-2" />
            Download
          </a>
        </div>
      </div>
    );
  };

  const renderMessage = (msg, index) => {
    const isAgent = msg.sender === "agent";

    return (
      <div
        key={index}
        className={`flex ${
          isAgent ? "justify-start" : "justify-end"
        } mb-4 animate-fadeIn`}
      >
        <div className={`max-w-2xl ${isAgent ? "ml-2" : "mr-2"}`}>
          {isAgent && (
            <div className="flex items-center mb-1">
              <div className="w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center mr-2">
                <Bot className="text-white text-xs" size={14} />
              </div>
              <span className="text-xs text-gray-500">AI Assistant</span>
            </div>
          )}

          <div
            className={`p-4 rounded-2xl shadow-md ${
              isAgent
                ? "bg-white text-gray-800 rounded-tl-none border border-gray-200"
                : "bg-indigo-600 text-white rounded-tr-none"
            }`}
          >
            <div className="whitespace-pre-wrap">{msg.text}</div>

            {msg.data &&
              msg.data.type === "analysis" &&
              renderAnalysisCard(msg.data.analysis)}
            {msg.data &&
              msg.data.type === "preview" &&
              renderPreviewCard(msg.data.preview)}
            {msg.data &&
              msg.data.type === "model_comparison" &&
              renderModelComparisonCard(msg.data.comparison)}
            {msg.data &&
              msg.data.type === "download" &&
              renderDownloadCard(msg.data)}

            <div className="text-xs opacity-60 mt-2">{msg.timestamp}</div>
          </div>
        </div>
      </div>
    );
  };

  const renderProgressBar = () => {
    if (!progress) return null;

    return (
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200 mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-gray-700">
            {progress.message}
          </span>
          <span className="text-sm font-bold text-indigo-600">
            {progress.percentage}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress.percentage}%` }}
          >
            <div className="h-full w-full bg-white/20 animate-pulse"></div>
          </div>
        </div>
        <div className="mt-2 flex items-center text-xs text-gray-500">
          <Loader2 className="animate-spin mr-2" size={14} />
          <span>Step: {progress.step}</span>
        </div>
      </div>
    );
  };

  const renderInput = () => {
    if (isLoading) {
      return (
        <div className="space-y-3">
          {renderProgressBar()}
          <div className="flex items-center justify-center p-4 bg-gray-50 rounded-xl">
            <Loader2 className="animate-spin text-indigo-600 text-xl mr-3" />
            <span className="text-gray-600 font-medium">
              {progress ? progress.message : "AI is thinking..."}
            </span>
          </div>
        </div>
      );
    }

    if (currentState === "initial" || currentState === "error") {
      return (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
            isDragging
              ? "border-indigo-500 bg-indigo-50"
              : "border-gray-300 hover:border-indigo-400 hover:bg-gray-50"
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileInputChange}
            className="hidden"
            accept=".csv,.xlsx,.xls"
          />
          <Upload className="text-5xl text-indigo-400 mx-auto mb-3" size={48} />
          <p className="text-gray-700 font-semibold mb-1">
            {isDragging ? "Drop your file here!" : "Drag & drop your file here"}
          </p>
          <p className="text-sm text-gray-500">or click to browse</p>
          <p className="text-xs text-gray-400 mt-2">
            Supports CSV, XLSX, XLS (Max 50MB)
          </p>
        </div>
      );
    }

    if (currentState === "analyzed" || currentState === "target_set") {
      return (
        <div className="space-y-3">
          {/* Output Type Selection */}
          {choices.length > 0 && (
            <div className="space-y-3">
              <div className="flex justify-center gap-3">
                {choices.map((choice) => (
                  <button
                    key={choice}
                    onClick={() => handleSendMessage(choice)}
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white font-semibold py-2 px-6 rounded-lg shadow-md hover:shadow-lg transition-all transform hover:scale-105"
                  >
                    {choice.charAt(0).toUpperCase() + choice.slice(1)}
                  </button>
                ))}
              </div>

              {/* Compare Models Button - Always show when target is set */}
              {currentState === "target_set" && (
                <div className="flex justify-center">
                  {modelComparison ? (
                    <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold py-2 px-6 rounded-lg shadow-md flex items-center">
                      <CheckCircle className="mr-2" size={18} />
                      Models Compared ✓
                    </div>
                  ) : (
                    <button
                      onClick={compareModels}
                      disabled={isComparing}
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-2 px-6 rounded-lg shadow-md hover:shadow-lg transition-all transform hover:scale-105 disabled:cursor-not-allowed flex items-center"
                    >
                      {isComparing ? (
                        <>
                          <Loader2 className="animate-spin mr-2" size={18} />
                          Comparing Models...
                        </>
                      ) : (
                        <>
                          <BarChart3 className="mr-2" size={18} />
                          Compare 5 ML Models
                        </>
                      )}
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-2">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-grow border-2 border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:border-indigo-500 transition-all"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!userInput.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-bold py-3 px-6 rounded-xl transition-all shadow-md hover:shadow-lg disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      );
    }

    if (currentState === "completed") {
      return (
        <div className="bg-green-50 border-2 border-green-200 rounded-xl p-4 text-center">
          <CheckCircle
            className="text-green-500 text-3xl mx-auto mb-2"
            size={48}
          />
          <p className="text-green-700 font-semibold">Analysis Complete! 🎉</p>
          <p className="text-sm text-gray-600 mt-1">
            Download your file above or start a new analysis
          </p>
          <button
            onClick={() => {
              setCurrentState("initial");
              setMessages([]);
              setSessionId(null);
              setAnalysis(null);
              setPreview(null);
              setChoices([]);
              addMessage(
                "agent",
                "Ready for a new analysis! Upload another file to begin."
              );
            }}
            className="mt-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-all"
          >
            Start New Analysis
          </button>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 flex items-center justify-center p-4">
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
        @keyframes slideIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>

      <div
        className="w-full max-w-6xl bg-white rounded-3xl shadow-2xl overflow-hidden flex flex-col lg:flex-row"
        style={{ height: "90vh" }}
      >
        <div className="lg:w-1/3 bg-gradient-to-br from-indigo-600 to-purple-700 p-8 text-white flex flex-col">
          <div className="flex items-center mb-6">
            <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center mr-4 shadow-lg">
              <Bot className="text-indigo-600" size={32} />
            </div>
            <div>
              <h1 className="text-2xl font-bold">AI Data Scientist</h1>
              <p className="text-xs text-indigo-200">
                Autonomous Analysis Agent
              </p>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 mb-6">
            <p className="text-sm leading-relaxed">
              Welcome! I'm an AI agent that autonomously analyzes your data,
              builds predictive models, and generates professional deliverables
              through natural conversation.
            </p>
          </div>

          <div className="space-y-4 text-sm mb-8">
            <div className="flex items-start">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                <span className="text-lg">📤</span>
              </div>
              <div>
                <div className="font-semibold">1. Upload Data</div>
                <div className="text-xs text-indigo-200">CSV or Excel file</div>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                <span className="text-lg">💬</span>
              </div>
              <div>
                <div className="font-semibold">2. Chat with AI</div>
                <div className="text-xs text-indigo-200">
                  Answer simple questions
                </div>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                <span className="text-lg">🤖</span>
              </div>
              <div>
                <div className="font-semibold">3. AI Analyzes</div>
                <div className="text-xs text-indigo-200">
                  Automated ML pipeline
                </div>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                <span className="text-lg">📊</span>
              </div>
              <div>
                <div className="font-semibold">4. Get Results</div>
                <div className="text-xs text-indigo-200">
                  Notebook or Dashboard
                </div>
              </div>
            </div>
          </div>

          <div className="mt-auto space-y-3">
            {sessionId && (
              <div className="bg-white/10 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-indigo-200 text-xs font-semibold">Active Session</span>
                  <span className="bg-green-400 w-2 h-2 rounded-full animate-pulse"></span>
                </div>
                <div className="font-mono text-[10px] opacity-75 truncate text-indigo-100">
                  {sessionId.substring(0, 12)}...
                </div>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-[10px] text-indigo-300">State:</span>
                  <span className="text-[10px] text-white font-semibold">{currentState}</span>
                </div>
                <div className="mt-1 flex items-center justify-between">
                  <span className="text-[10px] text-indigo-300">Messages:</span>
                  <span className="text-[10px] text-white font-semibold">{messages.length}</span>
                </div>
              </div>
            )}

            <div className="bg-white/10 rounded-lg p-3">
              <div className="text-indigo-200 text-xs font-semibold mb-3 text-center">
                📊 Session Manager
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={saveCurrentSession}
                  disabled={!sessionId || messages.length < 2}
                  className="bg-green-500/20 hover:bg-green-500/30 disabled:bg-gray-500/10 disabled:text-gray-400 text-green-200 text-[10px] font-semibold py-2 px-2 rounded-lg transition-all flex flex-col items-center justify-center disabled:cursor-not-allowed"
                  title="Save current session"
                >
                  <span className="text-base mb-1">💾</span>
                  <span>Save</span>
                </button>
                <button
                  onClick={loadSavedSessions}
                  className="bg-blue-500/20 hover:bg-blue-500/30 text-blue-200 text-[10px] font-semibold py-2 px-2 rounded-lg transition-all flex flex-col items-center justify-center"
                  title="Load saved session"
                >
                  <span className="text-base mb-1">📂</span>
                  <span>Load</span>
                </button>
                <button
                  onClick={exportChatHistory}
                  disabled={messages.length < 2}
                  className="bg-white/20 hover:bg-white/30 disabled:bg-gray-500/10 disabled:text-gray-400 text-white text-[10px] font-semibold py-2 px-2 rounded-lg transition-all flex flex-col items-center justify-center disabled:cursor-not-allowed"
                  title="Export chat history"
                >
                  <Download size={16} className="mb-1" />
                  <span>Export</span>
                </button>
                <button
                  onClick={clearSession}
                  disabled={!sessionId}
                  className="bg-red-500/20 hover:bg-red-500/30 disabled:bg-gray-500/10 disabled:text-gray-400 text-red-200 text-[10px] font-semibold py-2 px-2 rounded-lg transition-all flex flex-col items-center justify-center disabled:cursor-not-allowed"
                  title="Clear session"
                >
                  <span className="text-base mb-1">🗑️</span>
                  <span>Clear</span>
                </button>
              </div>
            </div>
          </div>

          <div className="mt-4 text-xs text-center text-indigo-200">
            <p>Powered by AI • FastAPI • React</p>
            <p className="mt-1 opacity-75">💾 Auto-saved to browser</p>
          </div>
        </div>

        <div className="flex-1 flex flex-col bg-gray-50">
          <div className="bg-white border-b border-gray-200 p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-800">
                  Conversation
                </h2>
                <p className="text-xs text-gray-500">
                  {currentState === "initial" && "Waiting for file upload"}
                  {currentState === "uploading" && "Uploading and analyzing..."}
                  {currentState === "analyzed" &&
                    "Dataset analyzed - awaiting target"}
                  {currentState === "target_set" && "Ready to generate output"}
                  {currentState === "generating" && "Generating your file..."}
                  {currentState === "completed" && "Analysis complete!"}
                </p>
              </div>

              {analysis && (
                <div className="flex gap-2 text-xs">
                  <div className="bg-indigo-100 px-3 py-1 rounded-full text-indigo-700 font-semibold">
                    {analysis.stats.rows.toLocaleString()} rows
                  </div>
                  <div className="bg-purple-100 px-3 py-1 rounded-full text-purple-700 font-semibold">
                    {analysis.stats.columns} cols
                  </div>
                </div>
              )}
            </div>
          </div>

          <div
            ref={chatWindowRef}
            className="flex-1 overflow-y-auto p-6 space-y-4"
          >
            {messages.map((msg, index) => renderMessage(msg, index))}
          </div>

          <div className="bg-white border-t border-gray-200 p-4 shadow-lg">
            {renderInput()}
          </div>
        </div>
      </div>

      {/* Analysis History Modal */}
      {showSessionHistory && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[85vh] overflow-hidden flex flex-col">
            <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white p-6 flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold flex items-center">
                  <span className="mr-3">📊</span>
                  Analysis History
                </h3>
                <p className="text-sm text-indigo-100 mt-1">Your saved data science sessions</p>
              </div>
              <button
                onClick={() => setShowSessionHistory(false)}
                className="text-white hover:bg-white/20 rounded-full p-2 transition-all"
              >
                <span className="text-2xl">×</span>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-br from-gray-50 to-indigo-50">
              {savedSessions.length === 0 ? (
                <div className="text-center py-16">
                  <div className="text-6xl mb-4">📂</div>
                  <p className="text-xl font-semibold text-gray-700 mb-2">No saved sessions yet</p>
                  <p className="text-sm text-gray-500">Save your current analysis to build your history!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {savedSessions.map((session, index) => (
                    <div
                      key={index}
                      className="bg-white rounded-2xl p-5 border-2 border-gray-200 hover:border-indigo-400 hover:shadow-xl transition-all transform hover:scale-[1.02] relative overflow-hidden"
                    >
                      {/* Decorative gradient bar */}
                      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
                      
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-bold text-lg text-gray-800">{session.name}</h4>
                            {session.currentState === 'completed' && (
                              <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-semibold">
                                ✓ Complete
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-500 flex items-center gap-2">
                            <span>🕒 {session.date}</span>
                            <span>•</span>
                            <span>📄 {session.datasetName}</span>
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => restoreSession(session)}
                            className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white text-sm font-semibold py-2 px-4 rounded-lg transition-all shadow-md hover:shadow-lg"
                          >
                            📂 Restore
                          </button>
                          <button
                            onClick={() => deleteSavedSession(index)}
                            className="bg-red-500 hover:bg-red-600 text-white text-sm font-semibold py-2 px-3 rounded-lg transition-all"
                            title="Delete session"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
                        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
                          <div className="text-blue-600 font-semibold mb-1">Messages</div>
                          <div className="text-xl font-bold text-blue-700">{session.messages.length}</div>
                        </div>
                        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
                          <div className="text-purple-600 font-semibold mb-1">Target</div>
                          <div className="text-sm font-bold text-purple-700 truncate">{session.targetColumn}</div>
                        </div>
                        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 border border-green-200">
                          <div className="text-green-600 font-semibold mb-1">Best Model</div>
                          <div className="text-sm font-bold text-green-700 truncate">{session.bestModel}</div>
                        </div>
                        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-3 border border-orange-200">
                          <div className="text-orange-600 font-semibold mb-1">Accuracy</div>
                          <div className="text-xl font-bold text-orange-700">{session.accuracy}%</div>
                        </div>
                        <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-3 border border-pink-200">
                          <div className="text-pink-600 font-semibold mb-1">Status</div>
                          <div className="text-sm font-bold text-pink-700 capitalize">{session.currentState}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="border-t border-gray-200 p-4 bg-white">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>💾 Stored locally in your browser</span>
                <span>📊 Max 15 sessions • Auto-expires after 30 days</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
