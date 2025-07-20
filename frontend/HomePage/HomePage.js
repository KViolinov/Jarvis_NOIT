document.addEventListener('DOMContentLoaded', () => {
    const jarvisDotsContainer = document.getElementById('jarvisDots');
    const numDots = 50;
    const createDot = () => {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        const size = Math.random() * 8 + 2;
        dot.style.width = `${size}px`;
        dot.style.height = `${size}px`;

        const xStart = Math.random() * 100 + '%';
        const yStart = Math.random() * 100 + '%';
        const xMid1 = Math.random() * 100 + '%';
        const yMid1 = Math.random() * 100 + '%';
        const xMid2 = Math.random() * 100 + '%';
        const yMid2 = Math.random() * 100 + '%';
        const xMid3 = Math.random() * 100 + '%';
        const yMid3 = Math.random() * 100 + '%';
        const xEnd = Math.random() * 100 + '%';
        const yEnd = Math.random() * 100 + '%';

        dot.style.setProperty('--x-start', xStart);
        dot.style.setProperty('--y-start', yStart);
        dot.style.setProperty('--x-mid1', xMid1);
        dot.style.setProperty('--y-mid1', yMid1);
        dot.style.setProperty('--x-mid2', xMid2);
        dot.style.setProperty('--y-mid2', yMid2);
        dot.style.setProperty('--x-mid3', xMid3);
        dot.style.setProperty('--y-mid3', yMid3);
        dot.style.setProperty('--x-end', xEnd);
        dot.style.setProperty('--y-end', yEnd);

        dot.style.animationDuration = `${Math.random() * 5 + 3}s`;
        dot.style.animationDelay = `${Math.random() * 2}s`;

        jarvisDotsContainer.appendChild(dot);
    };

    for (let i = 0; i < numDots; i++) {
        createDot();
    }
});

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