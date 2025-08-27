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
                0: 'fa-sun',                // Clear sky
                1: 'fa-cloud-sun',          // Mainly clear
                2: 'fa-cloud',              // Partly cloudy
                3: 'fa-cloud',              // Overcast
                45: 'fa-smog',              // Fog
                48: 'fa-smog',              // Depositing rime fog
                51: 'fa-cloud-rain',        // Light drizzle
                53: 'fa-cloud-rain',        // Moderate drizzle
                55: 'fa-cloud-rain',        // Dense drizzle
                61: 'fa-cloud-showers-heavy', // Slight rain
                63: 'fa-cloud-showers-heavy', // Moderate rain
                65: 'fa-cloud-showers-heavy', // Heavy rain
                71: 'fa-snowflake',         // Slight snow fall
                73: 'fa-snowflake',         // Moderate snow fall
                75: 'fa-snowflake',         // Heavy snow fall
                95: 'fa-bolt',              // Thunderstorm
                96: 'fa-bolt',              // Thunderstorm with hail
                99: 'fa-bolt'               // Thunderstorm with heavy hail
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