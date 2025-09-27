import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect, useRef, createContext } from 'react';
import axios from 'axios';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Settings from './pages/Settings';
import Home from './pages/Home';
import Chat from './pages/Chat';
import History from './pages/History';
import './App.css';

export const AuthContext = createContext();
export const AssistantContext = createContext();

// Function to generate unique message IDs
const generateMessageId = () => {
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

function App() {
  const [user, setUser] = useState(null);
  const [assistant, setAssistant] = useState({ name: 'Zyra', voice: 'en-CA-ClaraNeural' });
  const [status, setStatus] = useState('Available');
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatlogCache, setChatlogCache] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isMicOn, setIsMicOn] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const currentAudioRef = useRef(null);

  // Set authentication state from localStorage on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    const email = localStorage.getItem('email');
    
    if (token && email) {
      setIsAuthenticated(true);
      console.log('✅ User authenticated from localStorage');
    } else {
      setIsAuthenticated(false);
      console.log('🔐 No authentication found in localStorage');
    }
  }, []);

  const fetchChatlog = async () => {
    try {
      const email = localStorage.getItem('email') || '';
      if (!email) {
        console.log('❌ No email found for chatlog fetch');
        setChatlogCache([]);
        return;
      }

      console.log('📖 Fetching chatlog for:', email);
      const res = await axios.post('/api/get-chatlog', { email });
      
      if (res.data && res.data.chatlog) {
        console.log('✅ Chatlog fetched successfully, messages:', res.data.chatlog.length);
        setChatlogCache(res.data.chatlog);
      } else {
        console.log('⚠️ No chatlog data received');
        setChatlogCache([]);
      }
    } catch (err) {
      console.error('❌ Chatlog fetch error:', err);
      // Initialize with welcome message if chatlog fails
      const welcomeMsg = {
        role: 'assistant',
        content: "Hello! I'm Zyra, your virtual assistant. How can I help you today?",
        date: new Date().toISOString(),
        id: generateMessageId()
      };
      setChatlogCache([welcomeMsg]);
    }
  };

  const stopCurrentAudio = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
    if (window.currentAudio) {
      window.currentAudio.pause();
      window.currentAudio.currentTime = 0;
      window.currentAudio = null;
    }
  };

  const cancelCurrentCommand = () => {
    stopCurrentAudio();
    setIsProcessing(false);
    setStatus('Available');
    setIsMicOn(false);
  };

  // Auto-reset status after processing
  useEffect(() => {
    if (status === 'Answering ...') {
      const timer = setTimeout(() => {
        if (!isProcessing && !isMicOn) {
          setStatus('Available');
        }
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [status, isProcessing, isMicOn]);

  // Cleanup audio on page unload
  useEffect(() => {
    const handleBeforeUnload = () => {
      stopCurrentAudio();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      stopCurrentAudio();
    };
  }, []);

  // Fetch user settings and initialize chat
  useEffect(() => {
    const fetchUserSettings = async () => {
      const email = localStorage.getItem('email');
      const token = localStorage.getItem('token');
      
      if (!email || !token) {
        console.log('❌ No email or token found for settings fetch');
        setIsAuthenticated(false);
        return;
      }
      
      try {
        console.log('⚙️ Fetching user settings for:', email);
        const res = await axios.post('/api/get-user-settings', { email });
        
        if (!res.data) {
          throw new Error('No data received from server');
        }

        const userData = {
          email,
          username: res.data.username || 'User',
          assistantname: res.data.assistantname || 'Zyra',
          assistantvoice: res.data.assistantvoice || 'en-CA-ClaraNeural'
        };
        
        setUser(userData);
        setAssistant({
          name: res.data.assistantname || 'Zyra',
          voice: res.data.assistantvoice || 'en-CA-ClaraNeural'
        });

        console.log('✅ User settings loaded:', userData);

        // Welcome message logic - only show once per session
        const welcomeShown = sessionStorage.getItem('welcomeShown');
        if (!welcomeShown) {
          const welcomeMsg = `Hello, I'm ${userData.assistantname}, your virtual assistant. How can I help you today?`;
          const welcomeObj = {
            role: 'assistant',
            content: welcomeMsg,
            date: new Date().toISOString(),
            id: generateMessageId()
          };
          
          setChatlogCache(prev => [...prev, welcomeObj]);
          sessionStorage.setItem('welcomeShown', 'true');
          setStatus('Answering ...');
          
          // Play welcome audio if not muted
          if (!isMuted) {
            try {
              console.log('🔊 Playing welcome audio');
              const audioRes = await axios.post('/api/text-to-speech', 
                { text: welcomeMsg, email: userData.email }, 
                { responseType: 'blob', timeout: 10000 }
              );
              
              if (audioRes.data) {
                const audioUrl = URL.createObjectURL(audioRes.data);
                const audio = new Audio(audioUrl);
                window.currentAudio = audio;
                
                audio.onended = () => {
                  console.log('✅ Welcome audio finished playing');
                  setStatus('Available');
                };
                
                audio.play().catch(e => {
                  console.error('❌ Audio play error:', e);
                  setStatus('Available');
                });
              }
            } catch (audioError) {
              console.error('❌ Welcome audio error:', audioError);
              setStatus('Available');
            }
          } else {
            setStatus('Available');
          }
        }
        
        // Load existing chatlog
        await fetchChatlog();
        setIsAuthenticated(true);
        
      } catch (err) {
        console.error('❌ Settings fetch error:', err);
        
        if (err.response?.status === 401) {
          console.log('🔐 Unauthorized - clearing tokens');
          localStorage.removeItem('email');
          localStorage.removeItem('token');
          sessionStorage.clear();
          setIsAuthenticated(false);
        } else {
          // Network or server error - try to continue with default settings
          console.log('🔄 Using default settings due to server error');
          const defaultUserData = {
            email: email,
            username: 'User',
            assistantname: 'Zyra',
            assistantvoice: 'en-CA-ClaraNeural'
          };
          
          setUser(defaultUserData);
          setAssistant({
            name: 'Zyra',
            voice: 'en-CA-ClaraNeural'
          });
          
          // Initialize with welcome message
          const welcomeMsg = {
            role: 'assistant',
            content: "Hello! I'm Zyra, your virtual assistant. How can I help you today?",
            date: new Date().toISOString(),
            id: generateMessageId()
          };
          setChatlogCache([welcomeMsg]);
        }
        setStatus('Available');
      }
    };
    
    if (isAuthenticated) {
      console.log('🔐 App is authenticated, fetching settings...');
      fetchUserSettings();
    }
  }, [isAuthenticated, isMuted]);

  const logout = () => {
    console.log('🚪 User logging out');
    localStorage.removeItem('email');
    localStorage.removeItem('token');
    sessionStorage.clear();
    setUser(null);
    setAssistant({ name: 'Zyra', voice: 'en-CA-ClaraNeural' });
    setChatlogCache([]);
    setIsAuthenticated(false);
    setIsMicOn(false);
    setIsMuted(false);
    stopCurrentAudio();
    setStatus('Available');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      setUser, 
      isAuthenticated, 
      setIsAuthenticated, 
      logout 
    }}>
      <AssistantContext.Provider value={{ 
        assistant, 
        setAssistant, 
        status, 
        setStatus, 
        isProcessing, 
        setIsProcessing, 
        chatlogCache, 
        setChatlogCache, 
        stopCurrentAudio,
        cancelCurrentCommand,
        generateMessageId,
        isMicOn,
        setIsMicOn,
        isMuted,
        setIsMuted,
        fetchChatlog
      }}>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/forgot" element={<ForgotPassword />} />
              <Route path="/reset" element={<ResetPassword />} />
              <Route path="/settings" element={isAuthenticated ? <Settings /> : <Login />} />
              <Route path="/home" element={isAuthenticated ? <Home /> : <Login />} />
              <Route path="/chat" element={isAuthenticated ? <Chat /> : <Login />} />
              <Route path="/history" element={isAuthenticated ? <History /> : <Login />} />
              {/* Redirect unknown routes to login */}
              <Route path="*" element={<Login />} />
            </Routes>
          </div>
        </Router>
      </AssistantContext.Provider>
    </AuthContext.Provider>
  );
}

export default App;



//===========================================================================================================



// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import { useState, useEffect, useRef, createContext } from 'react';
// import axios from 'axios';
// import Login from './pages/Login';
// import Signup from './pages/Signup';
// import ForgotPassword from './pages/ForgotPassword';
// import ResetPassword from './pages/ResetPassword';
// import Settings from './pages/Settings';
// import Home from './pages/Home';
// import Chat from './pages/Chat';
// import History from './pages/History';
// import './App.css';

// export const AuthContext = createContext();
// export const AssistantContext = createContext();

// function App() {
//   const [user, setUser] = useState(null);
//   const [assistant, setAssistant] = useState({ name: 'Zyra', voice: 'en-CA-ClaraNeural' });
//   const [status, setStatus] = useState('Available');
//   const [isProcessing, setIsProcessing] = useState(false);
//   const [chatlogCache, setChatlogCache] = useState([]);
//   const currentAudioRef = useRef(null);

//   axios.defaults.baseURL = 'http://localhost:5000';
//   axios.defaults.headers.common['Authorization'] = `Bearer ${localStorage.getItem('token')}`;

//   const stopCurrentAudio = () => {
//     if (currentAudioRef.current) {
//       currentAudioRef.current.pause();
//       currentAudioRef.current.currentTime = 0;
//       currentAudioRef.current = null;
//     }
//     if (window.currentAudio) {
//       window.currentAudio.pause();
//       window.currentAudio.currentTime = 0;
//       window.currentAudio = null;
//     }
//   };

//   useEffect(() => {
//     if (status === 'Answering ...') {
//       const timer = setTimeout(() => {
//         setStatus('Available');
//       }, 10000);
//       return () => clearTimeout(timer);
//     }
//   }, [status]);

//   useEffect(() => {
//     const fetchUserSettings = async () => {
//       const email = localStorage.getItem('email');
//       const token = localStorage.getItem('token');
//       if (!email || !token) return;
      
//       try {
//         const res = await axios.post('/api/get-user-settings', { email });
//         setUser({
//           email,
//           username: res.data.username || '',
//           assistantname: res.data.assistantname || 'Zyra',
//           assistantvoice: res.data.assistantvoice || 'en-CA-ClaraNeural'
//         });
//         setAssistant({
//           name: res.data.assistantname || 'Zyra',
//           voice: res.data.assistantvoice || 'en-CA-ClaraNeural'
//         });
        
//         // FIXED: Load chatlog first, then check/add welcome
//         const chatRes = await axios.get('/api/get-chatlog');
//         const currentLog = chatRes.data.chatlog || [];
        
//         const welcomeMsg = `Hello, I'm ${res.data.assistantname || 'Zyra'}, a virtual assistant created by Debashis, how can I assist you?`;
//         const hasWelcome = currentLog.some(msg => 
//           msg.role === 'assistant' && msg.content === welcomeMsg
//         );
        
//         if (!hasWelcome) {
//           // Add welcome to backend
//           await axios.post('/api/add-to-chatlog', { role: 'assistant', content: welcomeMsg });
          
//           // Add to local cache with unique ID
//           const welcomeObj = {
//             role: 'assistant',
//             content: welcomeMsg,
//             date: new Date().toISOString(),
//             id: `welcome-${Date.now()}`
//           };
          
//           setChatlogCache(prev => {
//             // FIXED: Check for exact content match before adding
//             const exists = prev.some(msg => msg.content === welcomeMsg && msg.role === 'assistant');
//             if (exists) return prev;
//             return [...prev, welcomeObj];
//           });
          
//           // FIXED: Status sequence + speak
//           setStatus('Answering ...');
//           stopCurrentAudio();
          
//           const audioRes = await axios.post('/api/text-to-speech', { 
//             text: welcomeMsg, 
//             email 
//           }, { responseType: 'blob' });
          
//           const audio = new Audio(URL.createObjectURL(audioRes.data));
//           currentAudioRef.current = audio;
//           window.currentAudio = audio;
//           audio.play().catch(err => {
//             console.error('Welcome audio play failed:', err);
//           });
          
//           console.log('Welcome message added and spoken');
//         }
//       } catch (err) {
//         console.error('Settings error:', err);
//         if (err.response?.status === 401) {
//           localStorage.removeItem('email');
//           localStorage.removeItem('token');
//           window.location.href = '/';
//         }
//         setStatus('Available');
//       }
//     };
//     fetchUserSettings();
//   }, []);

//   return (
//     <AuthContext.Provider value={{ user, setUser }}>
//       <AssistantContext.Provider value={{ assistant, setAssistant, status, setStatus, isProcessing, setIsProcessing, chatlogCache, setChatlogCache }}>
//         <Router>
//           <Routes>
//             <Route path="/" element={<Login />} />
//             <Route path="/signup" element={<Signup />} />
//             <Route path="/forgot" element={<ForgotPassword />} />
//             <Route path="/reset" element={<ResetPassword />} />
//             <Route path="/settings" element={<Settings />} />
//             <Route path="/home" element={<Home />} />
//             <Route path="/chat" element={<Chat />} />
//             <Route path="/history" element={<History />} />
//           </Routes>
//         </Router>
//       </AssistantContext.Provider>
//     </AuthContext.Provider>
//   );
// }

// export default App;