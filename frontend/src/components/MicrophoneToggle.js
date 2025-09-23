import { useContext, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import { AssistantContext, AuthContext } from '../App';
import micOn from '../assets/mic-on.png';
import micOff from '../assets/mic-off.png';

function MicrophoneToggle() {
  const { 
    setStatus, 
    setIsProcessing, 
    setChatlogCache, 
    isMicOn, 
    setIsMicOn, 
    isMuted
  } = useContext(AssistantContext);
  
  const { user } = useContext(AuthContext);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const audioChunksRef = useRef([]);
  const isProcessingRef = useRef(false);
  const restartTimeoutRef = useRef(null);

  const resetRecording = useCallback(() => {
    setIsMicOn(false);
    setIsProcessing(false);
    isProcessingRef.current = false;
    setStatus('Available');
    audioChunksRef.current = [];
  }, [setIsMicOn, setIsProcessing, setStatus]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
    }
    resetRecording();
  }, [resetRecording]); // FIXED: Added resetRecording dependency

  // Sync local state with global state
  useEffect(() => {
    if (!isMicOn) {
      stopRecording();
    }
  }, [isMicOn, stopRecording]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, [stopRecording]);

  const playAudioResponse = async (text) => {
    if (isMuted) return Promise.resolve();
    
    try {
      const audioRes = await axios.post('/api/text-to-speech', 
        { text, email: user.email }, 
        { responseType: 'blob', timeout: 30000 }
      );
      
      const audioUrl = URL.createObjectURL(audioRes.data);
      const audio = new Audio(audioUrl);
      
      return new Promise((resolve) => {
        audio.onended = () => {
          // Immediately return to listening mode after audio ends
          if (isMicOn && isProcessingRef.current) {
            setStatus('Listening ...');
            startRecording(); // Restart recording for next command
          }
          resolve();
        };
        audio.onerror = resolve;
        audio.play().catch(err => {
          console.error('Audio playback error:', err);
          resolve();
        });
      });
    } catch (error) {
      console.error('TTS API error:', error);
      return Promise.resolve();
    }
  };

  const startRecording = async () => {
    try {
      if (isProcessingRef.current) return;
      
      setStatus('Listening ...');
      setIsProcessing(true);
      setIsMicOn(true);
      isProcessingRef.current = true;
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          sampleSize: 16,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      streamRef.current = stream;
      const mimeType = 'audio/webm; codecs=opus';
      mediaRecorderRef.current = new MediaRecorder(stream, { 
        mimeType,
        audioBitsPerSecond: 128000
      });
      
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        if (audioChunksRef.current.length === 0 || !isProcessingRef.current) {
          resetRecording();
          return;
        }

        setStatus('Processing ...');
        const messageId = Date.now().toString();
        const blob = new Blob(audioChunksRef.current, { type: mimeType });
        const formData = new FormData();
        formData.append('audio', blob, 'recording.webm');

        try {
          const sttRes = await axios.post('/api/speech-to-text', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 15000
          });
          
          // Always show what user said
          if (sttRes.data.text) {
            const userMsg = { 
              role: 'user', 
              content: sttRes.data.text, 
              date: new Date().toISOString(), 
              id: messageId 
            };
            
            setChatlogCache(prev => [...(prev || []), userMsg]);
          }

          if (sttRes.data.error || !sttRes.data.text || sttRes.data.text.includes("Sorry")) {
            setStatus('Available');
            audioChunksRef.current = [];
            return;
          }
          
          // Get assistant response
          const chatRes = await axios.post('/api/chat', { 
            message: sttRes.data.text,
            email: user.email
          }, { timeout: 30000 });
          
          const assistantMsg = { 
            role: 'assistant', 
            content: chatRes.data.reply, 
            date: new Date().toISOString(), 
            id: `${messageId}-res` 
          };
          
          setChatlogCache(prev => [...(prev || []), assistantMsg]);
          setStatus('Answering ...');
          
          // Play the audio response
          await playAudioResponse(chatRes.data.reply);
          
        } catch (err) {
          console.error('Voice command error:', err);
          setStatus('Available');
        } finally {
          audioChunksRef.current = [];
        }
      };

      mediaRecorderRef.current.start(100);
      
      // Auto-stop after 8 seconds
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.stop();
        }
      }, 8000);
      
    } catch (err) {
      console.error('Microphone access error:', err);
      resetRecording();
    }
  };

  const handleToggle = () => {
    if (isMicOn) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <button 
      onClick={handleToggle} 
      className={`p-2 rounded-full bg-gray-900 hover:opacity-80 transition-opacity ${isMicOn ? 'animate-pulse ring-2 ring-red-500' : ''}`}
    >
      <img src={isMicOn ? micOn : micOff} alt="Mic" className="w-5 h-5 md:w-6 md:h-6" />
    </button>
  );
}

export default MicrophoneToggle;