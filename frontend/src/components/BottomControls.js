import { useState, useContext } from 'react';
import { AssistantContext } from '../App';
import MicrophoneToggle from './MicrophoneToggle';
import MuteToggle from './MuteToggle';
import StatusDisplay from './StatusDisplay';
import cancelImg from '../assets/cancel.png';

function BottomControls() {
  const { setStatus, isProcessing, setIsProcessing } = useContext(AssistantContext);
  const [isMuted, setIsMuted] = useState(false);

  const handleCancel = () => {
    setIsProcessing(false);
    setStatus('Available');
    if (window.currentAudio) {
      window.currentAudio.pause();
      window.currentAudio = null;
    }
  };

  return (
    <div className="absolute bottom-4 left-0 right-0 flex justify-center z-30">
      {/* Everything centered relative to right section */}
      <div className="flex flex-col items-center space-y-2 md:space-y-3">
        {/* Status centered above buttons */}
        <div className="scale-90 md:scale-100 origin-bottom">
          <StatusDisplay />
        </div>

        {/* Buttons centered below */}
        <div className="flex justify-center space-x-3 md:space-x-4 bg-gray-800 bg-opacity-80 p-1 md:p-2 rounded-full">
          <MicrophoneToggle />
          <MuteToggle isMuted={isMuted} setIsMuted={setIsMuted} />
          {isProcessing && (
            <button
              onClick={handleCancel}
              className="p-1 md:p-2 rounded-full bg-red-600 hover:bg-red-700 transition-colors"
            >
              <img src={cancelImg} alt="Cancel" className="w-5 h-5 md:w-6 md:h-6" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default BottomControls;















// import { useState, useContext } from 'react';
// import { AssistantContext } from '../App';
// import MicrophoneToggle from './MicrophoneToggle';
// import MuteToggle from './MuteToggle';
// import StatusDisplay from './StatusDisplay';
// import cancelImg from '../assets/cancel.png';

// function BottomControls() {
//   const { setStatus, isProcessing, setIsProcessing } = useContext(AssistantContext);
//   const [isMuted, setIsMuted] = useState(false);

//   const handleCancel = () => {
//     setIsProcessing(false);
//     setStatus('Available');
//     if (window.currentAudio) {
//       window.currentAudio.pause();
//       window.currentAudio = null;
//     }
//   };

//   return (
//     <div className="absolute bottom-4 left-0 right-0 flex justify-center z-50">
//       {/* Wrapper: status above buttons */}
//       <div className="flex flex-col items-center space-y-3">
//         {/* Status centered */}
//         <StatusDisplay />

//         {/* Buttons centered below */}
//         <div className="flex justify-center space-x-4 bg-gray-800 bg-opacity-80 p-2 rounded-full">
//           <MicrophoneToggle />
//           <MuteToggle isMuted={isMuted} setIsMuted={setIsMuted} />
//           {isProcessing && (
//             <button
//               onClick={handleCancel}
//               className="p-2 rounded-full bg-red-600 hover:bg-red-700 transition-colors"
//             >
//               <img src={cancelImg} alt="Cancel" className="w-6 h-6" />
//             </button>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default BottomControls;
