import { useContext } from 'react';
import { AssistantContext } from '../App';
import cancelImg from '../assets/cancel.png';

function CancelButton() {
  const { cancelCurrentCommand, isProcessing } = useContext(AssistantContext);

  const handleCancel = () => {
    if (isProcessing) {
      cancelCurrentCommand();
    }
  };

  return (
    <button 
      onClick={handleCancel} 
      className={`p-2 rounded-full bg-gray-900 hover:opacity-80 transition-opacity ${isProcessing ? 'animate-pulse ring-2 ring-red-500' : 'opacity-50'}`}
      disabled={!isProcessing}
    >
      <img src={cancelImg} alt="Cancel" className="w-5 h-5 md:w-6 md:h-6" />
    </button>
  );
}

export default CancelButton;