import { useState, useContext, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { AuthContext, AssistantContext } from '../App';
import Sidebar from '../components/Sidebar';
import BottomControls from '../components/BottomControls';
import AnimatedBackground from '../components/AnimatedBackground';
import AIChipAnimation from '../components/AIChipAnimation';
import sendImg from '../assets/send.png';

function Chat() {
  const [message, setMessage] = useState('');
  const [replies, setReplies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [filter, setFilter] = useState("all");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const { user } = useContext(AuthContext);
  const { 
    setStatus, 
    setIsProcessing, 
    chatlogCache, 
    setChatlogCache, 
    stopCurrentAudio,
    generateMessageId
  } = useContext(AssistantContext);
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

  useEffect(() => {
    setIsProcessing(false);
    setStatus('Available');
    
    return () => {
      setIsProcessing(false);
      setStatus('Available');
    };
  }, [setIsProcessing, setStatus]);

  const fetchChatlog = useCallback(async () => {
    if (hasLoadedRef.current || !user?.email) {
      setLoading(false);
      return;
    }
    
    setLoading(true);
    try {
      console.log('Fetching chatlog for:', user.email);
      const res = await axios.post('/api/get-chatlog', { email: user.email });
      console.log('Chatlog response:', res.data);
      
      if (res.data && res.data.chatlog) {
        const formattedChatlog = res.data.chatlog.map(msg => ({
          ...msg,
          date: msg.date || new Date().toISOString(),
          id: msg.id || generateMessageId(),
          timestamp: msg.timestamp ? new Date(msg.timestamp).toISOString() : new Date().toISOString()
        }));
        setChatlogCache(formattedChatlog);
        hasLoadedRef.current = true;
      } else {
        setChatlogCache([]);
      }
    } catch (err) {
      console.error('Chat log fetch error:', err);
      setChatlogCache([]);
    } finally {
      setLoading(false);
    }
  }, [setChatlogCache, generateMessageId, user]);

  useEffect(() => {
    if (user?.email) {
      fetchChatlog();
    } else {
      setLoading(false);
    }
  }, [fetchChatlog, user]);

  useEffect(() => {
    if (chatlogCache && chatlogCache.length > 0) {
      const uniqueChatsMap = new Map();
      chatlogCache.forEach(msg => {
        if (!uniqueChatsMap.has(msg.id)) {
          uniqueChatsMap.set(msg.id, msg);
        }
      });
      setReplies(Array.from(uniqueChatsMap.values()));
    } else {
      setReplies([]);
    }
  }, [chatlogCache]);

  // FAST SCROLL - Removed complex animations that cause delays
  // Scroll to bottom function
  const scrollToBottom = useCallback(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, []);

  // Auto-scroll when replies change
  useEffect(() => {
    if (replies.length > 0) {
      setTimeout(() => {
        scrollToBottom();
      }, 100);
    }
  }, [replies, scrollToBottom]);

  const playAudioResponse = async (text) => {
    if (!user?.email) {
      console.error('User email not available for TTS');
      return;
    }
    
    try {
      const audioRes = await axios.post('/api/text-to-speech', 
        { text, email: user.email }, 
        { responseType: 'blob' }
      );
      const audioUrl = URL.createObjectURL(audioRes.data);
      const audio = new Audio(audioUrl);

      if (window.currentAudio) {
        window.currentAudio.pause();
      }
      window.currentAudio = audio;
      
      audio.play().catch(err => {
        console.error('Audio playback error:', err);
      });
    } catch (error) {
      console.error('TTS API error:', error);
    }
  };

  const clearChat = async () => {
    if (!user?.email) {
      console.error('User email not available for clear chat');
      return;
    }
    
    try {
      await axios.post('/api/clear-chatlog', { email: user.email });
      setChatlogCache([]);
      setReplies([]);
      setSearchTerm('');
      setIsDropdownOpen(false);
      hasLoadedRef.current = false; // Reset cache to allow refetch
    } catch (err) {
      console.error('Clear chat error:', err);
    }
  };

  const sendMessage = async () => {
    if (!message || isSending) return;
    if (!user?.email) {
      console.error('User email not available for chat');
      setStatus('Available');
      setIsProcessing(false);
      setIsSending(false);
      return;
    }
    
    setIsSending(true);
    const messageId = generateMessageId();
    const currentTimestamp = new Date().toISOString();
    const userMsg = { 
      role: 'user', 
      content: message, 
      date: currentTimestamp, 
      timestamp: currentTimestamp,
      id: messageId 
    };
    
    // IMMEDIATE UI UPDATE - No animation delays
    setReplies(prev => [...prev, userMsg]);
    setChatlogCache(prev => [...prev, userMsg]);
    
    setMessage('');
    setStatus('Processing ...');
    setIsProcessing(true);
    
    try {
      let assistantMsg;
      const assistantTimestamp = new Date().toISOString();
      
      if (message.toLowerCase().startsWith('generate image')) {
        const prompt = message.replace(/generate image/i, '').trim();
        const res = await axios.post('/api/image-generation', { prompt });
        assistantMsg = { 
          role: 'assistant', 
          content: `Generated images for "${prompt}":`, 
          date: assistantTimestamp, 
          timestamp: assistantTimestamp,
          id: `${messageId}-res`, 
          images: res.data.images 
        };
        setStatus('Available');
      } else {
        const res = await axios.post('/api/chat', { message: userMsg.content, email: user.email });
        assistantMsg = { 
          role: 'assistant', 
          content: res.data.reply, 
          date: assistantTimestamp, 
          timestamp: assistantTimestamp,
          id: `${messageId}-res` 
        };
        
        setStatus('Answering ...');
        stopCurrentAudio();
        // Don't wait for audio to play before showing message
        playAudioResponse(res.data.reply).catch(console.error);
      }
      
      // IMMEDIATE UI UPDATE for assistant response
      setReplies(prev => [...prev, assistantMsg]);
      setChatlogCache(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Send message error:', err);
      const errorMsg = 'Error occurred. Please try again.';
      const errorTimestamp = new Date().toISOString();
      const errObj = { 
        role: 'assistant', 
        content: errorMsg, 
        date: errorTimestamp, 
        timestamp: errorTimestamp,
        id: `${messageId}-err` 
      };
      
      setReplies(prev => [...prev, errObj]);
      setChatlogCache(prev => [...prev, errObj]);
      setStatus('Available');
    } finally {
      setIsSending(false);
      setIsProcessing(false);
    }
  };

  // Apply filter and search
  const filteredReplies = replies.filter(msg => {
    if (filter === "user" && msg.role !== "user") return false;
    if (filter === "assistant" && msg.role !== "assistant") return false;
    
    if (searchTerm.trim() !== '') {
      return msg.content.toLowerCase().includes(searchTerm.toLowerCase());
    }
    
    return true;
  });

  const groupedReplies = filteredReplies.reduce((acc, msg) => {
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
            <div className="flex items-center mt-2">
              <input type="text" className="border border-gray-700 p-2 flex-1 rounded-l bg-gray-800/80 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500" placeholder="Loading..." disabled />
              <button className="p-2 rounded-r bg-blue-600 text-white disabled:opacity-50" disabled>
                <img src={sendImg} alt="Send" className="w-6 h-6 invert" />
              </button>
            </div>
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
          {/* Header with Enhanced Dropdown */}
          <div className="flex justify-between items-center mb-2">
            <div className="flex-1"></div>
            <h2 className="top-0 text-2xl md:text-4xl font-mono font-bold bg-gradient-to-r from-cyan-200 via-cyan-300 to-cyan-200 bg-clip-text text-transparent text-center flex-1">
              Chat Assistant
            </h2>
            <div className="flex-1 flex justify-end relative" ref={dropdownRef}>
              {/* Dropdown Trigger Button */}
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="bg-gradient-to-br from-cyan-900/50 to-gray-900/30 backdrop-blur-lg border border-cyan-400/40 text-cyan-100 px-3 py-2 md:px-4 md:py-2 rounded-xl hover:from-cyan-600/40 hover:to-cyan-600/40 hover:border-cyan-300/60 transition-all duration-300 flex items-center space-x-2 shadow-lg hover:shadow-cyan-500/20"
              >
                {/* Mobile: Icon only, Desktop: Text + Icon */}
                <span className="hidden md:inline">{filterLabels[filter]}</span>
                <span className="md:hidden text-lg">{filterIcons[filter]}</span>
                <svg className={`w-4 h-4 transition-transform duration-300 ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {/* Enhanced Dropdown Menu */}
              <AnimatePresence>
                {isDropdownOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="absolute top-full right-0 mt-0 mb-2 p-1 w-80 md:w-96 bg-gradient-to-b from-cyan-900/20 to-gray-900/20 opacity-90 backdrop-blur-xl border border-cyan-400/30 rounded-2xl shadow-2xl z-50 overflow-hidden"
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
                          {filteredReplies.length} messages found for "{searchTerm}"
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Chat messages - REMOVED SLOW ANIMATIONS */}
          <div 
            className="h-[63vh] md:h-[63vh] flex-1 bg-gradient-to-b from-gray-900/95 to-gray-950/95 backdrop-blur-sm rounded-2xl p-4 md:p-6 z-50 border border-cyan-500/20 shadow-2xl mb-2 overflow-y-auto scrollbar-professional" 
            ref={chatContainerRef}
          >
            {Object.entries(groupedReplies).length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-400">
                <div className="text-center">
                  <svg className="w-16 h-16 mx-auto mb-4 text-cyan-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p className="text-lg">{searchTerm ? 'No messages found' : 'No messages yet'}</p>
                  <p className="text-sm mt-1">
                    {searchTerm ? 'Try different search terms' : 'Start a conversation with your AI assistant'}
                  </p>
                </div>
              </div>
            ) : (
              Object.entries(groupedReplies).map(([date, messages]) => (
                <div key={date}>
                  {/* Simplified date separator */}
                  <div className="text-center my-4 md:my-6">
                    <span className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-100 px-3 py-1 md:px-4 md:py-2 rounded-full text-xs md:text-sm font-medium backdrop-blur-sm">
                      {date}
                    </span>
                  </div>
                  
                  {/* FAST MESSAGE RENDERING - No animations */}
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

          {/* Input box */}
          <div className="flex items-center bg-gradient-to-b from-gray-900/95 to-gray-950/95 backdrop-blur-sm rounded-xl p-1 border border-cyan-500/20 shadow-xl mb-2">
            <input
              type="text"
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && sendMessage()}
              className="border-0 bg-transparent p-2 flex-1 text-white placeholder-gray-400 focus:outline-none focus:ring-0 text-sm md:text-base"
              placeholder="How can I assist you ..."
              disabled={isSending}
            />
            <button 
              onClick={sendMessage} 
              className="p-2 rounded-xl bg-cyan-600 text-white disabled:opacity-50 hover:bg-cyan-700 transition-colors duration-200" 
              disabled={isSending}
            >
              <img src={sendImg} alt="Send" className="w-6 h-6 md:w-8 md:h-6 invert" />
            </button>
          </div>
        </div>

        {/* Responsive Bottom Controls */}
        <div className="w-full flex justify-center mt-2">
          <div className="w-full max-w-2xl">
            <BottomControls />
          </div>
        </div>
        
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

export default Chat;













// import { useState, useContext, useEffect, useRef } from 'react';
// import { motion, AnimatePresence } from 'framer-motion';
// import axios from 'axios';
// import { AuthContext, AssistantContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import bigGif from '../assets/big-gif.gif';
// import sendImg from '../assets/send.png';

// function Chat() {
//   const [message, setMessage] = useState('');
//   const [replies, setReplies] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [isSending, setIsSending] = useState(false);
//   const [filter, setFilter] = useState("all");
//   const { user } = useContext(AuthContext);
//   const { 
//     setStatus, 
//     setIsProcessing, 
//     chatlogCache, 
//     setChatlogCache, 
//     stopCurrentAudio,
//     generateMessageId
//   } = useContext(AssistantContext);
//   const chatContainerRef = useRef(null);
//   const hasLoadedRef = useRef(false);

//   useEffect(() => {
//     setIsProcessing(false);
//     setStatus('Available');
    
//     return () => {
//       setIsProcessing(false);
//       setStatus('Available');
//     };
//   }, [setIsProcessing, setStatus]);

//   useEffect(() => {
//     const fetchChatlog = async () => {
//       if (hasLoadedRef.current) return;
      
//       setLoading(true);
//       try {
//         const res = await axios.get('/api/get-chatlog');
//         const formattedChatlog = res.data.chatlog.map(msg => ({
//           ...msg,
//           date: msg.date || new Date().toISOString(),
//           id: msg.id || generateMessageId()
//         }));
//         setChatlogCache(formattedChatlog);
//         hasLoadedRef.current = true;
//       } catch (err) {
//         console.error('Chat log fetch error:', err);
//       } finally {
//         setLoading(false);
//       }
//     };
    
//     fetchChatlog();
//   }, [setChatlogCache, generateMessageId]);

//   useEffect(() => {
//     if (chatlogCache && chatlogCache.length > 0) {
//       const uniqueChatsMap = new Map();
//       for (const msg of chatlogCache) {
//         if (!uniqueChatsMap.has(msg.id)) {
//           uniqueChatsMap.set(msg.id, msg);
//         }
//       }
//       setReplies(Array.from(uniqueChatsMap.values()));
//     }
//   }, [chatlogCache]);

//   // FIXED: Better scroll behavior
//   useEffect(() => {
//     if (chatContainerRef.current && replies.length > 0) {
//       const scrollToBottom = () => {
//         chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
//       };
      
//       // Immediate scroll
//       scrollToBottom();
      
//       // Additional scroll after a short delay to ensure it works
//       const timer = setTimeout(scrollToBottom, 100);
//       return () => clearTimeout(timer);
//     }
//   }, [replies]);

//   const playAudioResponse = async (text) => {
//     try {
//       const audioRes = await axios.post('/api/text-to-speech', 
//         { text, email: user.email }, 
//         { responseType: 'blob' }
//       );
//       const audioUrl = URL.createObjectURL(audioRes.data);
//       const audio = new Audio(audioUrl);

//       if (window.currentAudio) {
//         window.currentAudio.pause();
//       }
//       window.currentAudio = audio;
      
//       audio.play().catch(err => {
//         console.error('Audio playback error:', err);
//       });
//     } catch (error) {
//       console.error('TTS API error:', error);
//     }
//   };

//   const sendMessage = async () => {
//     if (!message || isSending) return;
//     if (!user?.email) {
//       console.error('User email not available for chat');
//       setStatus('Available');
//       setIsProcessing(false);
//       setIsSending(false);
//       return;
//     }
//     setIsSending(true);
//     const messageId = generateMessageId();
//     const userMsg = { role: 'user', content: message, date: new Date().toISOString(), id: messageId };
    
//     setReplies(prev => {
//       if (prev.some(m => m.id === userMsg.id)) return prev;
//       return [...prev, userMsg];
//     });
//     setChatlogCache(prev => {
//       if (prev.some(m => m.id === userMsg.id)) return prev;
//       return [...prev, userMsg];
//     });
    
//     setMessage('');
//     setStatus('Processing ...');
//     setIsProcessing(true);
    
//     try {
//       let assistantMsg;
//       if (message.toLowerCase().startsWith('generate image')) {
//         const prompt = message.replace(/generate image/i, '').trim();
//         const res = await axios.post('/api/image-generation', { prompt });
//         assistantMsg = { role: 'assistant', content: `Generated images for "${prompt}":`, date: new Date().toISOString(), id: `${messageId}-res`, images: res.data.images };
//         setStatus('Available');
//       } else {
//         const res = await axios.post('/api/chat', { message: userMsg.content, email: user.email });
//         assistantMsg = { role: 'assistant', content: res.data.reply, date: new Date().toISOString(), id: `${messageId}-res` };
        
//         setStatus('Answering ...');
        
//         stopCurrentAudio();
//         await playAudioResponse(res.data.reply);
//       }
      
//       setReplies(prev => {
//         if (prev.some(m => m.id === assistantMsg.id)) return prev;
//         return [...prev, assistantMsg];
//       });
//       setChatlogCache(prev => {
//         if (prev.some(m => m.id === assistantMsg.id)) return prev;
//         return [...prev, assistantMsg];
//       });
//     } catch (err) {
//       console.error('Send message error:', err);
//       const errorMsg = 'Error occurred. Please try again.';
//       const errId = `${messageId}-err`;
//       const errObj = { role: 'assistant', content: errorMsg, date: new Date().toISOString(), id: errId };
      
//       setReplies(prev => {
//         if (prev.some(m => m.id === errId)) return prev;
//         return [...prev, errObj];
//       });
//       setChatlogCache(prev => {
//         if (prev.some(m => m.id === errId)) return prev;
//         return [...prev, errObj];
//       });
//       setStatus('Available');
//     } finally {
//       setIsSending(false);
//       setIsProcessing(false);
//     }
//   };

//   // Apply filter
//   const filteredReplies = replies.filter(msg => {
//     if (filter === "all") return true;
//     if (filter === "user") return msg.role === "user";
//     if (filter === "assistant") return msg.role === "assistant";
//     return true;
//   });

//   const groupedReplies = filteredReplies.reduce((acc, msg) => {
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
//           <motion.div className="h-[70vh] bg-gray-800 rounded-lg p-4 shadow-lg flex flex-col space-y-4" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.5 }}>
//             {[...Array(5)].map((_, i) => (
//               <motion.div key={i} className="animate-pulse bg-gray-700 h-8 w-3/4 rounded" initial={{ opacity: 0.5 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, repeat: Infinity, repeatType: 'reverse' }} />
//             ))}
//           </motion.div>
//           <div className="flex items-center mt-2">
//             <input type="text" className="border border-gray-700 p-2 flex-1 rounded-l bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500" placeholder="Loading..." disabled />
//             <button className="p-2 rounded-r bg-blue-600 text-white disabled:opacity-50" disabled>
//               <img src={sendImg} alt="Send" className="w-6 h-6 invert" />
//             </button>
//           </div>
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
//         {/* Header row */}
//         <div className="flex items-center justify-between mb-4">
//           <h2 className="text-2xl font-bold">Chat Assistant</h2>
//           <select
//             value={filter}
//             onChange={(e) => setFilter(e.target.value)}
//             className="bg-gray-800 text-white border border-gray-700 rounded p-2 focus:outline-none focus:border-blue-500"
//           >
//             <option value="all">All Messages</option>
//             <option value="user">User Only</option>
//             <option value="assistant">Assistant Only</option>
//           </select>
//         </div>

//         {/* Chat messages */}
//         <motion.div 
//           className="h-[63vh] bg-gray-800 rounded-lg p-4 shadow-lg overflow-y-auto" 
//           initial={{ y: 20, opacity: 0 }} 
//           animate={{ y: 0, opacity: 1 }} 
//           transition={{ duration: 0.5 }} 
//           ref={chatContainerRef}
//         >
//           {Object.entries(groupedReplies).map(([date, messages]) => (
//             <div key={date}>
//               <div className="text-center text-gray-400 my-2">{date}</div>
//               <AnimatePresence>
//                 {messages.map(msg => (
//                   <motion.div
//                     key={msg.id}
//                     className={`mb-2 p-2 rounded ${msg.role === 'user' ? 'bg-blue-600 ml-auto w-fit max-w-[70%]' : 'bg-gray-700 w-fit max-w-[70%]'}`}
//                     initial={{ opacity: 0, y: 10 }}
//                     animate={{ opacity: 1, y: 0 }}
//                     exit={{ opacity: 0, y: -10 }}
//                     transition={{ duration: 0.3 }}
//                   >
//                     {msg.content}
//                     {msg.images && msg.images.map((url, i) => (
//                       <img key={i} src={url} alt="Generated" className="mt-2 w-[70vw] max-w-[600px] rounded" />
//                     ))}
//                     <div className="text-xs text-gray-400 mt-1">
//                       {new Date(msg.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
//                     </div>
//                   </motion.div>
//                 ))}
//               </AnimatePresence>
//             </div>
//           ))}
//         </motion.div>

//         {/* Input box */}
//         <div className="flex items-center mt-2">
//           <input
//             type="text"
//             value={message}
//             onChange={e => setMessage(e.target.value)}
//             onKeyPress={e => e.key === 'Enter' && sendMessage()}
//             className="border border-gray-700 p-2 flex-1 rounded-l bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
//             placeholder="Type your message..."
//             disabled={isSending}
//           />
//           <button onClick={sendMessage} className="p-2 rounded-r bg-blue-600 text-white disabled:opacity-50" disabled={isSending}>
//             <img src={sendImg} alt="Send" className="w-6 h-6 invert" />
//           </button>
//         </div>

//         <BottomControls />
//         <img src={bigGif} alt="Small GIF" className="w-28 h-28 absolute bottom-4 right-4 opacity-50" />
//       </div>
//     </motion.div>
//   );
// }

// export default Chat;
