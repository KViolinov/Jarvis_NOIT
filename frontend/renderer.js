// // Създаваме нова WebSocket връзка към Python бекенда
// const socket = new WebSocket('ws://localhost:8765');

// // Извиква се, когато връзката е успешно установена
// socket.onopen = () => {
//   console.log("✅ Успешно свързване с Python WebSocket сървъра.");
//   document.getElementById("status").innerText = "Връзката е установена. Очаквам ключова дума...";
// };

// // Извиква се при получаване на съобщение от сървъра
// socket.onmessage = (event) => {
//   console.log("📥 Получено съобщение от сървъра:", event.data);
//   try {
//     const data = JSON.parse(event.data);

//     // Проверяваме дали съобщението съдържа правилните данни
//     if (data.wake_word === "Jarvis") {
//       console.log("🟢 Ключовата дума е получена! Активиране...");
//       // Променяме текста на екрана
//       const statusElement = document.getElementById("status");
//       statusElement.innerText = "Джарвис е активиран! 🧠";
//       statusElement.style.color = "#00ff00"; // Правим текста зелен

//       // Тук може да извикаш функцията, която да изговори отговор
//       speakWithElevenLabs("Да, сър?");

//       // Връщаме статуса в изходно положение след няколко секунди
//       setTimeout(() => {
//         statusElement.innerText = "Очаквам ключова дума...";
//         statusElement.style.color = "#0f0";
//       }, 5000); // 5 секунди
//     }
//   } catch (error) {
//     console.error("Грешка при обработка на JSON съобщение:", error);
//   }
// };

// // Извиква се, ако възникне грешка с връзката
// socket.onerror = (error) => {
//   console.error("❌ WebSocket грешка:", error);
//   document.getElementById("status").innerText = "Грешка при свързване със сървъра.";
//   document.getElementById("status").style.color = "#ff0000"; // Правим текста червен
// };

// // Извиква се, когато връзката се затвори
// socket.onclose = () => {
//   console.log("🔌 Връзката със сървъра е прекъсната.");
//   document.getElementById("status").innerText = "Връзката е прекъсната.";
//   document.getElementById("status").style.color = "#ff8c00"; // Оранжево
// };


// function speakWithElevenLabs(text) {
//   console.log("📣 Изговаряне на текст:", text);
//   // Тук ще добавиш твоята логика за извикване на ElevenLabs API.
//   // Например, използвайки fetch() за заявка към техния сървър.
// }


// --- Clock and Date Update ---
        function updateTime() {
            const timeEl = document.getElementById('time');
            const dateEl = document.getElementById('date');
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            timeEl.textContent = `${hours}:${minutes}`;
            const days = ['Неделя', 'Понеделник', 'Вторник', 'Сряда', 'Четвъртък', 'Петък', 'Събота'];
            const months = ['Януари', 'Февруари', 'Март', 'Април', 'Май', 'Юни', 'Юли', 'Август', 'Септември', 'Октомври', 'Ноември', 'Декември'];
            const dayName = days[now.getDay()];
            const dayOfMonth = now.getDate();
            const monthName = months[now.getMonth()];
            dateEl.textContent = `${dayName}, ${dayOfMonth} ${monthName}`;
            updateGreeting();
        }
        updateTime();
        setInterval(updateTime, 1000);

        // --- Feather Icons ---
        feather.replace();

        // --- Interactive Control Cards ---
        document.querySelectorAll('.control-card').forEach(card => {
            card.addEventListener('click', () => {
                const statusEl = card.querySelector('.status');
                if (!statusEl) return;
                card.classList.toggle('active');
                if (card.classList.contains('active')) {
                     statusEl.textContent = 'Включено';
                } else {
                    statusEl.textContent = 'Изключено';
                }
            });
        });

        function updateGreeting() {
            const greetingEl = document.getElementById('greeting');
            const hour = new Date().getHours();

            let greeting = '';
            if (hour >= 5 && hour < 12) {
                greeting = 'Добро утро ☀️';
            } else if (hour >= 12 && hour < 18) {
                greeting = 'Добър ден 🌤️';
            } else {
                greeting = 'Добър вечер 🌙';
            }

            greetingEl.textContent = greeting;
        }




        //Weather - Api logic

        const API_KEY = "3df04d967baa9f2fca82aaa846470c69"; // Вземи от OpenWeatherMap
        const CITY = "Veliko Tarnovo";
        const UNITS = "metric"; // или 'imperial'

        async function fetchWeather() {
            try {
            const response = await fetch(
                `https://api.openweathermap.org/data/2.5/weather?q=${CITY}&units=${UNITS}&appid=${API_KEY}&lang=bg`
            );
            const data = await response.json();

            const temp = Math.round(data.main.temp);
            const humidity = data.main.humidity;
            const description = data.weather[0].description;

            document.getElementById("temp-text").textContent = `${temp}°C ${description.charAt(0).toUpperCase() + description.slice(1)}`;
            document.getElementById("humidity").textContent = `💧 ${humidity}%`;
            } catch (error) {
            console.error("Грешка при зареждане на времето:", error);
            document.getElementById("temp-text").textContent = "❌ Няма връзка";
            }
        }

        fetchWeather();
        setInterval(fetchWeather, 3600000);




        // --- TODO List Logic ---
        const todoInput = document.getElementById('todo-input');
        const addTodoBtn = document.getElementById('add-todo-btn');
        const todoList = document.getElementById('todo-list');

        // Electron IPC Renderer module
        const { ipcRenderer } = require('electron'); // <-- Добавете това за комуникация с main процеса

        // Функция за създаване на елемент на задача
        function createTaskElement(taskText, isCompleted) {
            const li = document.createElement('li');
            li.className = `flex items-center justify-between bg-white/5 p-3 rounded-lg ${isCompleted ? 'completed' : ''}`;
            li.innerHTML = `
                <div class="flex items-center">
                    <input type="checkbox" class="form-checkbox mr-3" ${isCompleted ? 'checked' : ''}>
                    <span class="task-text">${taskText}</span>
                </div>
                <button class="delete-btn text-slate-400 hover:text-white">
                    <i data-feather="trash-2" class="w-5 h-5"></i>
                </button>
            `;
            return li;
        }

        // Функция за добавяне на задача
        function addTask(taskText, isCompleted = false, saveToFile = true) {
            if (!taskText) return; // Prevent adding empty tasks
            const li = createTaskElement(taskText, isCompleted);
            todoList.appendChild(li);
            feather.replace(); // Re-initialize feather icons

            // Save tasks to file after adding (if needed)
            if (saveToFile) {
                saveTasks();
            }
        }

        // Функция за запазване на задачите във файл
        function saveTasks() {
            const tasks = [];
            document.querySelectorAll('#todo-list li').forEach(li => {
                const text = li.querySelector('.task-text').textContent;
                const isCompleted = li.querySelector('.form-checkbox').checked;
                tasks.push({ text, completed: isCompleted });
            });
            // Изпращане на задачите към главния процес за запазване
            ipcRenderer.send('save-todo-list', tasks);
        }

        // Listener за бутона "Добави нова задача"
        addTodoBtn.addEventListener('click', () => {
            const taskText = todoInput.value.trim();
            if (taskText) {
                addTask(taskText);
                todoInput.value = '';
                todoInput.focus();
            }
        });

        // Listener за Enter в инпут полето
        todoInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                const taskText = todoInput.value.trim();
                if (taskText) {
                    addTask(taskText);
                    todoInput.value = '';
                    todoInput.focus();
                }
            }
        });

        // Делегиране на събития за бутоните за изтриване и чекбоксовете
        todoList.addEventListener('click', (event) => {
            const target = event.target;
            const taskItem = target.closest('li');
            if (!taskItem) return;

            if (target.matches('.delete-btn, .delete-btn *')) {
                taskItem.remove();
                saveTasks(); // Запази след изтриване
            } else if (target.matches('.form-checkbox')) {
                taskItem.classList.toggle('completed');
                saveTasks(); // Запази след промяна на състоянието
            }
        });

        // Слушане на събитие от главния процес за заредени задачи
        ipcRenderer.on('load-todo-list', (event, tasks) => {
            todoList.innerHTML = ''; // Изчистване на съществуващите елементи
            tasks.forEach(task => {
                addTask(task.text, task.completed, false); // false, за да не запазва отново при зареждане
            });
        });

        // Изпращане на заявка към главния процес за зареждане на задачите при стартиране
        document.addEventListener('DOMContentLoaded', () => {
            ipcRenderer.send('request-todo-list');
        });







        
        // --- JARVIS Vision Interface + WebSocket Control ---
        const canvas = document.getElementById('jarvis-canvas');
        const ctx = canvas.getContext('2d');
        const jarvisStatusEl = document.getElementById('jarvis-status');

        let w, h;
        function resizeCanvas() {
            w = canvas.width = canvas.offsetWidth;
            h = canvas.height = canvas.offsetHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        // --- Цветове и състояния ---
        const COLORS = {
            idle: [0, 255, 255],       // CYAN
            listening: [255, 165, 0],  // ORANGE
            answering: [0, 219, 0]     // GREEN
        };
        const STATES = Object.keys(COLORS);
        let currentState = "idle";
        let currentColor = [...COLORS[currentState]];
        let targetColor = [...COLORS[currentState]];
        const colorSpeed = 4;

        // --- Частици за визуализация ---
        const center = { x: () => w / 2, y: () => h / 2 };
        let particles = [];
        const numParticles = 100;
        let angle = 0;
        let pulse = 3;
        let pulseDirection = 0.05;

        // Инициализация
        function initParticles() {
            particles = [];
            for (let i = 0; i < numParticles; i++) {
                particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    dx: (Math.random() - 0.5) * 4,
                    dy: (Math.random() - 0.5) * 4,
                    angleOffset: (i / numParticles) * Math.PI * 2
                });
            }
        }
        initParticles();

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

        function updateJarvisState(newState) {
            if (STATES.includes(newState)) {
                currentState = newState;
                targetColor = [...COLORS[currentState]];
            }
        }

        // --- Анимация ---
        function drawJarvis() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
            ctx.fillRect(0, 0, w, h);

            blendColor(currentColor, targetColor, colorSpeed);
            const colorStr = `rgb(${currentColor.map(Math.floor).join(',')})`;

            angle += 0.01;
            pulse += pulseDirection;
            if (pulse > 5 || pulse < 2) pulseDirection *= -1;

            for (let p of particles) {
                if (currentState !== "idle") {
                    const r = Math.min(w, h) / 3;
                    const targetX = center.x() + Math.cos(angle + p.angleOffset) * r;
                    const targetY = center.y() + Math.sin(angle + p.angleOffset) * r;
                    p.x += (targetX - p.x) * 0.05;
                    p.y += (targetY - p.y) * 0.05;
                } else {
                    p.x += p.dx;
                    p.y += p.dy;
                    if (p.x <= 0 || p.x >= w) p.dx *= -1;
                    if (p.y <= 0 || p.y >= h) p.dy *= -1;
                }

                ctx.beginPath();
                ctx.fillStyle = colorStr;
                ctx.arc(p.x, p.y, pulse, 0, Math.PI * 2);
                ctx.fill();
            }

            requestAnimationFrame(drawJarvis);
        }
        drawJarvis();

        // --- WebSocket комуникация ---
        const socket = new WebSocket('ws://localhost:8765');

        socket.onopen = () => {
            console.log("✅ Свързан с WebSocket сървъра.");
            jarvisStatusEl.textContent = "Връзката е установена. Очаквам ключова дума...";
            updateJarvisState("idle");
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.wake_word === "Jarvis") {
                    console.log("🟢 Ключова дума засечена.");
                    jarvisStatusEl.textContent = "Джарвис е активиран! 🧠";
                    jarvisStatusEl.style.color = "#39d353";
                    jarvisStatusEl.style.textShadow = "0 0 8px #39d353";
                    updateJarvisState("listening");

                    setTimeout(() => {
                        jarvisStatusEl.textContent = "Очаквам ключова дума...";
                        jarvisStatusEl.style.color = "";
                        jarvisStatusEl.style.textShadow = "";
                        updateJarvisState("idle");
                    }, 5000);

                } else if (data.status === "answering") {
                    updateJarvisState("answering");
                    jarvisStatusEl.textContent = "Джарвис отговаря...";
                    jarvisStatusEl.style.color = "#00db00";
                    jarvisStatusEl.style.textShadow = "0 0 5px #00db00";

                } else if (data.status === "idle") {
                    updateJarvisState("idle");
                    jarvisStatusEl.textContent = "Очаквам ключова дума...";
                    jarvisStatusEl.style.color = "";
                    jarvisStatusEl.style.textShadow = "";
                }
            } catch (err) {
                console.error("📛 Грешка при JSON parse:", err);
            }
        };

        socket.onerror = (error) => {
            console.error("❌ WebSocket грешка:", error);
            jarvisStatusEl.textContent = "Грешка при връзката.";
            jarvisStatusEl.style.color = "#ef4444";
            updateJarvisState("idle");
        };

        socket.onclose = () => {
            console.log("🔌 Връзката е прекъсната.");
            jarvisStatusEl.textContent = "Връзката е прекъсната.";
            jarvisStatusEl.style.color = "#f97316";
            updateJarvisState("idle");
        };

        





        // Timer part
        const timersContainer = document.getElementById("timers-container");
        const addTimerBtn = document.getElementById("add-timer-btn");
        let activeIntervals = {}; // За съхранение на интервалите

        function createTimer(durationInMinutes) {
            let totalSeconds = durationInMinutes * 60;
            let isRunning = true;
            const timerId = `timer-${Date.now()}`;

            const timerCard = document.createElement("div");
            timerCard.className = "card p-6 flex flex-col";
            timerCard.id = timerId;

            timerCard.innerHTML = `
                <div class="flex justify-between items-center">
                    <div id="${timerId}-display" class="text-4xl font-semibold">00:00</div>
                    <div class="flex items-center space-x-2">
                        <i id="${timerId}-toggle" data-feather="pause-circle" class="w-8 h-8 cursor-pointer"></i>
                        <button id="${timerId}-delete" class="text-slate-400 hover:text-white">
                            <i data-feather="trash-2" class="w-6 h-6"></i>
                        </button>
                    </div>
                </div>
            `;

            timersContainer.appendChild(timerCard);
            feather.replace();

            const displayEl = document.getElementById(`${timerId}-display`);
            const toggleEl = document.getElementById(`${timerId}-toggle`);
            const deleteBtn = document.getElementById(`${timerId}-delete`);

            function updateDisplay() {
                const minutes = Math.floor(totalSeconds / 60);
                const seconds = totalSeconds % 60;
                displayEl.innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }

            let interval = setInterval(() => {
                if (isRunning && totalSeconds > 0) {
                    totalSeconds--;
                    updateDisplay();
                } else if (totalSeconds <= 0) {
                    clearInterval(interval);
                    toggleEl.dataset.feather = "alert-circle";
                    feather.replace();
                    alert(`⏰ Таймерът за ${durationInMinutes} минути приключи!`);
                    delete activeIntervals[timerId];
                }
            }, 1000);

            activeIntervals[timerId] = interval;

            toggleEl.addEventListener("click", () => {
                isRunning = !isRunning;
                toggleEl.dataset.feather = isRunning ? "pause-circle" : "play-circle";
                feather.replace();
            });

            deleteBtn.addEventListener("click", () => {
                clearInterval(activeIntervals[timerId]);
                delete activeIntervals[timerId];
                timerCard.remove();
            });

            updateDisplay();
        }

        addTimerBtn.addEventListener("click", () => {
            const input = prompt("За колко минути да бъде таймера?");
            const minutes = parseInt(input);
            if (!isNaN(minutes) && minutes > 0) {
                createTimer(minutes);
            } else {
                alert("Моля, въведете валидно положително число.");
            }
        });



        // CPU, RAM sliders
          function getRandomPercentage(min = 5, max = 50) {
            return (Math.random() * (max - min) + min).toFixed(1);
        }

        function updateStats() {
            const cpuVal = getRandomPercentage();
            const ramVal = getRandomPercentage();
            const memVal = getRandomPercentage();

            document.getElementById('cpu-value').textContent = cpuVal + '%';
            document.getElementById('cpu-bar').style.width = cpuVal + '%';

            document.getElementById('ram-value').textContent = ramVal + '%';
            document.getElementById('ram-bar').style.width = ramVal + '%';

            document.getElementById('memory-value').textContent = memVal + '%';
            document.getElementById('memory-bar').style.width = memVal + '%';
        }

        // Обновявай на всеки 2 секунди
        setInterval(updateStats, 2000);

        // Първоначално обновяване при зареждане
        updateStats();

        