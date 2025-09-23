import { useContext } from 'react';
import { AssistantContext } from '../App';

function StatusDisplay() {
  const { status } = useContext(AssistantContext);

  const getStatusColor = () => {
    switch (status) {
      case 'Available':
        return 'bg-green-400';
      case 'Listening ...':
        return 'bg-blue-400';
      case 'Processing ...':
        return 'bg-yellow-400';
      case 'Answering ...':
        return 'bg-purple-400';
      case 'Generating':
        return 'bg-orange-400';
      case 'Muted':
        return 'bg-red-400';
      default:
        return 'bg-gray-400';
    }
  };

  return (
    <div className="flex items-center space-x-2 bg-gradient-to-b from-cyan-900/20 to-gray-950/20 bg-opacity-50 px-4 py-1 rounded-lg shadow-lg ">
      {/* Dot */}
      <span className={`w-3 h-3 rounded-full ${getStatusColor()}`}></span>

      {/* Status text */}
      <p className="text-sm font-medium font-mono text-white">
        {status}
      </p>
    </div>
  );
}

export default StatusDisplay;
