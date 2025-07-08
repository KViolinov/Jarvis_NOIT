document.addEventListener('DOMContentLoaded', () => {
        const timeCard = document.getElementById('time-card');
        function updateClock() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            timeCard.textContent = `${hours}:${minutes}`;
        }
        updateClock();
        setInterval(updateClock, 1000);

        const lightsData = [
            { name: 'Светлини в бара', icon: 'lamp', on: true }, 
            { name: 'Плафон', icon: 'lamp', on: true },
            { name: 'Лампа на бюрото', icon: 'desk' }, 
            { name: 'Телевизор', icon: 'television' },
        ];

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

        const lightsGrid = document.getElementById('lights-grid');
        lightsData.forEach(light => {
            const card = document.createElement('div');
            card.className = 'card';
            if (light.on) {
                card.classList.add('on');
            }
            card.innerHTML = `
                <div class="light-info">
                    <i class="ph-fill ph-${light.icon}"></i>
                    <div class="light-details">
                        <div class="name">${light.name}</div>
                        <div class="status">${light.on ? 'On' : 'Off'}</div>
                    </div>
                </div>
                <label class="toggle-switch">
                    <input type="checkbox" ${light.on ? 'checked' : ''}>
                    <span class="slider"></span>
                </label>
            `;
            lightsGrid.appendChild(card);

            const toggle = card.querySelector('input[type="checkbox"]');
            const statusText = card.querySelector('.status');
            toggle.addEventListener('change', () => {
                card.classList.toggle('on', toggle.checked);
                statusText.textContent = toggle.checked ? 'On' : 'Off';
            });
        });

        const navButtons = document.querySelectorAll('.nav-button');
        navButtons.forEach(button => {
            button.addEventListener('click', () => {
                document.querySelector('.nav-button.active')?.classList.remove('active');
                button.classList.add('active');
            });
        });

        const canvas = document.getElementById('jarvis-canvas');
        const ctx = canvas.getContext('2d');
        let particles = [];

        function resizeCanvas() {
            canvas.width = canvas.clientWidth;
            canvas.height = canvas.clientHeight;
            if (canvas.width > 0 && canvas.height > 0) {
                initParticles();
            }
        }
        
        window.addEventListener('resize', resizeCanvas);
        
        const particleConfig = {
            count: 80,
            speed: 0.3,
            minSize: 2,
            maxSize: 5,
            color: 'rgba(0, 240, 255, 0.9)', 
            glowColor: 'rgba(0, 240, 255, 0.1)'
        };
        
        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * (particleConfig.maxSize - particleConfig.minSize) + particleConfig.minSize;
                this.speedX = (Math.random() - 0.5) * particleConfig.speed;
                this.speedY = (Math.random() - 0.5) * particleConfig.speed;
            }

            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.x > canvas.width || this.x < 0) this.speedX *= -1;
                if (this.y > canvas.height || this.y < 0) this.speedY *= -1;
            }

            draw() {
                ctx.beginPath();
                const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size * 1.5);
                gradient.addColorStop(0, particleConfig.color);
                gradient.addColorStop(1, 'transparent');
                ctx.fillStyle = gradient;
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function initParticles() {
            particles = [];
            for (let i = 0; i < particleConfig.count; i++) {
                particles.push(new Particle());
            }
        }

        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (const particle of particles) {
                particle.update();
                particle.draw();
            }
            requestAnimationFrame(animateParticles);
        }
        
        setTimeout(() => {
            resizeCanvas();
            animateParticles();
        }, 100);
    });