import { useContext, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AssistantContext, AuthContext } from '../App';
import Sidebar from '../components/Sidebar';
import BottomControls from '../components/BottomControls';
import AnimatedBackground from '../components/AnimatedBackground';
import AIChipAnimation from '../components/AIChipAnimation';
import profileImg from '../assets/profile.png';

function Home() {
  const { setIsProcessing, setStatus, assistant } = useContext(AssistantContext);
  const { isAuthenticated } = useContext(AuthContext);
  const navigate = useNavigate();

  // Reset assistant state on mount
  useEffect(() => {
    setIsProcessing(false);
    setStatus('Available');
  }, [setIsProcessing, setStatus]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <motion.div 
      className="flex min-h-screen text-white" 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 0.5, ease: 'easeInOut' }}
    >
      {/* Sidebar stays visible */}
      <Sidebar />

      {/* Right content area with animated background */}
      <div className="flex-1 relative overflow-hidden">
        {/* Animated Canvas Background */}
        <AnimatedBackground />
        
        {/* Permanent Central AI Animation */}
        <div className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none">
          <div className="relative w-64 h-64">
            {/* Outer orb */}
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-blue-500/30"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.7, 1, 0.7],
                rotate: 360
              }}
              transition={{
                scale: { duration: 4, repeat: Infinity },
                opacity: { duration: 4, repeat: Infinity },
                rotate: { duration: 20, repeat: Infinity, ease: "linear" }
              }}
            />
            
            {/* Middle orb */}
            <motion.div
              className="absolute inset-4 rounded-full border-2 border-cyan-400/40"
              animate={{
                scale: [1, 1.1, 1],
                opacity: [0.6, 0.9, 0.6],
                rotate: -360
              }}
              transition={{
                scale: { duration: 3, repeat: Infinity, delay: 0.5 },
                opacity: { duration: 3, repeat: Infinity, delay: 0.5 },
                rotate: { duration: 15, repeat: Infinity, ease: "linear" }
              }}
            />
            
            {/* Inner orb */}
            <motion.div
              className="absolute inset-8 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600"
              animate={{
                scale: [1, 1.05, 1],
                boxShadow: [
                  "0 0 20px rgba(0, 255, 255, 0.5)",
                  "0 0 40px rgba(0, 255, 255, 0.8)",
                  "0 0 20px rgba(0, 255, 255, 0.5)"
                ]
              }}
              transition={{
                duration: 2,
                repeat: Infinity
              }}
            />
            
            {/* Central core */}
            <motion.div
              className="absolute inset-12 rounded-full bg-white"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [1, 0.8, 1],
                rotate: 360
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity
              }}
            />
            
            {/* Floating particles */}
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-2 h-2 bg-cyan-400 rounded-full"
                style={{
                  left: `${50 + 40 * Math.cos((i / 8) * 2 * Math.PI)}%`,
                  top: `${50 + 40 * Math.sin((i / 8) * 2 * Math.PI)}%`,
                  transform: 'translate(-50%, -50%)'
                }}
                animate={{
                  scale: [0.5, 1.2, 0.5],
                  opacity: [0, 1, 0],
                  rotate: 360
                }}
                transition={{
                  duration: 2 + i * 0.5,
                  repeat: Infinity,
                  delay: i * 0.3
                }}
              />
            ))}
            
            {/* Assistant Name - Positioned in the center */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <motion.div
                className="text-cyan-600 text-2xl font-mono font-bold uppercase  mb-1 drop-shadow-lg z-30"
                animate={{
                  textShadow: [
                    "0 0 8px rgba(0, 255, 255, 0.6)",
                    "0 0 25px rgba(0, 255, 255, 0.9)",
                    "0 0 8px rgba(0, 255, 255, 0.6)"
                  ]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity
                }}
              >
                {assistant?.name || 'Zyra'}
              </motion.div>
              <motion.div
                className="text-blue-300 text-xs font-mono tracking-wider z-30"
                animate={{
                  opacity: [0.7, 1, 0.7]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity
                }}
              >
                AI SYSTEM ACTIVE
              </motion.div>
            </div>
          </div>
        </div>

        {/* Bottom Corner AI Chip Animation - Hidden on Mobile */}
        <div className="hidden md:block absolute bottom-0 left-4 z-20 pointer-events-none">
          <div className="scale-75">
            <AIChipAnimation size="sm" />
          </div>
        </div> 
        <div className="hidden md:block absolute bottom-0 right-4 z-20 pointer-events-none">
          <div className="scale-75">
            <AIChipAnimation size="sm" />
          </div>
        </div>
        
        <div className="relative z-10 p-4 md:p-8 flex flex-col items-center justify-center h-full">
          <motion.div 
            className="absolute top-4 right-4"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
          >
            <Link to="/settings">
              <img 
                src={profileImg} 
                alt="Profile" 
                className="fixed top-8 right-4 w-10 h-10 rounded-full border-2 border-blue-500 hover:scale-105 transition-transform" 
              />
            </Link>
          </motion.div>

          <div className="w-full flex justify-center">
            <BottomControls />
          </div>
        </div>
      </div>

      {/* Add CSS for blending directly in the component */}
      <style>
        {`
          .gif-blended {
            mix-blend-mode: screen;
            opacity: 0.9;
            filter: contrast(1.1) brightness(1.1);
          }
          
          .gif-container {
            background: transparent;
            border-radius: 12px;
            overflow: hidden;
          }
          
          @media (max-width: 768px) {
            .gif-blended {
              mix-blend-mode: screen;
              opacity: 0.85;
            }
          }
        `}
      </style>
    </motion.div>
  );
}

export default Home;

























// import { useContext, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { motion } from 'framer-motion';
// import { AssistantContext, AuthContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import bigGif from '../assets/big-gif.gif';
// import profileImg from '../assets/profile.png';
// import bgGif from '../assets/bg-gif.gif';

// function Home() {
//   const { setIsProcessing, setStatus, status } = useContext(AssistantContext);
//   const { isAuthenticated } = useContext(AuthContext);
//   const navigate = useNavigate();

//   // Reset assistant state on mount
//   useEffect(() => {
//     setIsProcessing(false);
//     setStatus('Available');
//   }, [setIsProcessing, setStatus]);

//   useEffect(() => {
//     if (!isAuthenticated) {
//       navigate('/');
//     }
//   }, [isAuthenticated, navigate]);

//   if (!isAuthenticated) {
//     return null;
//   }

//   return (
//     <motion.div 
//       className="flex min-h-screen text-white" 
//       initial={{ opacity: 0 }} 
//       animate={{ opacity: 1 }} 
//       transition={{ duration: 0.5, ease: 'easeInOut' }}
//     >
//       {/* Sidebar stays visible */}
//       <Sidebar />

//       {/* Right content area with background gif */}
//       <div className="flex-1 relative">
//         {/* Background only for right side */}
//         <div 
//           className="absolute inset-0 w-full h-full bg-cover bg-center"
//           style={{ backgroundImage: `url(${bgGif})` }}
//         ></div>

//         <div className="relative z-10 p-4 md:p-8 flex flex-col items-center justify-center h-full">
//           <motion.div 
//             className="absolute top-4 right-4"
//             initial={{ y: -20, opacity: 0 }}
//             animate={{ y: 0, opacity: 1 }}
//             transition={{ delay: 0.2, duration: 0.5 }}
//           >
//             <Link to="/settings">
//               <img 
//                 src={profileImg} 
//                 alt="Profile" 
//                 className="w-10 h-10 rounded-full border-2 border-blue-500 hover:scale-105 transition-transform" 
//               />
//             </Link>
//           </motion.div>

//           {/* Big GIF with perfect blending to remove black background */}
//           <motion.div 
//             className="w-[70vw] max-w-[600px] h-auto mb-4 relative gif-container"
//             initial={{ scale: 0.8, opacity: 0 }}
//             animate={{ scale: 1, opacity: 1 }}
//             transition={{ delay: 0.4, duration: 0.5, ease: 'easeOut' }}
//           >
//             <img 
//               src={bigGif} 
//               alt="Assistant" 
//               className="w-full h-full gif-blended" 
//             />
//           </motion.div>
          
//           {/* Status Display */}
//           <motion.p 
//             className="text-lg font-semibold text-gray-300 mb-4 px-4 py-2 rounded-lg bg-black bg-opacity-40"
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ delay: 0.8, duration: 0.5 }}
//           >
//             Status: {status}
//           </motion.p>

//           <div className="w-full flex justify-center">
//             <BottomControls />
//           </div>

//           <div className="w-30 h-20 absolute bottom-4 right-4 gif-container">
//             <img 
//               src={bigGif} 
//               alt="Small GIF" 
//               className="w-full h-full gif-blended" 
//             />
//           </div>
//         </div>
//       </div>

//       {/* Add CSS for blending directly in the component */}
//       <style>
//         {`
//           .gif-blended {
//             mix-blend-mode: screen;
//             opacity: 0.9;
//             filter: contrast(1.1) brightness(1.1);
//           }
          
//           .gif-container {
//             background: transparent;
//             border-radius: 12px;
//             overflow: hidden;
//           }
          
//           @media (max-width: 768px) {
//             .gif-blended {
//               mix-blend-mode: screen;
//               opacity: 0.85;
//             }
//           }
//         `}
//       </style>
//     </motion.div>
//   );
// }

// export default Home;















// import { useContext, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { motion } from 'framer-motion';
// import { AssistantContext, AuthContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import bigGif from '../assets/big-gif.gif';
// import profileImg from '../assets/profile.png';
// import bgGif from '../assets/bg-gif.gif';

// function Home() {
//   const { setIsProcessing, setStatus, status } = useContext(AssistantContext); // ADDED: status
//   const { isAuthenticated } = useContext(AuthContext);
//   const navigate = useNavigate();

//   // Reset assistant state on mount
//   useEffect(() => {
//     setIsProcessing(false);
//     setStatus('Available');
//   }, [setIsProcessing, setStatus]);

//   useEffect(() => {
//     if (!isAuthenticated) {
//       navigate('/');
//     }
//   }, [isAuthenticated, navigate]);

//   if (!isAuthenticated) {
//     return null;
//   }

//   return (
//     <motion.div 
//       className="flex min-h-screen text-white" 
//       initial={{ opacity: 0 }} 
//       animate={{ opacity: 1 }} 
//       transition={{ duration: 0.5, ease: 'easeInOut' }}
//     >
//       {/* Sidebar stays visible */}
//       <Sidebar />

//       {/* Right content area with background gif */}
//       <div className="flex-1 relative">
//         {/* Background only for right side */}
//         <div 
//           className="absolute inset-0 w-full h-full bg-cover bg-center"
//           style={{ backgroundImage: `url(${bgGif})` }}
//         ></div>

//         <div className="relative z-10 p-4 md:p-8 flex flex-col items-center justify-center h-full">
//           <motion.div 
//             className="absolute top-4 right-4"
//             initial={{ y: -20, opacity: 0 }}
//             animate={{ y: 0, opacity: 1 }}
//             transition={{ delay: 0.2, duration: 0.5 }}
//           >
//             <Link to="/settings">
//               <img 
//                 src={profileImg} 
//                 alt="Profile" 
//                 className="w-10 h-10 rounded-full border-2 border-blue-500 hover:scale-105 transition-transform" 
//               />
//             </Link>
//           </motion.div>

//           {/* <motion.img 
//             src={bigGif} 
//             alt="Assistant" 
//             className="w-[70vw] max-w-[600px] h-auto mb-4 mix-blend-lighten opacity-80" 
//             initial={{ scale: 0.8, opacity: 0 }}
//             animate={{ scale: 1, opacity: 1 }}
//             transition={{ delay: 0.4, duration: 0.5, ease: 'easeOut' }}
//           />  */}
          
//           {/* FIXED: Status Display - Now shows actual status */}
//           <motion.p 
//             className="text-lg font-semibold text-gray-300 mb-4  px-4 py-2 rounded-lg"
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ delay: 0.8, duration: 0.5 }}
//           >
//           </motion.p>

//           <div className="w-full flex justify-center">
//             <BottomControls />
//           </div>

//           <img 
//             src={bigGif} 
//             alt="Small GIF" 
//             className="w-30 h-20 absolute bottom-4 right-4 opacity-70" 
//           />
//         </div>
//       </div>
//     </motion.div>
//   );
// }

// export default Home;













// import { useContext, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { motion } from 'framer-motion';
// import { AssistantContext, AuthContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import bigGif from '../assets/big-gif.gif';
// import profileImg from '../assets/profile.png';
// import bgGif from '../assets/bg-gif.gif'; // 🔹 background gif

// function Home() {
//   const { setIsProcessing, setStatus } = useContext(AssistantContext);
//   const { isAuthenticated } = useContext(AuthContext);
//   const navigate = useNavigate();

//   // 🔹 Reset assistant state on mount
//   useEffect(() => {
//     setIsProcessing(false);
//     setStatus('Available');
//   }, [setIsProcessing, setStatus]);

//   useEffect(() => {
//     if (!isAuthenticated) {
//       navigate('/');
//     }
//   }, [isAuthenticated, navigate]);

//   if (!isAuthenticated) {
//     return null;
//   }

//   return (
//     <motion.div 
//       className="flex min-h-screen text-white" 
//       initial={{ opacity: 0 }} 
//       animate={{ opacity: 1 }} 
//       transition={{ duration: 0.5, ease: 'easeInOut' }}
//     >
//       {/* Sidebar stays visible */}
//       <Sidebar />

//       {/* 🔹 Right content area with background gif */}
//       <div className="flex-1 relative">
//         {/* Background only for right side */}
//         <div 
//           className="absolute inset-0 w-full h-full bg-cover bg-center"
//           style={{ backgroundImage: `url(${bgGif})` }}
//         ></div>

//         <div className="relative z-10 p-4 md:p-8 flex flex-col items-center justify-center h-full">
//           <motion.div 
//             className="absolute top-4 right-4"
//             initial={{ y: -20, opacity: 0 }}
//             animate={{ y: 0, opacity: 1 }}
//             transition={{ delay: 0.2, duration: 0.5 }}
//           >
//             <Link to="/settings">
//               <img 
//                 src={profileImg} 
//                 alt="Profile" 
//                 className="w-10 h-10 rounded-full border-2 border-blue-500 hover:scale-105 transition-transform" 
//               />
//             </Link>
//           </motion.div>

//           <motion.img 
//             src={bigGif} 
//             alt="Assistant" 
//             className="w-[70vw] max-w-[600px] h-auto mb-4" 
//             initial={{ scale: 0.8, opacity: 0 }}
//             animate={{ scale: 1, opacity: 1 }}
//             transition={{ delay: 0.4, duration: 0.5, ease: 'easeOut' }}
//           /> 
//           {/* 🔹 Status Display */}
//           <motion.p 
//             className="text-lg font-semibold text-gray-300 mb-4"
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ delay: 0.8, duration: 0.5 }}
//           >
//           </motion.p>

//           <div className="w-full flex justify-center">
//             <BottomControls />
//           </div>

//           <img 
//             src={bigGif} 
//             alt="Small GIF" 
//             className="w-20 h-20 absolute bottom-4 right-4 opacity-70" 
//           />
//         </div>
//       </div>
//     </motion.div>
//   );
// }

// export default Home;








// import { useContext, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { motion } from 'framer-motion';
// import { AssistantContext, AuthContext } from '../App';
// import Sidebar from '../components/Sidebar';
// import BottomControls from '../components/BottomControls';
// import bigGif from '../assets/big-gif.gif';
// import profileImg from '../assets/profile.png';

// function Home() {
//   const { status, setIsProcessing, setStatus } = useContext(AssistantContext);
//   const { isAuthenticated } = useContext(AuthContext);
//   const navigate = useNavigate();

//   // 🔹 Reset assistant state on mount
//   useEffect(() => {
//     setIsProcessing(false);
//     setStatus('Available');
//   }, [setIsProcessing, setStatus]);

//   useEffect(() => {
//     if (!isAuthenticated) {
//       navigate('/');
//     }
//   }, [isAuthenticated, navigate]);

//   if (!isAuthenticated) {
//     return null;
//   }

//   return (
//     <motion.div 
//       className="flex min-h-screen bg-gray-900 text-white" 
//       initial={{ opacity: 0 }} 
//       animate={{ opacity: 1 }} 
//       transition={{ duration: 0.5, ease: 'easeInOut' }}
//     >
//       <Sidebar />
//       <div className="flex-1 p-4 md:p-8 flex flex-col items-center justify-center relative">
//         <motion.div 
//           className="absolute top-4 right-4"
//           initial={{ y: -20, opacity: 0 }}
//           animate={{ y: 0, opacity: 1 }}
//           transition={{ delay: 0.2, duration: 0.5 }}
//         >
//           <Link to="/settings">
//             <img src={profileImg} alt="Profile" className="w-10 h-10 rounded-full border-2 border-blue-500 hover:scale-105 transition-transform" />
//           </Link>
//         </motion.div>
//         <motion.img 
//           src={bigGif} 
//           alt="Assistant" 
//           className="w-[70vw] max-w-[600px] h-auto mb-4" 
//           initial={{ scale: 0.8, opacity: 0 }}
//           animate={{ scale: 1, opacity: 1 }}
//           transition={{ delay: 0.4, duration: 0.5, ease: 'easeOut' }}
//         />
//         {/* 🔹 Status Display */}
//         <motion.p 
//           className="text-lg font-semibold text-gray-300 mb-4"
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//           transition={{ delay: 0.8, duration: 0.5 }}
//         >
//         </motion.p>
//         <div className="w-full flex justify-center">
//           <BottomControls />
//         </div>
//         <img src={bigGif} alt="Small GIF" className="w-20 h-20 absolute bottom-4 right-4 opacity-70" />
//       </div>
//     </motion.div>
//   );
// }

// export default Home;
