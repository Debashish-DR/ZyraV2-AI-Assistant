import { motion } from 'framer-motion';

function AIChipAnimation() {
  return (
    <div className="hidden md:block relative bottom-2 z-20 pointer-events-none">
      <div className="relative w-40 h-40">
        {/* AI Chip Visualization */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          {/* Chip Base */}
          <motion.rect
            x="35"
            y="35"
            width="30"
            height="30"
            rx="3"
            fill="rgba(10, 20, 40, 0.9)"
            stroke="rgba(0, 150, 255, 0.8)"
            strokeWidth="1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          />
          
          {/* Chip Details */}
          <motion.rect
            x="38"
            y="38"
            width="24"
            height="24"
            rx="2"
            fill="rgba(5, 15, 30, 0.9)"
            stroke="rgba(0, 200, 255, 0.6)"
            strokeWidth="0.5"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.2 }}
          />
          
          {/* Central AI Text */}
<motion.text
  x="50"
  y="56"
  textAnchor="middle"
  className="text-lg font-bold"
  fill="rgba(0, 255, 255, 0.9)"
  initial={{ opacity: 0, scale: 0 }}
  animate={{ 
    opacity: 1, 
    scale: 1,
    filter: [
      "drop-shadow(0 0 2px rgba(0, 255, 255, 0.5))",
      "drop-shadow(0 0 8px rgba(0, 255, 255, 0.8))",
      "drop-shadow(0 0 2px rgba(0, 255, 255, 0.5))"
    ]
  }}
  transition={{ 
    duration: 1, 
    delay: 0.4,
    filter: {
      duration: 2,
      repeat: Infinity
    }
  }}
>
  AI
</motion.text>
          
          {/* Neural connections - Top side */}
          {[...Array(3)].map((_, i) => {
            const x = 38 + (i * 12);
            return (
              <motion.path
                key={`top-${i}`}
                d={`M${x},35 L${x},10`}
                stroke="rgba(0, 200, 255, 0.6)"
                strokeWidth="0.8"
                fill="none"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatType: "reverse",
                  delay: i * 0.3,
                  ease: "easeInOut"
                }}
              />
            );
          })}
          
          {/* Neural connections - Right side */}
          {[...Array(3)].map((_, i) => {
            const y = 38 + (i * 12);
            return (
              <motion.path
                key={`right-${i}`}
                d={`M65,${y} L90,${y}`}
                stroke="rgba(0, 200, 255, 0.6)"
                strokeWidth="0.8"
                fill="none"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatType: "reverse",
                  delay: 0.5 + i * 0.3,
                  ease: "easeInOut"
                }}
              />
            );
          })}
          
          {/* Neural connections - Bottom side */}
          {[...Array(3)].map((_, i) => {
            const x = 38 + (i * 12);
            return (
              <motion.path
                key={`bottom-${i}`}
                d={`M${x},65 L${x},90`}
                stroke="rgba(0, 200, 255, 0.6)"
                strokeWidth="0.8"
                fill="none"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatType: "reverse",
                  delay: 1.0 + i * 0.3,
                  ease: "easeInOut"
                }}
              />
            );
          })}
          
          {/* Neural connections - Left side */}
          {[...Array(3)].map((_, i) => {
            const y = 38 + (i * 12);
            return (
              <motion.path
                key={`left-${i}`}
                d={`M35,${y} L10,${y}`}
                stroke="rgba(0, 200, 255, 0.6)"
                strokeWidth="0.8"
                fill="none"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatType: "reverse",
                  delay: 1.5 + i * 0.3,
                  ease: "easeInOut"
                }}
              />
            );
          })}
          
          {/* Neural nodes at connection ends */}
          {[...Array(12)].map((_, i) => {
            let cx, cy;
            if (i < 3) {
              // Top nodes
              cx = 38 + (i * 12);
              cy = 7;
            } else if (i < 6) {
              // Right nodes
              cx = 93;
              cy = 38 + ((i - 3) * 12);
            } else if (i < 9) {
              // Bottom nodes
              cx = 38 + ((i - 6) * 12);
              cy = 93;
            } else {
              // Left nodes
              cx = 7;
              cy = 38 + ((i - 9) * 12);
            }
            
            return (
              <motion.circle
                key={`node-${i}`}
                cx={cx}
                cy={cy}
                r="2"
                fill="rgba(0, 255, 200, 0.9)"
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.5, 1] }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  delay: i * 0.2,
                  repeatType: "reverse"
                }}
              />
            );
          })}
          
          {/* Data pulses traveling along connections */}
          {[...Array(4)].map((_, i) => {
            let startX, startY, endX, endY, delay;
            if (i === 0) {
              // Top connection pulse
              startX = 50; startY = 35;
              endX = 50; endY = 10;
              delay = 0;
            } else if (i === 1) {
              // Right connection pulse
              startX = 65; startY = 50;
              endX = 90; endY = 50;
              delay = 1;
            } else if (i === 2) {
              // Bottom connection pulse
              startX = 50; startY = 65;
              endX = 50; endY = 90;
              delay = 2;
            } else {
              // Left connection pulse
              startX = 35; startY = 50;
              endX = 10; endY = 50;
              delay = 3;
            }
            
            return (
              <motion.circle
                key={`pulse-${i}`}
                r="1.5"
                fill="rgba(0, 255, 255, 1)"
                initial={{ cx: startX, cy: startY }}
                animate={{ 
                  cx: [startX, endX],
                  cy: [startY, endY]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: delay,
                  ease: "linear"
                }}
              />
            );
          })}
          
          {/* Chip Pins */}
          {[...Array(4)].map((_, side) => (
            [...Array(4)].map((_, i) => {
              let x, y;
              if (side === 0) {
                // Top pins
                x = 35 + (i * 10);
                y = 35;
              } else if (side === 1) {
                // Right pins
                x = 65;
                y = 35 + (i * 10);
              } else if (side === 2) {
                // Bottom pins
                x = 35 + (i * 10);
                y = 65;
              } else {
                // Left pins
                x = 35;
                y = 35 + (i * 10);
              }
              
              return (
                <motion.rect
                  key={`pin-${side}-${i}`}
                  x={x-1}
                  y={y-1}
                  width="2"
                  height="2"
                  rx="0.5"
                  fill="rgba(200, 200, 255, 0.8)"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.8 + (side * 0.2) + (i * 0.1) }}
                />
              );
            })
          ))}
        </svg>
      </div>
      
      {/* Brain Text Animation - Fixed positioning */}
      <div className="absolute w-full top-full mt-1 flex justify-center">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
        >
          <motion.span
            className="text-cyan-400 font-mono text-xs font-bold tracking-wider"
            animate={{
              textShadow: [
                "0 0 5px rgba(0, 255, 255, 0.5)",
                "0 0 15px rgba(0, 255, 255, 0.8)",
                "0 0 5px rgba(0, 255, 255, 0.5)"
              ]
            }}
            transition={{
              duration: 2,
              repeat: Infinity
            }}
          >
            NEURAL PROCESSING UNIT
          </motion.span>
        </motion.div>
      </div>
    </div>
  );
}

export default AIChipAnimation;