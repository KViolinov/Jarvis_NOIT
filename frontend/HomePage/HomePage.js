document.addEventListener('DOMContentLoaded', () => {
    // Time update logic
    function updateTime() {
        const timeElement = document.querySelector('.current-time');
        if (timeElement) {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            timeElement.textContent = `${hours}:${minutes}`;
        }
    }
    updateTime();
    setInterval(updateTime, 60000);

    // Jarvis animation logic
    const canvas = document.getElementById('canvas');
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }
    const ctx = canvas.getContext('2d');

    let w, h;
    function resize() {
        w = canvas.width = canvas.offsetWidth;
        h = canvas.height = canvas.offsetHeight;
        if (w <= 0 || h <= 0) {
            console.warn('Canvas has invalid dimensions:', w, h);
        }
    }
    resize();
    window.addEventListener('resize', resize);

    // Color definitions
    const COLORS = {
        idle: [135, 115, 178],       // CYAN
        listening: [255, 165, 0],    // ORANGE
        answering: [0, 219, 0]       // GREEN
    };

    // State machine
    const STATES = ["idle", "listening", "answering"];
    let currentStateIndex = 0;
    let currentState = STATES[currentStateIndex];
    let currentColor = [...COLORS[currentState]];
    let targetColor = [...COLORS[currentState]];
    let lastStateChange = Date.now();

    const colorSpeed = 4;
    function blendColor(current, target, speed) {
        for (let i = 0; i < 3; i++) {
            const diff = target[i] - current[i];
            if (Math.abs(diff) > speed) {
                current[i] += speed * Math.sign(diff);
            } else {
                current[i] = target[i];
            }
        }
    }

    // Bouncing balls animation
    const numBalls = 25;
    const balls = [];

    // Initialize balls with random positions, velocities, and smaller sizes
    for (let i = 0; i < numBalls; i++) {
        balls.push({
            x: Math.random() * w,
            y: Math.random() * h,
            radius: Math.random() * 3 + 2, // Random radius between 2 and 5
            vx: (Math.random() - 0.5) * 8, // Random velocity between -4 and 4
            vy: (Math.random() - 0.5) * 8
        });
    }

    function animate() {
        // Clear canvas
        ctx.clearRect(0, 0, w, h);

        // Update state every 3 seconds
        if (Date.now() - lastStateChange > 3000) {
            currentStateIndex = (currentStateIndex + 1) % STATES.length;
            currentState = STATES[currentStateIndex];
            targetColor = [...COLORS[currentState]];
            lastStateChange = Date.now();
        }

        // Blend colors
        blendColor(currentColor, targetColor, colorSpeed);

        // Update and draw balls
        balls.forEach(ball => {
            // Update position
            ball.x += ball.vx;
            ball.y += ball.vy;

            // Bounce off walls
            if (ball.x - ball.radius < 0) {
                ball.x = ball.radius;
                ball.vx = -ball.vx;
            } else if (ball.x + ball.radius > w) {
                ball.x = w - ball.radius;
                ball.vx = -ball.vx;
            }
            if (ball.y - ball.radius < 0) {
                ball.y = ball.radius;
                ball.vy = -ball.vy;
            } else if (ball.y + ball.radius > h) {
                ball.y = h - ball.radius;
                ball.vy = -ball.vy;
            }

            // Draw ball with slight transparency
            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${currentColor[0]}, ${currentColor[1]}, ${currentColor[2]}, 0.8)`;
            ctx.fill();

            // Draw glow effect
            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.radius + 1.5, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(${currentColor[0]}, ${currentColor[1]}, ${currentColor[2]}, 0.3)`;
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        requestAnimationFrame(animate);
    }

    console.log('Jarvis animation started');
    animate();
});