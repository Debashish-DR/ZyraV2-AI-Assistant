import { useEffect, useRef } from 'react';

function AnimatedBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationId;
    
    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Tech grid parameters
    const gridSize = 40;
    const nodes = [];
    const pulses = [];
    const connections = [];
    
    // Create grid nodes
    for (let x = 0; x <= canvas.width; x += gridSize) {
      for (let y = 0; y <= canvas.height; y += gridSize) {
        nodes.push({
          x,
          y,
          active: Math.random() > 0.9,
          activation: 0,
          pulseTimer: Math.random() * 100
        });
      }
    }
    
    // Create connections between nearby nodes
    nodes.forEach((node, i) => {
      nodes.forEach((otherNode, j) => {
        if (i !== j) {
          const dx = node.x - otherNode.x;
          const dy = node.y - otherNode.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < gridSize * 2.5) {
            connections.push({
              from: node,
              to: otherNode,
              active: false,
              strength: 0
            });
          }
        }
      });
    });
    
    // Create data stream particles
    const particles = [];
    for (let i = 0; i < 15; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        speed: Math.random() * 1 + 0.5, // Slower speed
        size: Math.random() * 2 + 1,
        path: [],
        targetNode: Math.floor(Math.random() * nodes.length)
      });
    }
    
    // Create hexagon patterns
    const hexagons = [];
    const hexSize = 80;
    for (let x = -hexSize; x < canvas.width + hexSize; x += hexSize * 1.5) {
      for (let y = -hexSize; y < canvas.height + hexSize; y += hexSize * Math.sqrt(3)) {
        hexagons.push({
          x,
          y: y + (x / hexSize % 2 ? hexSize * Math.sqrt(3) / 2 : 0),
          rotation: 0,
          pulse: 0
        });
      }
    }
    
    // Animation loop
    const animate = (time) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw dark gradient background
      const gradient = ctx.createRadialGradient(
        canvas.width / 2,
        canvas.height / 2,
        0,
        canvas.width / 2,
        canvas.height / 2,
        Math.max(canvas.width, canvas.height)
      );
      gradient.addColorStop(0, 'rgba(5, 10, 20, 0.95)');
      gradient.addColorStop(1, 'rgba(0, 0, 5, 0.95)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Update and draw hexagons (slower rotation)
      hexagons.forEach(hex => {
        hex.rotation += 0.0005; // Slower rotation
        hex.pulse = Math.sin(time * 0.0005 + hex.x * 0.01) * 0.5 + 0.5; // Slower pulse
        
        ctx.save();
        ctx.translate(hex.x, hex.y);
        ctx.rotate(hex.rotation);
        
        ctx.strokeStyle = `rgba(0, 150, 255, ${0.05 + hex.pulse * 0.1})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        
        for (let i = 0; i < 6; i++) {
          const angle = (Math.PI / 3) * i;
          const x = Math.cos(angle) * (hexSize * (0.7 + hex.pulse * 0.3));
          const y = Math.sin(angle) * (hexSize * (0.7 + hex.pulse * 0.3));
          
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        
        ctx.closePath();
        ctx.stroke();
        ctx.restore();
      });
      
      // Update nodes and create pulses (slower activation)
      nodes.forEach(node => {
        node.pulseTimer++;
        
        if (node.pulseTimer > 150 && Math.random() > 0.995) { // Slower activation
          node.active = true;
          node.pulseTimer = 0;
          
          // Create new pulse
          if (Math.random() > 0.7) {
            pulses.push({
              x: node.x,
              y: node.y,
              radius: 0,
              maxRadius: gridSize * (2 + Math.random() * 3),
              life: 1,
              speed: 0.3 + Math.random() * 1.0 // Slower pulses
            });
          }
        }
        
        if (node.active) {
          node.activation += 0.05; // Slower activation
          if (node.activation > 1) {
            node.activation = 0;
            node.active = false;
          }
        }
        
        // Draw nodes
        if (node.active || node.activation > 0) {
          const size = 2 + node.activation * 3;
          const alpha = 0.3 + node.activation * 0.7;
          
          ctx.fillStyle = `rgba(0, 200, 255, ${alpha})`;
          ctx.beginPath();
          ctx.arc(node.x, node.y, size, 0, Math.PI * 2);
          ctx.fill();
          
          ctx.strokeStyle = `rgba(0, 200, 255, ${alpha * 0.5})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.arc(node.x, node.y, size + 3, 0, Math.PI * 2);
          ctx.stroke();
        }
      });
      
      // Update and draw pulses
      for (let i = pulses.length - 1; i >= 0; i--) {
        const pulse = pulses[i];
        pulse.radius += pulse.speed;
        pulse.life -= 0.01; // Slower fade
        
        if (pulse.life <= 0 || pulse.radius > pulse.maxRadius) {
          pulses.splice(i, 1);
          continue;
        }
        
        const alpha = pulse.life * 0.3;
        ctx.strokeStyle = `rgba(0, 200, 255, ${alpha})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(pulse.x, pulse.y, pulse.radius, 0, Math.PI * 2);
        ctx.stroke();
      }
      
      // Update and draw connections (slower connection animation)
      connections.forEach(conn => {
        const dx = conn.from.x - conn.to.x;
        const dy = conn.from.y - conn.to.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if ((conn.from.active || conn.to.active) && distance < gridSize * 2.5) {
          conn.strength = Math.min(1, conn.strength + 0.03); // Slower connection build-up
        } else {
          conn.strength = Math.max(0, conn.strength - 0.01); // Slower connection fade
        }
        
        if (conn.strength > 0) {
          const alpha = conn.strength * 0.3;
          ctx.strokeStyle = `rgba(0, 150, 255, ${alpha})`;
          ctx.lineWidth = conn.strength;
          ctx.beginPath();
          ctx.moveTo(conn.from.x, conn.from.y);
          ctx.lineTo(conn.to.x, conn.to.y);
          ctx.stroke();
        }
      });
      
      // Update and draw data stream particles
      particles.forEach(particle => {
        const targetNode = nodes[particle.targetNode];
        const dx = targetNode.x - particle.x;
        const dy = targetNode.y - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 10) {
          particle.targetNode = Math.floor(Math.random() * nodes.length);
          particle.path = [];
        } else {
          particle.x += (dx / distance) * particle.speed;
          particle.y += (dy / distance) * particle.speed;
          particle.path.push({ x: particle.x, y: particle.y });
          
          if (particle.path.length > 15) { // Shorter trails
            particle.path.shift();
          }
        }
        
        // Draw particle path
        if (particle.path.length > 1) {
          ctx.strokeStyle = 'rgba(0, 255, 200, 0.6)';
          ctx.lineWidth = particle.size;
          ctx.beginPath();
          ctx.moveTo(particle.path[0].x, particle.path[0].y);
          
          for (let i = 1; i < particle.path.length; i++) {
            ctx.lineTo(particle.path[i].x, particle.path[i].y);
          }
          
          ctx.stroke();
        }
        
        // Draw particle
        ctx.fillStyle = 'rgba(0, 255, 200, 0.8)';
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();
      });
      
      // Create binary rain effect (slower)
      ctx.fillStyle = 'rgba(0, 255, 150, 0.1)';
      ctx.font = '12px monospace';
      
      for (let i = 0; i < 15; i++) { // Fewer digits
        const x = Math.random() * canvas.width;
        const y = (time / 30 + Math.random() * 100) % canvas.height; // Slower fall
        const digit = Math.random() > 0.5 ? '1' : '0';
        ctx.fillText(digit, x, y);
      }
      
      animationId = requestAnimationFrame(animate);
    };
    
    animate(0);
    
    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  return (
    <>
      <canvas 
        ref={canvasRef} 
        className="absolute inset-0 w-full h-full"
      />
      
      {/* Dark overlay for better contrast */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 to-black/60" />
    </>
  );
}

export default AnimatedBackground;