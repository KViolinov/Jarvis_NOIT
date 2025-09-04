document.addEventListener('DOMContentLoaded', () => {
    const loadingScreen = document.getElementById('loading-screen');

    setTimeout(() => {
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500); // Wait for fade-out transition
        }
    }, 10000); // Show loading screen for 10 seconds
    
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

    function updateGreeting() {
        const greetingTextElement = document.getElementById('greeting-text');
        const hour = new Date().getHours();

        let greeting = 'Здравейте, Константин';

        if (hour >= 5 && hour < 12) {
            greeting = 'Добро утро, Константин';
        } else if (hour >= 12 && hour < 18) {
            greeting = 'Добър ден, Константин';
        } else {
            greeting = 'Добър вечер, Константин';
        }

        greetingTextElement.textContent = greeting;
    }

    updateGreeting(); 
    setInterval(updateGreeting, 60 * 60 * 1000); 

    // 🌦️ Weather update logic with Open-Meteo
    async function updateWeather() {
        const weatherElement = document.querySelector('.weather-info div');
        const iconElement = document.querySelector('.weather-info i');

        const city = 'Велико Търново';
        const lat = 43.083652325433626;
        const lon = 25.62943277673674;

        const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            const temp = Math.round(data.current_weather.temperature * 10) / 10;
            const conditionCode = data.current_weather.weathercode;

            // Update weather text
            weatherElement.innerHTML = `${temp}°C<br>${city}`;

            // Map Open-Meteo weather codes to FontAwesome icons
            const iconMap = {
                0: 'fa-sun',
                1: 'fa-cloud-sun',
                2: 'fa-cloud',
                3: 'fa-cloud',
                45: 'fa-smog',
                48: 'fa-smog',
                51: 'fa-cloud-rain',
                53: 'fa-cloud-rain',
                55: 'fa-cloud-rain',
                61: 'fa-cloud-showers-heavy',
                63: 'fa-cloud-showers-heavy',
                65: 'fa-cloud-showers-heavy',
                71: 'fa-snowflake',
                73: 'fa-snowflake',
                75: 'fa-snowflake',
                95: 'fa-bolt',
                96: 'fa-bolt',
                99: 'fa-bolt'
            };

            const iconClass = iconMap[conditionCode] || 'fa-question';
            iconElement.className = `fas ${iconClass}`;
        } catch (error) {
            console.error('Failed to fetch weather:', error);
            weatherElement.innerHTML = `${city} - Weather Unavailable`;
        }
    }

    updateWeather();
    setInterval(updateWeather, 10 * 60 * 1000); // Update every 10 minutes

    // Dashboard buttons
    const lightButtons = document.querySelectorAll('.dashboard-item');
    lightButtons.forEach(button => {
        button.addEventListener('click', () => {
            button.classList.toggle('active');
            const buttonText = button.querySelector('span').textContent;
            console.log(`${buttonText} state was toggled.`);
        });
    });

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
        idle: [135, 115, 178],       // Purple
        listening: [255, 165, 0],    // Orange
        answering: [0, 219, 0]       // Green
    };

    let currentState = "idle";
    let currentColor = [...COLORS[currentState]];
    let targetColor = [...currentColor];
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

    for (let i = 0; i < numBalls; i++) {
        balls.push({
            x: Math.random() * w,
            y: Math.random() * h,
            radius: Math.random() * 3 + 2,
            vx: (Math.random() - 0.5) * 8,
            vy: (Math.random() - 0.5) * 8
        });
    }

    function animate() {
        ctx.clearRect(0, 0, w, h);

        // Blend toward new target color
        blendColor(currentColor, targetColor, colorSpeed);

        balls.forEach(ball => {
            ball.x += ball.vx;
            ball.y += ball.vy;

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

            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${currentColor[0]}, ${currentColor[1]}, ${currentColor[2]}, 0.8)`;
            ctx.fill();

            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.radius + 1.5, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(${currentColor[0]}, ${currentColor[1]}, ${currentColor[2]}, 0.3)`;
            ctx.lineWidth = 1;
            ctx.stroke();
        });

        requestAnimationFrame(animate);
    }

    // WebSocket connection to Jarvis Core
    const socket = new WebSocket("ws://localhost:8765");

    socket.addEventListener("open", () => {
        console.log("✅ Connected to Jarvis WebSocket");
    });

    socket.addEventListener("message", (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.state && COLORS[data.state]) {
                console.log(`🔄 Changing state to: ${data.state}`);
                currentState = data.state;
                targetColor = [...COLORS[data.state]];
            }
        } catch (e) {
            console.error("Failed to parse WebSocket message:", e);
        }
    });

    socket.addEventListener("close", () => {
        console.log("❌ WebSocket closed, retry in 3s...");
        setTimeout(() => location.reload(), 3000);
    });

    console.log('Jarvis animation started');
    animate();
});
