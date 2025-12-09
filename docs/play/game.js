// Game Constants
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
const PLAYER_SIZE = 50;
const PLAYER_SPEED = 5;
const BULLET_SPEED = 10;
const BULLET_SIZE = 10;

// Game State
let canvas, ctx;
let lastTime = 0;
let gameRunning = false;
let audioContext;
let sounds = {};

const keys = {
    w: false, a: false, s: false, d: false,
    ArrowUp: false, ArrowLeft: false, ArrowDown: false, ArrowRight: false,
    " ": false, Shift: false
};

const players = [
    {
        x: 100,
        y: CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2,
        width: PLAYER_SIZE,
        height: PLAYER_SIZE,
        color: '#3498db', // Blue
        health: 100,
        maxHealth: 100,
        direction: 1, // 1 for right, -1 for left
        name: "Player 1",
        score: 0,
        cooldown: 0
    },
    {
        x: CANVAS_WIDTH - 100 - PLAYER_SIZE,
        y: CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2,
        width: PLAYER_SIZE,
        height: PLAYER_SIZE,
        color: '#e74c3c', // Red
        health: 100,
        maxHealth: 100,
        direction: -1,
        name: "Player 2 (CPU)",
        score: 0,
        cooldown: 0,
        isCpu: true
    }
];

let bullets = [];
let particles = [];

// Initialization
window.onload = function() {
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    
    canvas.width = CANVAS_WIDTH;
    canvas.height = CANVAS_HEIGHT;
    
    // Initialize Audio
    initAudio();

    // Setup input listeners
    window.addEventListener('keydown', (e) => {
        if(keys.hasOwnProperty(e.key)) keys[e.key] = true;
        
        // Resume audio context on user interaction (browser policy)
        if (audioContext && audioContext.state === 'suspended') {
            audioContext.resume();
        }
    });
    
    window.addEventListener('keyup', (e) => {
        if(keys.hasOwnProperty(e.key)) keys[e.key] = false;
    });

    // Start Game Loop
    gameRunning = true;
    requestAnimationFrame(gameLoop);
};

// Main Game Loop
function gameLoop(timestamp) {
    if (!gameRunning) return;
    
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    
    update(deltaTime);
    draw();
    
    requestAnimationFrame(gameLoop);
}

// Update Game Logic
function update(deltaTime) {
    // Player 1 Movement (WASD)
    if (keys.w && players[0].y > 0) players[0].y -= PLAYER_SPEED;
    if (keys.s && players[0].y < CANVAS_HEIGHT - PLAYER_SIZE) players[0].y += PLAYER_SPEED;
    if (keys.a && players[0].x > 0) {
        players[0].x -= PLAYER_SPEED;
        players[0].direction = -1;
    }
    if (keys.d && players[0].x < CANVAS_WIDTH - PLAYER_SIZE) {
        players[0].x += PLAYER_SPEED;
        players[0].direction = 1;
    }
    
    // Player 1 Shooting
    if (keys[" "] && players[0].cooldown <= 0) {
        shoot(players[0]);
        players[0].cooldown = 20; // Frames cooldown
    }
    if (players[0].cooldown > 0) players[0].cooldown--;

    // CPU Logic (Simple AI)
    const cpu = players[1];
    const target = players[0];
    
    // Move towards player Y
    if (cpu.y < target.y - 10) cpu.y += PLAYER_SPEED * 0.6;
    else if (cpu.y > target.y + 10) cpu.y -= PLAYER_SPEED * 0.6;
    
    // Keep distance or close in
    const dist = Math.abs(cpu.x - target.x);
    if (dist > 400) {
        if (cpu.x > target.x) cpu.x -= PLAYER_SPEED * 0.5;
        else cpu.x += PLAYER_SPEED * 0.5;
    } else if (dist < 200) {
        if (cpu.x > target.x) cpu.x += PLAYER_SPEED * 0.5;
        else cpu.x -= PLAYER_SPEED * 0.5;
    }
    
    // Face player
    cpu.direction = (target.x > cpu.x) ? 1 : -1;
    
    // CPU Shoot
    if (cpu.cooldown <= 0 && Math.random() < 0.05 && Math.abs(cpu.y - target.y) < 50) {
        shoot(cpu);
        cpu.cooldown = 30;
    }
    if (cpu.cooldown > 0) cpu.cooldown--;

    // Update Bullets
    for (let i = bullets.length - 1; i >= 0; i--) {
        let b = bullets[i];
        b.x += b.vx;
        b.y += b.vy;
        
        // Remove if out of bounds
        if (b.x < 0 || b.x > CANVAS_WIDTH || b.y < 0 || b.y > CANVAS_HEIGHT) {
            bullets.splice(i, 1);
            continue;
        }
        
        // Check collisions
        for (let p of players) {
            if (p === b.owner) continue; // Don't hit self
            
            if (rectIntersect(b.x, b.y, BULLET_SIZE, BULLET_SIZE, p.x, p.y, p.width, p.height)) {
                p.health -= 10;
                playSound('hit');
                createParticles(b.x, b.y, p.color);
                bullets.splice(i, 1);
                
                if (p.health <= 0) {
                    playSound('win');
                    resetGame(b.owner.name + " Wins!");
                }
                break;
            }
        }
    }
    
    // Update Particles
    for (let i = particles.length - 1; i >= 0; i--) {
        let p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.05;
        if (p.life <= 0) particles.splice(i, 1);
    }
}

// Draw Game
function draw() {
    // Clear background
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw Grid (optional)
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for(let i=0; i<CANVAS_WIDTH; i+=50) {
        ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,CANVAS_HEIGHT); ctx.stroke();
    }
    for(let i=0; i<CANVAS_HEIGHT; i+=50) {
        ctx.beginPath(); ctx.moveTo(0,i); ctx.lineTo(CANVAS_WIDTH,i); ctx.stroke();
    }

    // Draw Players
    for (let p of players) {
        ctx.fillStyle = p.color;
        // Shadow
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 10;
        ctx.fillRect(p.x, p.y, p.width, p.height);
        ctx.shadowBlur = 0;
        
        // Eyes (to show direction)
        ctx.fillStyle = 'white';
        let eyeX = (p.direction === 1) ? p.x + 30 : p.x + 10;
        ctx.fillRect(eyeX, p.y + 10, 10, 10);
        
        // Health Bar
        ctx.fillStyle = '#c0392b';
        ctx.fillRect(p.x, p.y - 15, p.width, 5);
        ctx.fillStyle = '#2ecc71';
        ctx.fillRect(p.x, p.y - 15, p.width * (p.health / p.maxHealth), 5);
    }

    // Draw Bullets
    ctx.fillStyle = '#f1c40f';
    for (let b of bullets) {
        ctx.beginPath();
        ctx.arc(b.x + BULLET_SIZE/2, b.y + BULLET_SIZE/2, BULLET_SIZE/2, 0, Math.PI*2);
        ctx.fill();
    }
    
    // Draw Particles
    for (let p of particles) {
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI*2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
    }
}

// Helper Functions
function initAudio() {
    try {
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioContext();
        
        // Load sounds
        loadSound('shoot', 'assets/coin.mp3'); // Using coin sound for shooting for now
        loadSound('hit', 'assets/fart.mp3');   // Using fart sound for hit
        loadSound('win', 'assets/321go.mp3');  // Using 321go for win
        
    } catch(e) {
        console.log('Web Audio API is not supported in this browser');
    }
}

function loadSound(name, url) {
    fetch(url)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
        .then(audioBuffer => {
            sounds[name] = audioBuffer;
        })
        .catch(e => console.error('Error loading sound:', e));
}

function playSound(name) {
    if (sounds[name] && audioContext) {
        const source = audioContext.createBufferSource();
        source.buffer = sounds[name];
        source.connect(audioContext.destination);
        source.start(0);
    }
}

function shoot(player) {
    playSound('shoot');
    bullets.push({
        x: (player.direction === 1) ? player.x + player.width : player.x - BULLET_SIZE,
        y: player.y + player.height / 2 - BULLET_SIZE / 2,
        vx: player.direction * BULLET_SPEED,
        vy: 0,
        owner: player
    });
}

function rectIntersect(x1, y1, w1, h1, x2, y2, w2, h2) {
    return x2 < x1 + w1 && x2 + w2 > x1 && y2 < y1 + h1 && y2 + h2 > y1;
}

function createParticles(x, y, color) {
    for (let i = 0; i < 10; i++) {
        particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 5,
            vy: (Math.random() - 0.5) * 5,
            life: 1.0,
            color: color,
            size: Math.random() * 5 + 2
        });
    }
}

function resetGame(message) {
    alert(message);
    players[0].health = 100;
    players[0].x = 100;
    players[0].y = CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2;
    
    players[1].health = 100;
    players[1].x = CANVAS_WIDTH - 100 - PLAYER_SIZE;
    players[1].y = CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2;
    
    bullets = [];
    particles = [];
}
