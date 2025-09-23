import { useContext } from 'react';
import { AssistantContext } from '../App';
import muteImg from '../assets/mute.png';
import unmuteImg from '../assets/unmute.png';

function MuteToggle() {
  const { isMuted, setIsMuted, stopCurrentAudio } = useContext(AssistantContext);

  const handleToggle = () => {
    if (isMuted) {
      setIsMuted(false);
    } else {
      setIsMuted(true);
      stopCurrentAudio(); // Stop any ongoing audio when muting
    }
  };

  return (
    <button 
      onClick={handleToggle} 
      className={`p-2 rounded-full bg-gray-900 hover:opacity-80 transition-opacity ${isMuted ? 'ring-2 ring-yellow-500' : ''}`}
    >
      <img src={isMuted ? muteImg : unmuteImg} alt="Mute" className="w-5 h-5 md:w-6 md:h-6" />
    </button>
  );
}

export default MuteToggle;