import { useState, useContext, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { AuthContext, AssistantContext } from '../App';
import Sidebar from '../components/Sidebar';
import BottomControls from '../components/BottomControls';
import AnimatedBackground from '../components/AnimatedBackground';
import AIChipAnimation from '../components/AIChipAnimation';
import voiceDefault from '../assets/voice-default.png';
import voiceFemale from '../assets/voice-female.png';
import voiceMale from '../assets/voice-male.png';

function Settings() {
  const { user, setUser } = useContext(AuthContext);
  const { assistant, setAssistant } = useContext(AssistantContext);
  const [name, setName] = useState(assistant?.name || 'Zyra');
  const [voice, setVoice] = useState(assistant?.voice || 'en-CA-ClaraNeural');
  const [username, setUsername] = useState(user?.username || '');
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');
  const navigate = useNavigate();
  
  const voices = [
    { id: 'en-CA-ClaraNeural', name: 'Clara', img: voiceDefault, accent: '🇨🇦', country: 'Canadian' },
    { id: 'en-US-AriaNeural', name: 'Aria', img: voiceFemale, accent: '🇺🇸', country: 'US' },
    { id: 'en-GB-RyanNeural', name: 'Ryan', img: voiceMale, accent: '🇬🇧', country: 'UK' },
  ];

  useEffect(() => {
    const fetchSettings = async () => {
      const email = localStorage.getItem('email');
      const token = localStorage.getItem('token');
      if (!email || !token) {
        navigate('/');
        return;
      }
      try {
        const res = await axios.post('/api/get-user-settings', { email }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setUser({
          email,
          username: res.data.username || '',
          assistantname: res.data.assistantname || 'Zyra',
          assistantvoice: res.data.assistantvoice || 'en-CA-ClaraNeural'
        });
        setAssistant({
          name: res.data.assistantname || 'Zyra',
          voice: res.data.assistantvoice || 'en-CA-ClaraNeural'
        });
        setUsername(res.data.username || '');
        setName(res.data.assistantname || 'Zyra');
        setVoice(res.data.assistantvoice || 'en-CA-ClaraNeural');
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem('email');
          localStorage.removeItem('token');
          navigate('/');
        }
      }
    };
    if (localStorage.getItem('token')) {
      fetchSettings();
    }
  }, [setUser, setAssistant, navigate]);

  const playSavedVoice = async (voiceId) => {
    try {
      const audioRes = await axios.post('/api/text-to-speech', 
        { 
          text: `Hello ${username || 'there'}! I'm ${name}, your assistant. Settings saved successfully!`,
          voice: voiceId,
          email: user?.email 
        }, 
        { responseType: 'blob' }
      );
      const audioUrl = URL.createObjectURL(audioRes.data);
      const audio = new Audio(audioUrl);
      audio.play().catch(console.error);
    } catch (error) {
      console.error('Voice API error:', error);
    }
  };

  const handleSave = async () => {
    const email = localStorage.getItem('email');
    const token = localStorage.getItem('token');
    if (!email || !token) {
      alert('Please log in to save settings');
      navigate('/');
      return;
    }

    setIsSaving(true);
    setSaveStatus('Saving...');

    try {
      await axios.post('/api/settings', {
        email,
        username,
        assistantname: name,
        assistantvoice: voice
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAssistant({ name, voice });
      setUser({ ...user, username, assistantname: name, assistantvoice: voice });
      
      setSaveStatus('Saved successfully! ✅');
      await playSavedVoice(voice);
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (err) {
      setSaveStatus('Error saving settings ❌');
      setTimeout(() => setSaveStatus(''), 3000);
      if (err.response?.status === 401) {
        localStorage.removeItem('email');
        localStorage.removeItem('token');
        navigate('/');
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <motion.div 
      className="flex min-h-screen bg-gray-900 text-white" 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 0.5 }}
    >
      <Sidebar />
      
      <div className="flex-1 p-3 md:p-6 relative overflow-hidden">
        <AnimatedBackground />
        
        {/* Single Card Layout */}
        <div className="relative z-10 h-full flex flex-col items-center justify-center">
          {/* Compact Settings Card */}
          <motion.div 
            className="w-full max-w-md bg-gradient-to-br from-gray-900/95 to-gray-950/95 backdrop-blur-xl rounded-2xl border border-cyan-500/30 shadow-2xl p-4 md:p-6"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            {/* Header */}
            <div className="text-center mb-4">
              <h2 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-cyan-200 to-cyan-300 bg-clip-text text-transparent">
                Settings
              </h2>
              <p className="text-cyan-200/70 text-xs md:text-sm mt-1">
                Customize your assistant
              </p>
            </div>

            {/* User Settings - Compact */}
            <div className="space-y-3 mb-4">
              <div>
                <label className="block text-cyan-200 mb-1 text-xs md:text-sm">Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  className="w-full p-2 text-sm bg-gray-800/50 border border-cyan-500/30 rounded-lg text-white focus:outline-none focus:border-cyan-400"
                  placeholder="Your username"
                />
              </div>

              <div>
                <label className="block text-cyan-200 mb-1 text-xs md:text-sm">Assistant Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full p-2 text-sm bg-gray-800/50 border border-cyan-500/30 rounded-lg text-white focus:outline-none focus:border-cyan-400"
                  placeholder="Assistant name"
                />
              </div>
            </div>

            {/* Voice Selection - Horizontal Compact */}
            <div className="mb-4">
              <label className="block text-cyan-200 mb-2 text-xs md:text-sm">Voice Preference</label>
              <div className="flex justify-between gap-2">
                {voices.map((v) => (
                  <motion.div 
                    key={v.id} 
                    className={`flex-1 cursor-pointer text-center p-2 rounded-lg border transition-all duration-200 ${
                      voice === v.id 
                        ? 'bg-cyan-500/20 border-cyan-400 shadow' 
                        : 'bg-gray-800/30 border-cyan-500/20 hover:bg-cyan-500/10'
                    }`}
                    onClick={() => setVoice(v.id)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <div className="flex flex-col items-center">
                      <img 
                        src={v.img} 
                        alt={v.name} 
                        className="w-8 h-8 md:w-10 md:h-10 rounded-full border border-cyan-500/30" 
                      />
                      <span className="text-lg -mt-1">{v.accent}</span>
                      <span className="text-white text-xs font-medium mt-1">{v.name}</span>
                      <span className="text-cyan-300/70 text-[10px]">{v.country}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2">
              <button 
                onClick={handleSave} 
                disabled={isSaving}
                className="w-full py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg font-medium hover:from-cyan-700 hover:to-blue-700 disabled:opacity-50 transition-all duration-200 text-sm flex items-center justify-center gap-2"
              >
                {isSaving ? (
                  <>
                    <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Save Settings
                  </>
                )}
              </button>
              
              <Link 
                to="/home" 
                className="w-full py-2 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg font-medium hover:from-gray-700 hover:to-gray-800 transition-all duration-200 text-sm flex items-center justify-center gap-2"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Home
              </Link>
            </div>

            {/* Save Status */}
            <AnimatePresence>
              {saveStatus && (
                <motion.p
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="text-center mt-2 text-cyan-400 text-xs font-medium"
                >
                  {saveStatus}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
          {/* Responsive Bottom Controls */}
        <div className="w-full flex justify-center mt-2">
          <div className="w-full max-w-2xl">
            <BottomControls />
          </div>
        </div>

        {/* AI Chip Animations */}
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

export default Settings;


















// import { useState, useContext, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { motion } from 'framer-motion';
// import axios from 'axios';
// import { AuthContext, AssistantContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import bigGif from '../assets/big-gif.gif';
// import voiceDefault from '../assets/voice-default.png';
// import voiceFemale from '../assets/voice-female.png';
// import voiceMale from '../assets/voice-male.png';

// function Settings() {
//   const { user, setUser } = useContext(AuthContext);
//   const { assistant, setAssistant, status } = useContext(AssistantContext);
//   const [name, setName] = useState(assistant?.name || 'Zyra');
//   const [voice, setVoice] = useState(assistant?.voice || 'en-CA-ClaraNeural');
//   const [username, setUsername] = useState(user?.username || '');
//   const navigate = useNavigate();
//   const voices = [
//     { id: 'en-CA-ClaraNeural', name: 'Clara (Canadian)', img: voiceDefault },
//     { id: 'en-US-AriaNeural', name: 'Aria (US)', img: voiceFemale },
//     { id: 'en-GB-RyanNeural', name: 'Ryan (UK)', img: voiceMale },
//   ];

//   useEffect(() => {
//     const fetchSettings = async () => {
//       const email = localStorage.getItem('email');
//       const token = localStorage.getItem('token');
//       if (!email || !token) {
//         console.error('Missing email or token in localStorage');
//         alert('Error loading settings. Please log in again.');
//         navigate('/');
//         return;
//       }
//       try {
//         const res = await axios.post('/api/get-user-settings', { email }, {
//           headers: { Authorization: `Bearer ${token}` }
//         });
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
//         setUsername(res.data.username || '');
//         setName(res.data.assistantname || 'Zyra');
//         setVoice(res.data.assistantvoice || 'en-CA-ClaraNeural');
//       } catch (err) {
//         console.error('Settings fetch error:', err);
//         if (err.response?.status === 401) {
//           alert('Session expired. Please log in again.');
//           localStorage.removeItem('email');
//           localStorage.removeItem('token');
//           navigate('/');
//         } else {
//           alert('Error loading settings. Please log in again.');
//         }
//       }
//     };
//     if (localStorage.getItem('token')) {
//       fetchSettings();
//     }
//   }, [setUser, setAssistant, navigate]);

//   const handleSave = async () => {
//     const email = localStorage.getItem('email');
//     const token = localStorage.getItem('token');
//     if (!email || !token) {
//       console.error('No email or token in localStorage');
//       alert('Please log in to save settings');
//       navigate('/');
//       return;
//     }
//     try {
//       await axios.post('/api/settings', {
//         email,
//         username,
//         assistantname: name,
//         assistantvoice: voice
//       }, {
//         headers: { Authorization: `Bearer ${token}` }
//       });
//       setAssistant({ name, voice });
//       setUser({ ...user, username, assistantname: name, assistantvoice: voice });
//       alert('Settings saved successfully');
//     } catch (err) {
//       console.error('Settings save error:', err);
//       if (err.response?.status === 401) {
//         alert('Session expired. Please log in again.');
//         localStorage.removeItem('email');
//         localStorage.removeItem('token');
//         navigate('/');
//       } else {
//         alert('Error saving settings: ' + err.message);
//       }
//     }
//   };

//   return (
//     <motion.div 
//       className="flex min-h-screen bg-gray-900 text-white" 
//       initial={{ opacity: 0 }} 
//       animate={{ opacity: 1 }} 
//       transition={{ duration: 0.5, ease: 'easeInOut' }}
//     >
//       <Sidebar />
//       <div className="flex-1 p-4 md:p-8 relative">
//         {/* 🔹 Status Display */}
//         <motion.p 
//           className="absolute top-4 right-4 text-gray-300 font-semibold"
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//           transition={{ delay: 0.5, duration: 0.5 }}
//         >
//           Status: {status}
//         </motion.p>

//         <motion.div 
//           className="p-8 bg-gray-800 rounded-lg shadow-md w-full max-w-md mx-auto"
//           initial={{ scale: 0.9, opacity: 0 }}
//           animate={{ scale: 1, opacity: 1 }}
//           transition={{ duration: 0.5 }}
//         >
//           <h2 className="text-2xl mb-4 text-center">Settings</h2>
//           <label className="block mb-2">Username:</label>
//           <input
//             type="text"
//             value={username}
//             onChange={e => setUsername(e.target.value)}
//             className="border border-gray-700 p-2 mb-4 w-full rounded bg-gray-900 text-white"
//             placeholder="Enter username"
//           />
//           <label className="block mb-2">Assistant Name:</label>
//           <input
//             type="text"
//             value={name}
//             onChange={e => setName(e.target.value)}
//             className="border border-gray-700 p-2 mb-4 w-full rounded bg-gray-900 text-white"
//             placeholder="Enter assistant name"
//           />
//           <label className="block mb-2">Voice:</label>
//           <div className="flex space-x-4 mb-4">
//             {voices.map(v => (
//               <motion.div 
//                 key={v.id} 
//                 className={`cursor-pointer ${voice === v.id ? 'border-2 border-blue-500' : ''} rounded-lg`}
//                 onClick={() => setVoice(v.id)}
//                 whileHover={{ scale: 1.05 }}
//                 transition={{ duration: 0.2 }}
//               >
//                 <img src={v.img} alt={v.name} className="w-16 h-16 rounded-full" />
//                 <p className="text-center text-gray-300">{v.name}</p>
//               </motion.div>
//             ))}
//           </div>
//           <button onClick={handleSave} className="bg-blue-600 text-white p-2 w-full rounded hover:bg-blue-700 transition-colors">Save</button>
//           <p className="mt-2 text-center"><Link to="/home" className="text-blue-400 hover:underline">Back to Home</Link></p>
//         </motion.div>
//         <BottomControls />
//         <img src={bigGif} alt="Small GIF" className="w-28 h-28 absolute bottom-4 right-4 opacity-50" />
//       </div>
//     </motion.div>
//   );
// }

// export default Settings;










// import { useState, useContext, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { motion } from 'framer-motion';
// import axios from 'axios';
// import { AuthContext, AssistantContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import StatusDisplay from '../components/StatusDisplay';
// import bigGif from '../assets/big-gif.gif';
// import voiceDefault from '../assets/voice-default.png';
// import voiceFemale from '../assets/voice-female.png';
// import voiceMale from '../assets/voice-male.png';
// import profileImg from '../assets/profile.png';

// function Settings() {
//   const { user, setUser } = useContext(AuthContext);
//   const { assistant, setAssistant } = useContext(AssistantContext);
//   const [name, setName] = useState(assistant?.name || 'Zyra');
//   const [voice, setVoice] = useState(assistant?.voice || 'en-CA-ClaraNeural');
//   const [username, setUsername] = useState(user?.username || '');
//   const [profilePic, setProfilePic] = useState(null);
//   const [saving, setSaving] = useState(false);
//   const [error, setError] = useState('');
//   const navigate = useNavigate();

//   const voices = [
//     { 
//       id: 'en-CA-ClaraNeural', 
//       name: 'Clara (Canadian)', 
//       img: voiceDefault,
//       previewText: "Hello, I'm your assistant Clara with a warm Canadian voice."
//     },
//     { 
//       id: 'en-US-AriaNeural', 
//       name: 'Aria (US)', 
//       img: voiceFemale,
//       previewText: "Hi there! I'm Aria, your friendly American assistant."
//     },
//     { 
//       id: 'en-GB-RyanNeural', 
//       name: 'Ryan (UK)', 
//       img: voiceMale,
//       previewText: "Hello! This is Ryan speaking with a proper British accent."
//     },
//   ];

//   // FIXED: Load settings + profile pic
//   useEffect(() => {
//     const loadSettings = async () => {
//       const email = localStorage.getItem('email');
//       const token = localStorage.getItem('token');
      
//       if (!email || !token) {
//         navigate('/');
//         return;
//       }

//       try {
//         const [settingsRes, profileRes] = await Promise.all([
//           axios.post('/api/get-user-settings', { email }, {
//             headers: { Authorization: `Bearer ${token}` }
//           }),
//           axios.post('/api/get-profile-pic', { email }, {
//             headers: { Authorization: `Bearer ${token}` }
//           })
//         ]);

//         const settings = settingsRes.data;
//         setUser({
//           email,
//           username: settings.username || '',
//           assistantname: settings.assistantname || 'Zyra',
//           assistantvoice: settings.assistantvoice || 'en-CA-ClaraNeural'
//         });
        
//         setAssistant({
//           name: settings.assistantname || 'Zyra',
//           voice: settings.assistantvoice || 'en-CA-ClaraNeural'
//         });
        
//         setUsername(settings.username || '');
//         setName(settings.assistantname || 'Zyra');
//         setVoice(settings.assistantvoice || 'en-CA-ClaraNeural');
        
//         // FIXED: Load profile picture
//         if (profileRes.data.profilePic) {
//           setProfilePic(profileRes.data.profilePic);
//           localStorage.setItem('profilePic', profileRes.data.profilePic);
//         }
        
//       } catch (err) {
//         console.error('Settings load error:', err);
//         if (err.response?.status === 401) {
//           localStorage.removeItem('email');
//           localStorage.removeItem('token');
//           navigate('/');
//         } else {
//           setError('Failed to load settings');
//         }
//       }
//     };

//     loadSettings();
//   }, [navigate, setUser, setAssistant]);

//   // FIXED: Profile picture upload
//   const handleProfileUpload = async (e) => {
//     const file = e.target.files[0];
//     if (!file || !file.type.startsWith('image/')) {
//       setError('Please select a valid image file');
//       return;
//     }

//     if (file.size > 2 * 1024 * 1024) { // 2MB limit
//       setError('Image size must be less than 2MB');
//       return;
//     }

//     const reader = new FileReader();
//     reader.onload = async (e) => {
//       const base64 = e.target.result;
//       setProfilePic(base64);
      
//       try {
//         const email = localStorage.getItem('email');
//         const token = localStorage.getItem('token');
//         await axios.post('/api/update-profile-pic', { 
//           email, 
//           profilePic: base64 
//         }, {
//           headers: { Authorization: `Bearer ${token}` }
//         });
//         localStorage.setItem('profilePic', base64);
//         setError('');
//       } catch (err) {
//         console.error('Profile save error:', err);
//         setError('Failed to save profile picture');
//       }
//     };
//     reader.readAsDataURL(file);
//   };

//   // FIXED: Voice preview
//   const previewVoice = async (voiceId, previewText) => {
//     try {
//       const email = localStorage.getItem('email');
//       const audioRes = await axios.post('/api/text-to-speech', { 
//         text: previewText, 
//         voice: voiceId,
//         email 
//       }, { responseType: 'blob' });
      
//       const audio = new Audio(URL.createObjectURL(audioRes.data));
//       audio.play().catch(err => {
//         console.error('Voice preview error:', err);
//         alert('Preview not available. Please check your browser settings.');
//       });
//     } catch (err) {
//       console.error('Voice preview error:', err);
//     }
//   };

//   const handleSave = async () => {
//     if (!username.trim() || !name.trim()) {
//       setError('Username and assistant name are required');
//       return;
//     }

//     setSaving(true);
//     setError('');
    
//     const email = localStorage.getItem('email');
//     const token = localStorage.getItem('token');
    
//     try {
//       await axios.post('/api/settings', {
//         email,
//         username: username.trim(),
//         assistantname: name.trim(),
//         assistantvoice: voice
//       }, {
//         headers: { Authorization: `Bearer ${token}` }
//       });
      
//       setAssistant({ name: name.trim(), voice });
//       setUser(prev => ({ 
//         ...prev, 
//         username: username.trim(),
//         assistantname: name.trim(),
//         assistantvoice: voice 
//       }));
      
//       // FIXED: Success feedback
//       const successMsg = document.createElement('div');
//       successMsg.textContent = 'Settings saved successfully!';
//       successMsg.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
//       document.body.appendChild(successMsg);
      
//       setTimeout(() => {
//         successMsg.remove();
//       }, 3000);
      
//     } catch (err) {
//       console.error('Settings save error:', err);
//       if (err.response?.status === 401) {
//         localStorage.removeItem('email');
//         localStorage.removeItem('token');
//         navigate('/');
//       } else {
//         setError(err.response?.data?.error || 'Failed to save settings');
//       }
//     } finally {
//       setSaving(false);
//     }
//   };

//   return (
//     <motion.div 
//       className="flex min-h-screen bg-gray-900 text-white" 
//       initial={{ opacity: 0 }} 
//       animate={{ opacity: 1 }} 
//       transition={{ duration: 0.5 }}
//     >
//       <Sidebar />
      
//       <div className="flex-1 p-4 md:p-8 relative min-h-screen flex flex-col">
//         <motion.div 
//           className="max-w-md mx-auto w-full space-y-6"
//           initial={{ opacity: 0, y: 20 }}
//           animate={{ opacity: 1, y: 0 }}
//           transition={{ duration: 0.5 }}
//         >
//           {/* Header */}
//           <motion.div 
//             className="text-center mb-8"
//             initial={{ scale: 0.9 }}
//             animate={{ scale: 1 }}
//           >
//             <h1 className="text-3xl font-bold mb-2">⚙️ Settings</h1>
//             <p className="text-gray-400">Customize your assistant experience</p>
//           </motion.div>

//           {/* Profile Picture */}
//           <motion.div 
//             className="bg-gray-800 rounded-xl p-6"
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ delay: 0.1 }}
//           >
//             <label className="block text-sm font-medium mb-3 text-gray-300">
//               Profile Picture
//             </label>
//             <div className="flex items-center space-x-4">
//               <div className="relative">
//                 <img 
//                   src={profilePic || profileImg} 
//                   alt="Profile" 
//                   className="w-20 h-20 rounded-full object-cover border-2 border-gray-600"
//                 />
//                 <div className="absolute -bottom-1 -right-1 bg-blue-600 p-1 rounded-full">
//                   <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
//                     <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
//                   </svg>
//                 </div>
//               </div>
              
//               <input
//                 type="file"
//                 accept="image/*"
//                 onChange={handleProfileUpload}
//                 className="hidden"
//                 id="profile-upload"
//               />
//               <label 
//                 htmlFor="profile-upload" 
//                 className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg cursor-pointer transition-colors whitespace-nowrap"
//               >
//                 Change Photo
//               </label>
//             </div>
//           </motion.div>

//           {/* Username */}
//           <motion.div 
//             className="bg-gray-800 rounded-xl p-6"
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ delay: 0.2 }}
//           >
//             <label className="block text-sm font-medium mb-3 text-gray-300">
//               Your Name
//             </label>
//             <input
//               type="text"
//               value={username}
//               onChange={e => setUsername(e.target.value)}
//               className="w-full border border-gray-600 p-3 rounded-lg bg-gray-900 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
//               placeholder="Enter your display name"
//               maxLength={50}
//             />
//           </motion.div>

//           {/* Assistant Name */}
//           <motion.div 
//             className="bg-gray-800 rounded-xl p-6"
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ delay: 0.3 }}
//           >
//             <label className="block text-sm font-medium mb-3 text-gray-300">
//               Assistant Name
//             </label>
//             <input
//               type="text"
//               value={name}
//               onChange={e => setName(e.target.value)}
//               className="w-full border border-gray-600 p-3 rounded-lg bg-gray-900 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
//               placeholder="Enter assistant name (e.g., Zyra, Jarvis)"
//               maxLength={30}
//             />
//           </motion.div>

//           {/* Voice Selection */}
//           <motion.div 
//             className="bg-gray-800 rounded-xl p-6"
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ delay: 0.4 }}
//           >
//             <label className="block text-sm font-medium mb-4 text-gray-300">
//               Assistant Voice
//             </label>
            
//             <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
//               {voices.map((v, index) => (
//                 <motion.div
//                   key={v.id}
//                   className={`relative cursor-pointer rounded-lg p-3 border-2 transition-all ${
//                     voice === v.id 
//                       ? 'border-blue-500 bg-blue-500/10' 
//                       : 'border-gray-600 hover:border-gray-500'
//                   }`}
//                   onClick={() => setVoice(v.id)}
//                   initial={{ opacity: 0, y: 20 }}
//                   animate={{ opacity: 1, y: 0 }}
//                   transition={{ delay: index * 0.1 }}
//                   whileHover={{ scale: 1.02 }}
//                 >
//                   {/* Voice Image */}
//                   <div className="flex justify-center mb-2">
//                     <img 
//                       src={v.img} 
//                       alt={v.name} 
//                       className={`w-16 h-16 rounded-full object-cover ${
//                         voice === v.id ? 'ring-2 ring-blue-500' : ''
//                       }`} 
//                     />
//                   </div>
                  
//                   {/* Voice Info */}
//                   <div className="text-center">
//                     <p className="font-medium text-sm">{v.name}</p>
//                     <p className="text-xs text-gray-400 mt-1">{v.id}</p>
//                   </div>
                  
//                   {/* FIXED: Preview Button */}
//                   <button
//                     onClick={(e) => {
//                       e.stopPropagation();
//                       previewVoice(v.id, v.previewText);
//                     }}
//                     className="absolute top-2 right-2 p-1 bg-gray-700 hover:bg-gray-600 rounded-full transition-colors"
//                     title="Preview voice"
//                   >
//                     <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
//                       <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
//                     </svg>
//                   </button>
                  
//                   {/* Selection Indicator */}
//                   {voice === v.id && (
//                     <motion.div
//                       className="absolute -bottom-1 -right-1 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center"
//                       layoutId="voice-selection"
//                     >
//                       <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
//                         <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
//                       </svg>
//                     </motion.div>
//                   )}
//                 </motion.div>
//               ))}
//             </div>
//           </motion.div>

//           {/* Error Display */}
//           {error && (
//             <motion.div 
//               className="bg-red-900/20 border border-red-500 text-red-300 p-3 rounded-lg"
//               initial={{ opacity: 0, y: -10 }}
//               animate={{ opacity: 1, y: 0 }}
//             >
//               ⚠️ {error}
//             </motion.div>
//           )}

//           {/* Save Button */}
//           <motion.div 
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ delay: 0.6 }}
//           >
//             <button 
//               onClick={handleSave}
//               disabled={saving || !username.trim() || !name.trim()}
//               className={`w-full py-3 px-6 rounded-lg font-medium transition-all ${
//                 saving || !username.trim() || !name.trim()
//                   ? 'bg-gray-600 cursor-not-allowed'
//                   : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
//               } text-white`}
//             >
//               {saving ? (
//                 <div className="flex items-center justify-center space-x-2">
//                   <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
//                   <span>Saving...</span>
//                 </div>
//               ) : (
//                 '💾 Save Settings'
//               )}
//             </button>
//           </motion.div>
//         </motion.div>

//         {/* Status and Controls */}
//         <StatusDisplay status={saving ? 'Saving...' : 'Settings Ready'} />
//         <div className="pb-20 md:pb-8">
//           <BottomControls />
//         </div>

//         <img src={bigGif} alt="Assistant" className="w-20 h-20 absolute bottom-4 right-4 opacity-50 hidden md:block" />
//       </div>
//     </motion.div>
//   );
// }

// export default Settings;