import { useState, useEffect, useContext } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { AuthContext } from '../App';
import toggleImg from "../assets/toggle.png";
import logoImg from "../assets/logo.png";

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(window.innerWidth >= 768);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 768);
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleResize = () => {
      const desktop = window.innerWidth >= 768;
      setIsDesktop(desktop);
      // On desktop, sidebar should be open by default
      if (desktop) {
        setIsOpen(true);
      } else {
        setIsOpen(false);
      }
    };
    
    window.addEventListener("resize", handleResize);
    handleResize();
    
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const navItems = [
    { path: "/home", label: "Home", icon: "🏠" },
    { path: "/chat", label: "Chat", icon: "💬" },
    { path: "/history", label: "History", icon: "📊" },
  ];

  // Close sidebar when clicking on a link on mobile
  const handleNavClick = () => {
    if (!isDesktop) {
      setIsOpen(false);
    }
  };

  return (
    <>
      {/* Toggle Button - Always visible */}
      <motion.button
        onClick={toggleSidebar}
        className="fixed top-8 left-4 z-50 p-2 bg-gray-900/80 backdrop-blur-sm rounded-lg border border-cyan-500/30 shadow-xl"
        whileHover={{ scale: 1.05, backgroundColor: "rgba(17, 24, 39, 0.9)" }}
        whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <img src={toggleImg} alt="Toggle" className="w-5 h-5 filter brightness-125" />
      </motion.button>

      {/* Sidebar/Menu Overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop - Only on mobile */}
            {!isDesktop && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40"
                onClick={() => setIsOpen(false)}
              />
            )}
            
            {/* Sidebar */}
            <motion.div
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="fixed top-0 left-0 h-full w-80 bg-gradient-to-b from-gray-900/95 to-gray-950/95 backdrop-blur-md z-50 p-6 border-r border-cyan-500/20 shadow-2xl overflow-y-auto"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center space-x-4">
                  <motion.div
                    whileHover={{ rotate: 5, scale: 1.05 }}
                    transition={{ type: "spring", stiffness: 400, damping: 10 }}
                  >
                    <img src={logoImg} alt="Logo" className="w-12 h-12 rounded-xl bg-cyan-900/30 p-1" />
                  </motion.div>
                  <div>
                    <h1 className="text-cyan-400 font-bold text-xl">AI Assistant</h1>
                    <p className="text-cyan-600 text-xs font-mono">Created by Debashish</p>
                  </div>
                </div>
                
                <motion.button 
                  onClick={() => setIsOpen(false)}
                  whileHover={{ scale: 1.1, backgroundColor: "rgba(6, 182, 212, 0.2)" }}
                  whileTap={{ scale: 0.9 }}
                  className="p-2 rounded-full bg-cyan-900/30 transition-colors"
                >
                  <img
                    src={toggleImg}
                    alt="Close"
                    className="w-4 h-4 filter brightness-125"
                  />
                </motion.button>
              </div>

              {/* Divider */}
              <div className="relative mb-8">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-cyan-500/20"></div>
                </div>
                <div className="relative flex justify-center">
                  <span className="px-2 text-xs text-cyan-600 font-mono bg-gray-900">NAVIGATION</span>
                </div>
              </div>

              {/* Navigation Items */}
              <nav className="space-y-3 mb-8">
                {navItems.map((item, index) => (
                  <motion.div
                    key={item.path}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Link
                      to={item.path}
                      onClick={handleNavClick}
                      className={`flex items-center p-4 rounded-xl transition-all duration-300 group ${
                        location.pathname === item.path
                          ? "bg-cyan-600/20 text-cyan-400 shadow-lg shadow-cyan-500/10 border-l-4 border-cyan-400"
                          : "text-gray-300 hover:bg-gray-800/50 hover:text-cyan-300 hover:shadow-lg hover:shadow-cyan-500/5"
                      }`}
                    >
                      <span className="text-xl mr-4 group-hover:scale-110 transition-transform">{item.icon}</span>
                      <span className="font-medium">{item.label}</span>
                      {location.pathname === item.path && (
                        <motion.div 
                          className="ml-auto w-2 h-2 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400/50"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ type: "spring", stiffness: 500 }}
                        />
                      )}
                    </Link>
                  </motion.div>
                ))}
              </nav>

              {/* Footer with Logout */}
              <div className="absolute bottom-6 left-6 right-6">
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="relative mb-6"
                >
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-cyan-500/20"></div>
                  </div>
                </motion.div>

                <motion.button
                  onClick={handleLogout}
                  whileHover={{ 
                    scale: 1.02, 
                    backgroundColor: "rgba(239, 68, 68, 0.2)",
                    boxShadow: "0 0 15px rgba(239, 68, 68, 0.3)"
                  }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center justify-center p-4 rounded-xl text-gray-300 bg-gray-800/40 hover:text-red-400 transition-all duration-300 group"
                >
                  <span className="font-medium mr-2">Logout</span>
                  <motion.span
                    animate={{ x: [0, 3, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  >
                    ⎋
                  </motion.span>
                </motion.button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Semi-transparent border indicator when sidebar is closed on desktop */}
      {isDesktop && !isOpen && (
        <motion.div 
          className="fixed top-0 left-0 h-full w-1 bg-gradient-to-b from-cyan-500/30 to-blue-500/30 z-40"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        />
      )}
    </>
  );
}
















// import { useState, useEffect, useContext } from "react";
// import { motion } from "framer-motion";
// import { Link, useNavigate } from "react-router-dom";
// import { AuthContext } from '../App';
// import toggleImg from "../assets/toggle.png";
// import logoImg from "../assets/logo.png";

// export default function Sidebar() {
//   const [isOpen, setIsOpen] = useState(false);
//   const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 768);
//   const { logout } = useContext(AuthContext);
//   const navigate = useNavigate();

//   useEffect(() => {
//     const handleResize = () => {
//       setIsDesktop(window.innerWidth >= 768);
//     };
//     window.addEventListener("resize", handleResize);
//     handleResize();
//     return () => window.removeEventListener("resize", handleResize);
//   }, []);

//   useEffect(() => {
//     if (isDesktop) {
//       setIsOpen(true);
//     } else {
//       setIsOpen(false);
//     }
//   }, [isDesktop]);

//   const handleLogout = () => {
//     logout();
//     navigate('/');
//   };

//   return (
//     <>
//       {!isOpen && (
//         <button
//           onClick={() => setIsOpen(true)}
//           className="fixed top-4 left-4 z-50"
//         >
//           <img src={toggleImg} alt="Toggle" className="w-6 h-6"/>
//         </button>
//       )}

//       <motion.div
//         className={`bg-gray-800 text-gray-200 h-screen p-4 flex flex-col ${
//           isOpen ? "w-64" : "w-16"
//         } transition-all shadow-lg`}
//         animate={{ width: isOpen ? 256 : 64 }}
//         transition={{ duration: 0.3, ease: "easeInOut" }}
//       >
//         <div className="flex items-center justify-between mb-4">
//           {isOpen && (
//             <img src={logoImg} alt="Logo" className="w-12 h-12" />
//           )}

//           <button onClick={() => setIsOpen(!isOpen)}>
//             <img
//               src={toggleImg}
//               alt="Toggle"
//               className="w-6 h-6 block"
//             />
//           </button>
//         </div>

//         {isOpen && <div className="border-b border-gray-600 mb-4"></div>}

//         {isOpen && (
//           <motion.div
//             className="flex flex-col space-y-4 flex-1"
//             initial={{ opacity: 0 }}
//             animate={{ opacity: 1 }}
//             transition={{ duration: 0.3 }}
//           >
//             <Link
//               to="/home"
//               className="hover:bg-gray-700 p-2 rounded transition-colors"
//             >
//               Home
//             </Link>
//             <Link
//               to="/chat"
//               className="hover:bg-gray-700 p-2 rounded transition-colors"
//             >
//               Chat
//             </Link>
//             <Link
//               to="/history"
//               className="hover:bg-gray-700 p-2 rounded transition-colors"
//             >
//               History
//             </Link>
//             <div className="flex-grow" />
//             <button
//               onClick={handleLogout}
//               className="hover:bg-gray-700 p-2 rounded transition-colors mt-auto text-left"
//             >
//               Logout
//             </button>
//           </motion.div>
//         )}
//       </motion.div>
//     </>
//   );
// }