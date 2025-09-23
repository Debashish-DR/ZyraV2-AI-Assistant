import { useState, useContext, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { AssistantContext } from '../App';
import Sidebar from '../components/Sidebar';
import BottomControls from '../components/BottomControls';
import AnimatedBackground from '../components/AnimatedBackground';
import AIChipAnimation from '../components/AIChipAnimation';
import bigGif from '../assets/big-gif.gif';

function History() {
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showScrollToBottom, setShowScrollToBottom] = useState(false);
  const { chatlogCache, setChatlogCache, setIsProcessing, setStatus, generateMessageId } = useContext(AssistantContext);
  const chatContainerRef = useRef(null);
  const dropdownRef = useRef(null);
  const searchInputRef = useRef(null);
  const hasLoadedRef = useRef(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Focus search input when dropdown opens
  useEffect(() => {
    if (isDropdownOpen && searchInputRef.current) {
      setTimeout(() => {
        searchInputRef.current?.focus();
      }, 100);
    }
  }, [isDropdownOpen]);

  // Reset assistant state on mount
  useEffect(() => {
    setIsProcessing(false);
    setStatus('Available');
  }, [setIsProcessing, setStatus]);

  const fetchChatlog = useCallback(async () => {
  if (hasLoadedRef.current) return;
  
  setLoading(true);
  try {
    // FIX: Get email from localStorage and ensure it exists
    const email = localStorage.getItem('email');
    if (!email) {
      console.error('No email found in localStorage');
      setLoading(false);
      return;
    }
    
    const res = await axios.post('/api/get-chatlog', { email });
    const formattedChatlog = res.data.chatlog.map(msg => ({
      ...msg,
      date: msg.date || new Date().toISOString(),
      id: msg.id || generateMessageId(),
      timestamp: msg.timestamp ? new Date(msg.timestamp).toISOString() : new Date().toISOString()
    }));
    setChatlogCache(formattedChatlog);
    hasLoadedRef.current = true;
  } catch (err) {
    console.error('History fetch error:', err);
  } finally {
    setLoading(false);
  }
}, [setChatlogCache, generateMessageId]);

  useEffect(() => {
    if (!chatlogCache || chatlogCache.length === 0) {
      fetchChatlog();
    } else {
      setLoading(false);
    }
  }, [chatlogCache, fetchChatlog]);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, []);

  // Scroll to bottom when chatlog updates
  useEffect(() => {
    if (chatlogCache && chatlogCache.length > 0) {
      // Small delay to ensure DOM is updated
      setTimeout(() => {
        scrollToBottom();
      }, 100);
    }
  }, [chatlogCache, scrollToBottom]);

  // Show/hide scroll to bottom button based on scroll position
  useEffect(() => {
    const handleScroll = () => {
      if (chatContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
        const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
        setShowScrollToBottom(!isNearBottom);
      }
    };

    const chatContainer = chatContainerRef.current;
    if (chatContainer) {
      chatContainer.addEventListener('scroll', handleScroll);
      // Check initial position
      handleScroll();
      
      return () => chatContainer.removeEventListener('scroll', handleScroll);
    }
  }, []);

  const clearChat = async () => {
    try {
      await axios.post('/api/clear-chatlog', { email: localStorage.getItem('userEmail') || '' });
      setChatlogCache([]);
      setSearchTerm('');
      setIsDropdownOpen(false);
    } catch (err) {
      console.error('Clear chat error:', err);
    }
  };

  // Apply filter and search
  const filteredChatlog = (chatlogCache || []).filter(msg => {
    if (filter === "user" && msg.role !== "user") return false;
    if (filter === "assistant" && msg.role !== "assistant") return false;
    
    if (searchTerm.trim() !== '') {
      return msg.content.toLowerCase().includes(searchTerm.toLowerCase());
    }
    
    return true;
  });

  const groupedChatlog = filteredChatlog.reduce((acc, msg) => {
    const messageDate = msg.timestamp || msg.date;
    const date = new Date(messageDate).toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
    if (!acc[date]) acc[date] = [];
    acc[date].push(msg);
    return acc;
  }, {});

  const filterIcons = {
    all: '🗨️',
    user: '👤',
    assistant: '🤖'
  };

  const filterLabels = {
    all: 'All Messages',
    user: 'User Only', 
    assistant: 'Assistant Only'
  };

  if (loading) {
    return (
      <motion.div className="flex min-h-screen bg-gray-900 text-white" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
        <Sidebar />
        <div className="flex-1 p-4 md:p-8 relative overflow-hidden">
          <AnimatedBackground />
          <div className="relative z-10">
            <motion.div className="h-[70vh] bg-gray-800/80 backdrop-blur-md rounded-lg p-4 shadow-lg flex flex-col space-y-4" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.5 }}>
              {[...Array(5)].map((_, i) => (
                <motion.div key={i} className="animate-pulse bg-gray-700 h-8 w-3/4 rounded" initial={{ opacity: 0.5 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, repeat: Infinity, repeatType: 'reverse' }} />
              ))}
            </motion.div>
            <BottomControls />
          </div>
          
          <div className="hidden md:block absolute bottom-0 left-4 z-20 pointer-events-none">
            <div className="scale-75"><AIChipAnimation size="sm" /></div>
          </div> 
          <div className="hidden md:block absolute bottom-0 right-4 z-20 pointer-events-none">
            <div className="scale-75"><AIChipAnimation size="sm" /></div>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div className="flex min-h-screen bg-gray-900 text-white" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
      <Sidebar />
      <div className="flex-1 p-4 md:p-8 relative overflow-hidden">
        <AnimatedBackground />
        
        <div className="relative z-10">
          {/* Header with Enhanced Dropdown - Fixed z-index */}
          <div className="flex justify-between items-center mb-2">
            <div className="flex-1"></div>
            <h2 className="top-0 text-2xl md:text-4xl font-mono font-bold bg-gradient-to-r from-cyan-200 via-cyan-300 to-cyan-200 bg-clip-text text-transparent text-center flex-1">
              Chat History
            </h2>
            <div className="flex-1 flex justify-end relative" ref={dropdownRef}>
              {/* Dropdown Trigger Button */}
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="bg-gradient-to-br from-cyan-900/50 to-gray-900/30 backdrop-blur-lg border border-cyan-400/40 text-cyan-100 px-3 py-2 md:px-4 md:py-2 rounded-xl hover:from-cyan-600/40 hover:to-cyan-600/40 hover:border-cyan-300/60 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-cyan-500/20"
              >
                <span className="hidden md:inline">{filterLabels[filter]}</span>
                <span className="md:hidden text-lg">{filterIcons[filter]}</span>
                <svg className={`w-4 h-4 transition-transform duration-300 ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {/* Enhanced Dropdown Menu - Fixed z-index to appear above chat container */}
              <AnimatePresence>
                {isDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-full right-0 mt-2 p-1 w-80 md:w-96 bg-gradient-to-b from-cyan-900/20 to-gray-900/20 opacity-90 backdrop-blur-xl border border-cyan-400/30 rounded-2xl shadow-2xl z-50 overflow-hidden"
                  >
                    {/* Search Section */}
                    <div className="p-4 border-b border-cyan-500/20">
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                          </svg>
                        </div>
                        <input
                          ref={searchInputRef}
                          type="text"
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 bg-gray-700/50 border border-cyan-500/30 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                          placeholder="Search messages..."
                        />
                        {searchTerm && (
                          <button
                            onClick={() => setSearchTerm('')}
                            className="absolute inset-y-0 right-0 pr-3 flex items-center"
                          >
                            <svg className="w-4 h-4 text-gray-400 hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Filter Options */}
                    <div className="max-h-60 overflow-y-auto">
                      {[
                        { value: 'all', label: 'All Messages', icon: '🗨️', desc: 'Show all conversations' },
                        { value: 'user', label: 'User Only', icon: '👤', desc: 'Only your messages' },
                        { value: 'assistant', label: 'Assistant Only', icon: '🤖', desc: 'Only AI responses' }
                      ].map((option) => (
                        <button
                          key={option.value}
                          onClick={() => { setFilter(option.value); setIsDropdownOpen(false); }}
                          className={`w-full text-left px-4 py-3 hover:bg-cyan-500/20 transition-all duration-200 border-b border-cyan-500/10 last:border-b-0 group ${
                            filter === option.value ? 'bg-cyan-500/30 text-cyan-200' : 'text-gray-300'
                          }`}
                        >
                          <div className="flex items-center space-x-3">
                            <span className="text-lg">{option.icon}</span>
                            <div className="flex-1">
                              <div className="font-medium group-hover:text-cyan-200">{option.label}</div>
                              <div className="text-xs text-gray-400 group-hover:text-cyan-300/80">{option.desc}</div>
                            </div>
                            {filter === option.value && (
                              <svg className="w-4 h-4 text-cyan-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                        </button>
                      ))}
                    </div>

                    {/* Clear Chat Section */}
                    <div className="border-t border-cyan-500/20 bg-gradient-to-r from-red-500/10 to-red-600/10">
                      <button
                        onClick={clearChat}
                        className="w-full text-left px-4 py-3 text-red-300 hover:bg-red-500/20 transition-all duration-200 group"
                      >
                        <div className="flex items-center space-x-3">
                          <svg className="w-5 h-5 text-red-400 group-hover:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          <div>
                            <div className="font-medium group-hover:text-red-200">Clear Chat History</div>
                            <div className="text-xs text-red-400/80 group-hover:text-red-300/80">Permanently delete all messages</div>
                          </div>
                        </div>
                      </button>
                    </div>

                    {/* Search Results Info */}
                    {searchTerm && (
                      <div className="px-4 py-2 bg-cyan-500/10 border-t border-cyan-500/20">
                        <div className="text-xs text-cyan-400 text-center">
                          {filteredChatlog.length} messages found for "{searchTerm}"
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Chat History Container */}
          <div 
            className="h-[70vh] flex-1 bg-gradient-to-b from-gray-900/95 to-gray-950/95 backdrop-blur-sm rounded-2xl p-4 md:p-6 border border-cyan-500/20 shadow-2xl mb-2 overflow-y-auto scrollbar-professional relative" 
            ref={chatContainerRef}
          >
            {/* Scroll to Bottom Button */}
            <AnimatePresence>
              {showScrollToBottom && (
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  onClick={scrollToBottom}
                  className="absolute bottom-4 right-4 bg-gradient-to-br from-cyan-600 to-blue-600 text-white p-3 rounded-full shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 z-30 hover:scale-110"
                  title="Scroll to bottom"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </motion.button>
              )}
            </AnimatePresence>

            {Object.entries(groupedChatlog).length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-400">
                <div className="text-center">
                  <svg className="w-16 h-16 mx-auto mb-4 text-cyan-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p className="text-lg">{searchTerm ? 'No messages found' : 'No chat history available'}</p>
                  <p className="text-sm mt-1">
                    {searchTerm ? 'Try different search terms' : 'Start chatting to see your history here'}
                  </p>
                </div>
              </div>
            ) : (
              Object.entries(groupedChatlog).map(([date, messages]) => (
                <div key={date}>
                  {/* Date separator */}
                  <div className="text-center my-4 md:my-6">
                    <span className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-100 px-3 py-1 md:px-4 md:py-2 rounded-full text-xs md:text-sm font-medium backdrop-blur-sm">
                      {date}
                    </span>
                  </div>
                  
                  {/* Messages */}
                  {messages.map((msg) => {
                    const messageTimestamp = msg.timestamp || msg.date;
                    return (
                      <div
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} mb-3`}
                      >
                        <div
                          className={`max-w-[90%] md:max-w-[70%] rounded-xl p-3 ${
                            msg.role === 'user' 
                              ? 'bg-gradient-to-br from-cyan-600/50 to-gray-800/50 border border-cyan-500/20' 
                              : 'bg-gray-800/80 border border-cyan-500/20'
                          }`}
                        >
                          <div className="text-white/90 text-sm md:text-base">
                            {msg.content}
                            {msg.images && msg.images.map((url, i) => (
                              <img 
                                key={i} 
                                src={url} 
                                alt="Generated" 
                                className="mt-2 rounded-lg max-w-full"
                              />
                            ))}
                          </div>
                          <div className={`text-xs mt-1 ${
                            msg.role === 'user' ? 'text-cyan-200/70' : 'text-gray-400'
                          }`}>
                            {new Date(messageTimestamp).toLocaleTimeString('en-US', { 
                              hour: '2-digit', 
                              minute: '2-digit',
                              hour12: true 
                            })}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Responsive Bottom Controls */}
        <div className="w-full flex justify-center">
          <div className="w-full max-w-2xl">
            <BottomControls />
          </div>
        </div>
        
        {/* GIF in corner */}
        <img src={bigGif} alt="AI Animation" className="w-28 h-28 absolute bottom-4 right-4 opacity-50 z-20 hidden md:block" />
        
        {/* AI Chip Animation - Hidden on mobile for better performance */}
        <div className="hidden md:block absolute bottom-0 left-4 z-20 pointer-events-none">
          <div className="scale-75"><AIChipAnimation size="sm" /></div>
        </div> 
        <div className="hidden md:block absolute bottom-0 right-4 z-20 pointer-events-none">
          <div className="scale-75"><AIChipAnimation size="sm" /></div>
        </div>
      </div>
    </motion.div>
  );
}

export default History;













//=======================================================================================================================


// import { useState, useContext, useEffect } from 'react';
// import { motion, AnimatePresence } from 'framer-motion';
// import axios from 'axios';
// import { AssistantContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import bigGif from '../assets/big-gif.gif';

// function History() {
//   const [loading, setLoading] = useState(true);
//   const { chatlogCache, setChatlogCache } = useContext(AssistantContext);

//   useEffect(() => {
//     const fetchChatlog = async () => {
//       setLoading(true);
//       try {
//         const res = await axios.get('/api/get-chatlog');
//         const formattedChatlog = res.data.chatlog.map(msg => ({
//           ...msg,
//           date: msg.date || new Date().toISOString(),
//           id: msg.id || `${msg.role}-${Date.now()}-${Math.random()}`
//         }));
//         setChatlogCache(formattedChatlog);
//       } catch (err) {
//         console.error('History fetch error:', err);
//       } finally {
//         setLoading(false);
//       }
//     };
//     if (!chatlogCache || chatlogCache.length === 0) {
//       fetchChatlog();
//     } else {
//       setLoading(false);
//     }
//   }, [chatlogCache, setChatlogCache]); // Added chatlogCache to dependency array

//   const groupedChatlog = (chatlogCache || []).reduce((acc, msg) => {
//     const date = new Date(msg.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
//     if (!acc[date]) acc[date] = [];
//     acc[date].push(msg);
//     return acc;
//   }, {});

//   if (loading) {
//     return (
//       <motion.div className="flex min-h-screen bg-gray-900 text-white" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
//         <Sidebar />
//         <div className="flex-1 p-4 md:p-8 relative">
//           <h2 className="text-2xl font-semibold text-center mb-4">Chat History</h2>
//           <motion.div className="h-[70vh] bg-gray-800 rounded-lg p-4 shadow-lg flex flex-col space-y-4" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.5 }}>
//             {[...Array(5)].map((_, i) => (
//               <motion.div key={i} className="animate-pulse bg-gray-700 h-8 w-3/4 rounded" initial={{ opacity: 0.5 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, repeat: Infinity, repeatType: 'reverse' }} />
//             ))}
//           </motion.div>
//           <BottomControls />
//           <img src={bigGif} alt="Small GIF" className="w-28 h-28 absolute bottom-4 right-4 opacity-50" />
//         </div>
//       </motion.div>
//     );
//   }

//   return (
//     <motion.div className="flex min-h-screen bg-gray-900 text-white" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
//       <Sidebar />
//       <div className="flex-1 p-4 md:p-8 relative">
//         <h2 className="text-2xl font-semibold text-center mb-4">Chat History</h2>
//         <motion.div className="h-[70vh] bg-gray-800 rounded-lg p-4 shadow-lg overflow-y-auto" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.5 }}>
//           {Object.entries(groupedChatlog).length === 0 ? (
//             <div className="text-center text-gray-400">No chat history available.</div>
//           ) : (
//             Object.entries(groupedChatlog).map(([date, messages]) => (
//               <div key={date}>
//                 <div className="text-center text-gray-400 my-2">{date}</div>
//                 <AnimatePresence>
//                   {messages.map(msg => (
//                     <motion.div
//                       key={msg.id}
//                       className={`mb-2 p-2 rounded ${msg.role === 'user' ? 'bg-blue-600 ml-auto w-fit max-w-[70%]' : 'bg-gray-700 w-fit max-w-[70%]'}`}
//                       initial={{ opacity: 0, y: 10 }}
//                       animate={{ opacity: 1, y: 0 }}
//                       exit={{ opacity: 0, y: -10 }}
//                       transition={{ duration: 0.3 }}
//                     >
//                       {msg.content}
//                       {msg.images && msg.images.map((url, i) => (
//                         <img key={i} src={url} alt="Generated" className="mt-2 w-[70vw] max-w-[600px] rounded" />
//                       ))}
//                       <div className="text-xs text-gray-400 mt-1">
//                         {new Date(msg.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
//                       </div>
//                     </motion.div>
//                   ))}
//                 </AnimatePresence>
//               </div>
//             ))
//           )}
//         </motion.div>
//         <BottomControls />
//         <img src={bigGif} alt="Small GIF" className="w-28 h-28 absolute bottom-4 right-4 opacity-50" />
//       </div>
//     </motion.div>
//   );
// }

// export default History;

//=======================================================================================================================

// import { useState, useEffect, useRef, useContext } from 'react';
// import { motion, AnimatePresence } from 'framer-motion';
// import axios from 'axios';
// import { AssistantContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import bigGif from '../assets/big-gif.gif';

// function History() {
//   const [loading, setLoading] = useState(true);
//   const { chatlogCache, setChatlogCache } = useContext(AssistantContext);
//   const chatContainerRef = useRef(null);

//   useEffect(() => {
//     const fetchChatlog = async () => {
//       if (chatlogCache) {
//         setLoading(false);
//         return;
//       }
//       try {
//         const res = await axios.get('/api/get-chatlog');
//         const formattedChatlog = res.data.chatlog.map(msg => ({
//           ...msg,
//           date: msg.date || new Date().isoformat(),
//           id: msg.id || `${msg.role}-${Date.now()}-${Math.random()}`
//         }));
//         setChatlogCache(formattedChatlog);
//       } catch (err) {
//         console.error(err);
//       } finally {
//         setLoading(false);
//       }
//     };
//     fetchChatlog();
//   }, [chatlogCache, setChatlogCache]);

//   useEffect(() => {
//     if (chatContainerRef.current) {
//       chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
//     }
//   }, [chatlogCache]);

//   const groupedChatlog = (chatlogCache || []).reduce((acc, msg) => {
//     const date = new Date(msg.date).toLocaleDateString();
//     if (!acc[date]) acc[date] = [];
//     acc[date].push(msg);
//     return acc;
//   }, {});

//   if (loading) {
//     return (
//       <motion.div 
//         className="flex min-h-screen bg-gray-900 text-white" 
//         initial={{ opacity: 0 }} 
//         animate={{ opacity: 1 }} 
//         transition={{ duration: 0.5, ease: 'easeInOut' }}
//       >
//         <Sidebar />
//         <div className="flex-1 p-4 md:p-8 relative">
//           <motion.h2 
//             className="text-2xl mb-4"
//             initial={{ y: -20, opacity: 0 }}
//             animate={{ y: 0, opacity: 1 }}
//             transition={{ duration: 0.5 }}
//           >
//             Chat History
//           </motion.h2>
//           <div className="chat-container h-[70vh] bg-gray-800 rounded-lg p-4 shadow-lg flex flex-col space-y-4">
//             {[...Array(5)].map((_, i) => (
//               <motion.div 
//                 key={i} 
//                 className="animate-pulse bg-gray-700 h-8 w-3/4 rounded"
//                 initial={{ opacity: 0.5 }}
//                 animate={{ opacity: 1 }}
//                 transition={{ duration: 0.5, repeat: Infinity, repeatType: 'reverse' }}
//               />
//             ))}
//           </div>
//           <BottomControls />
//           <img src={bigGif} alt="Small GIF" className="w-28 h-28 absolute bottom-4 right-4 opacity-50" />
//         </div>
//       </motion.div>
//     );
//   }

//   return (
//     <motion.div 
//       className="flex min-h-screen bg-gray-900 text-white" 
//       initial={{ opacity: 0 }} 
//       animate={{ opacity: 1 }} 
//       transition={{ duration: 0.5, ease: 'easeInOut' }}
//     >
//       <Sidebar />
//       <div className="flex-1 p-4 md:p-8 relative">
//         <motion.h2 
//           className="text-2xl mb-4"
//           initial={{ y: -20, opacity: 0 }}
//           animate={{ y: 0, opacity: 1 }}
//           transition={{ duration: 0.5 }}
//         >
//           Chat History
//         </motion.h2>
//         <motion.div 
//           className="chat-container overflow-y-auto overflow-x-hidden h-[70vh] bg-gray-800 rounded-lg p-4 shadow-lg flex flex-col-reverse"
//           ref={chatContainerRef}
//           initial={{ y: 20, opacity: 0 }}
//           animate={{ y: 0, opacity: 1 }}
//           transition={{ duration: 0.5, ease: 'easeOut' }}
//         >
//           <AnimatePresence>
//             {Object.entries(groupedChatlog).reverse().map(([date, messages]) => (
//               <motion.div
//                 key={date}
//                 initial={{ opacity: 0 }}
//                 animate={{ opacity: 1 }}
//                 exit={{ opacity: 0 }}
//                 transition={{ duration: 0.3 }}
//                 className="mb-4"
//               >
//                 <p className="text-center text-gray-400 text-sm mb-2">{date}</p>
//                 {messages.map((msg) => (
//                   <motion.div 
//                     key={msg.id} 
//                     className="mb-2"
//                     initial={{ opacity: 0, y: 20 }}
//                     animate={{ opacity: 1, y: 0 }}
//                     transition={{ duration: 0.3 }}
//                   >
//                     <p className="font-bold text-blue-400">{msg.role === 'user' ? 'You:' : 'Assistant:'}</p>
//                     <p className="text-gray-300 max-w-[80%] break-words">{msg.content}</p>
//                     {msg.images && msg.images.map((img, j) => (
//                       <img key={j} src={img} alt="Generated Image" className="mt-2 max-w-full rounded-lg" />
//                     ))}
//                   </motion.div>
//                 ))}
//               </motion.div>
//             ))}
//           </AnimatePresence>
//         </motion.div>
//         <BottomControls />
//         <img src={bigGif} alt="Small GIF" className="w-28 h-28 absolute bottom-4 right-4 opacity-50" />
//       </div>
//     </motion.div>
//   );
// }

// export default History;