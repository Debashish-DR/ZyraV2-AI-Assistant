import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../config/api';

function ResetPassword() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const query = new URLSearchParams(location.search);
  const token = query.get('token');

  // Floating animation for background elements
  const [bubbles, setBubbles] = useState([]);
  
  useEffect(() => {
    // Create floating bubbles for background
    const newBubbles = Array.from({ length: 25 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 5 + 1,
      duration: Math.random() * 15 + 15,
      delay: Math.random() * 5
    }));
    setBubbles(newBubbles);
  }, []);

  const handleReset = async () => {
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    try {
      await api.post('/api/reset', { token, new_password: newPassword });
      setMessage('Password reset successfully. Please log in.');
      setTimeout(() => navigate('/'), 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Error resetting password');
    }
  };

  return (
    <motion.div 
      className="flex h-screen items-center justify-center bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 overflow-hidden relative"
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 0.8 }}
    >
      {/* Animated background elements */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        {bubbles.map(bubble => (
          <motion.div
            key={bubble.id}
            className="absolute rounded-full bg-gradient-to-br from-blue-600/10 to-purple-600/10"
            style={{
              width: `${bubble.size}rem`,
              height: `${bubble.size}rem`,
              left: `${bubble.x}%`,
              top: `${bubble.y}%`,
            }}
            animate={{
              y: [0, -40, 0],
              x: [0, 20, 0],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: bubble.duration,
              repeat: Infinity,
              delay: bubble.delay,
              ease: "easeInOut"
            }}
          />
        ))}
        
        {/* Grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:40px_40px]"></div>
        
        {/* Glowing orbs */}
        <motion.div 
          className="absolute -left-32 -top-32 w-96 h-96 bg-blue-600/10 rounded-full filter blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
          }}
        />
        <motion.div 
          className="absolute -right-32 -bottom-32 w-96 h-96 bg-purple-600/10 rounded-full filter blur-3xl"
          animate={{
            scale: [1.3, 1, 1.3],
            opacity: [0.4, 0.2, 0.4],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
          }}
        />
        
        {/* Particle effect */}
        <div className="absolute inset-0 opacity-30">
          {Array.from({ length: 50 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-white rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, -10, 0],
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: Math.random() * 5 + 3,
                repeat: Infinity,
                delay: Math.random() * 5,
              }}
            />
          ))}
        </div>
      </div>

      <motion.div 
        className="p-8 bg-gray-800/50 backdrop-blur-lg rounded-2xl shadow-2xl w-full max-w-md border border-gray-800/50 relative z-10"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.7, ease: "easeOut" }}
      >
        {/* Header with animated icon */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="mb-4"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-14 w-14 mx-auto text-blue-500 animate-pulse hover:rotate-12 transition-transform duration-300" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
            </svg>
          </motion.div>
          
          <motion.h2 
            className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-2"
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.6 }}
          >
            Reset Password
          </motion.h2>
          
          <motion.p 
            className="text-gray-400 text-sm"
            initial={{ y: -10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.6 }}
          >
            Create a new secure password
          </motion.p>
        </div>
        
        {error && (
          <motion.p 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-red-400 mb-6 text-center bg-red-900/30 py-2 rounded-lg border border-red-800/50 flex items-center justify-center text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error}
          </motion.p>
        )}

        {message && (
          <motion.p 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-green-400 mb-6 text-center bg-green-900/30 py-2 rounded-lg border border-green-800/50 flex items-center justify-center text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            {message}
          </motion.p>
        )}
        
        <div className="space-y-4">
          <div>
            <label className="block text-gray-300 mb-2 font-medium text-sm">New Password</label>
            <div className="relative">
              <input
                type={showNewPassword ? "text" : "password"}
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                className="border border-gray-700 p-3 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50 bg-gray-700/50 text-white placeholder-gray-400 pl-10 pr-12 transition-all duration-300"
                placeholder="Enter new password"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
              </div>
              <motion.button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowNewPassword(!showNewPassword)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                {showNewPassword ? (
                  <motion.span
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    className="text-xl"
                    title="I can see the password now 😁😉😃"
                  >
                    🐵
                  </motion.span>
                ) : (
                  <motion.span
                    initial={{ scale: 0, rotate: 180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    className="text-xl"
                    title="The password is hidden 🔒"
                  >
                    🙈
                  </motion.span>
                )}
              </motion.button>
            </div>
          </div>

          <div>
            <label className="block text-gray-300 mb-2 font-medium text-sm">Confirm Password</label>
            <div className="relative">
              <input
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                className="border border-gray-700 p-3 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50 bg-gray-700/50 text-white placeholder-gray-400 pl-10 pr-12 transition-all duration-300"
                placeholder="Confirm your password"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
              </div>
              <motion.button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                {showConfirmPassword ? (
                  <motion.span
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    className="text-xl"
                    title="I can see the password now 😁😉😃"
                  >
                    🐵
                  </motion.span>
                ) : (
                  <motion.span
                    initial={{ scale: 0, rotate: 180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    className="text-xl"
                    title="The password is hidden 🔒"
                  >
                    🙈
                  </motion.span>
                )}
              </motion.button>
            </div>
          </div>
        </div>
        
        <motion.button 
          whileHover={{ 
            scale: 1.02,
            boxShadow: "0 0 20px rgba(59, 130, 246, 0.4)"
          }}
          whileTap={{ scale: 0.98 }}
          onClick={handleReset} 
          className="w-full mt-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-lg transition-all duration-300 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 shadow-lg relative overflow-hidden group"
        >
          <span className="relative z-10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
            </svg>
            Reset Password
          </span>
          <motion.div 
            className="absolute inset-0 bg-gradient-to-r from-blue-700 to-purple-700 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
            initial={{ x: '-100%' }}
            whileHover={{ x: '0%' }}
            transition={{ duration: 0.7 }}
          />
        </motion.button>
        
        <div className="mt-6 text-center text-gray-400 text-sm">
          <p>
            Remember your password?{' '}
            <Link to="/" className="text-blue-400 hover:text-blue-300 transition-colors hover:underline font-medium">
              Sign In
            </Link>
          </p>
        </div>
        
        <div className="mt-5 pt-6 border-t border-gray-700/30">
          <p className="text-center text-gray-500 text-xs">
            Secure authentication with advanced encryption
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default ResetPassword;












// import { useState } from 'react';
// import { Link, useNavigate, useLocation } from 'react-router-dom';
// import { motion } from 'framer-motion';
// import axios from 'axios';

// function ResetPassword() {
//   const [newPassword, setNewPassword] = useState('');
//   const [confirmPassword, setConfirmPassword] = useState('');
//   const [message, setMessage] = useState('');
//   const navigate = useNavigate();
//   const location = useLocation();

//   const query = new URLSearchParams(location.search);
//   const token = query.get('token');

//   const handleReset = async () => {
//     if (newPassword !== confirmPassword) {
//       setMessage('Passwords do not match');
//       return;
//     }
//     try {
//       await axios.post('/api/reset', { token, new_password: newPassword });
//       setMessage('Password reset successfully. Please log in.');
//       setTimeout(() => navigate('/'), 2000);
//     } catch (err) {
//       setMessage(err.response?.data?.error || 'Error resetting password');
//     }
//   };

//   return (
//     <motion.div className="flex h-screen items-center justify-center bg-gray-100" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
//       <div className="p-8 bg-white rounded shadow-md w-full max-w-md">
//         <h2 className="text-2xl mb-4 text-center">Reset Password</h2>
//         {message && <p className="mb-4 text-center">{message}</p>}
//         <input
//           type="password"
//           value={newPassword}
//           onChange={e => setNewPassword(e.target.value)}
//           className="border p-2 mb-4 w-full rounded"
//           placeholder="New Password"
//         />
//         <input
//           type="password"
//           value={confirmPassword}
//           onChange={e => setConfirmPassword(e.target.value)}
//           className="border p-2 mb-4 w-full rounded"
//           placeholder="Confirm Password"
//         />
//         <button onClick={handleReset} className="bg-blue-500 text-white p-2 w-full rounded hover:bg-blue-600">Reset Password</button>
//         <p className="mt-2 text-center"><Link to="/" className="text-blue-500">Back to Login</Link></p>
//       </div>
//     </motion.div>
//   );
// }

// export default ResetPassword;