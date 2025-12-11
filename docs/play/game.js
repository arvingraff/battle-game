// Game Constants
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
const PLAYER_SIZE = 50;
const PLAYER_SPEED = 5;
const BULLET_SPEED = 10;
const BULLET_SIZE = 10;

// Game States
const STATE_MENU = 0;
const STATE_PLAYING = 1;
const STATE_GAMEOVER = 2;

// Game State
let canvas, ctx;
let lastTime = 0;
let gameRunning = false;
let gameState = STATE_MENU;
let audioContext;
let sounds = {};
let bgMusicNode = null;
let gameMode = 'battle'; // 'battle', 'survival'
let wave = 1;
let enemies = [];
let secretBuffer = "";
let godMode = false;
let finalMode = false;
let momMode = false;

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
        cooldown: 0,
        isTralala: false
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

        // Secret Code Detection
        if (e.key.length === 1) {
            secretBuffer += e.key;
            if (secretBuffer.length > 10) secretBuffer = secretBuffer.slice(-10);
            checkSecrets();
        }

        // Menu Navigation
        if (gameState === STATE_MENU) {
            if (e.key === '1') startGame('battle');
            if (e.key === '2') startGame('survival');
            if (e.key === '3') startGame('mom');
        } else if (gameState === STATE_GAMEOVER) {
            if (e.key === 'r' || e.key === 'R') {
                gameState = STATE_MENU;
                playSound('select');
            }
        }
    });
    
    window.addEventListener('keyup', (e) => {
        if(keys.hasOwnProperty(e.key)) keys[e.key] = false;
    });

    // Mouse/Touch for Menu
    canvas.addEventListener('mousedown', handleMenuClick);
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault(); // Prevent scrolling
        handleMenuClick(e.touches[0]);
    }, {passive: false});

    // Start Game Loop
    gameRunning = true;
    requestAnimationFrame(gameLoop);
};

function handleMenuClick(e) {
    if (gameState !== STATE_MENU && gameState !== STATE_GAMEOVER) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (canvas.width / rect.width);
    const y = (e.clientY - rect.top) * (canvas.height / rect.height);

    if (gameState === STATE_MENU) {
        // Battle Mode Button
        if (x > 200 && x < 600 && y > 250 && y < 320) {
            startGame('battle');
        }
        // Survival Mode Button
        else if (x > 200 && x < 600 && y > 350 && y < 420) {
            startGame('survival');
        }
        // Mom Mode Button
        else if (x > 200 && x < 600 && y > 450 && y < 520) {
            startGame('mom');
        }
    } else if (gameState === STATE_GAMEOVER) {
        // Restart Button
        if (x > 250 && x < 550 && y > 400 && y < 470) {
            gameState = STATE_MENU;
            playSound('select');
        }
    }
}

function checkSecrets() {
    // Tralala Transformation (Code: 67)
    if (secretBuffer.endsWith("67")) {
        players[0].isTralala = !players[0].isTralala;
        playSound('select');
        // Don't clear buffer to allow chaining for 6776
    }

    // Final Mode (Code: 6776) - Requires Tralala
    if (secretBuffer.endsWith("6776")) {
        if (players[0].isTralala) {
            finalMode = !finalMode;
            godMode = finalMode; // Final mode includes God Mode
            alert("FINAL MODE " + (finalMode ? "ACTIVATED" : "DEACTIVATED"));
            playSound('win');
            secretBuffer = "";
        }
    }
}

function startGame(mode) {
    gameMode = mode;
    gameState = STATE_PLAYING;
    resetGameLogic();
    playMusic();
    
    if (mode === 'mom') {
        momMode = true;
        // Mom Mode specific setup
        players[0].x = 50;
        players[0].y = CANVAS_HEIGHT / 2;
        
        // Mom Enemy
        enemies.push({
            x: CANVAS_WIDTH - 100,
            y: CANVAS_HEIGHT / 2 - 50,
            width: 100,
            height: 100,
            color: 'purple', // Mom color
            health: 9999, // Invincible
            speed: 2, // Slow but relentless
            isMom: true
        });
    } else {
        momMode = false;
    }
}

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
    if (gameState === STATE_MENU || gameState === STATE_GAMEOVER) return;

    if (gameMode === 'battle') {
        updateBattle(deltaTime);
    } else if (gameMode === 'survival') {
        updateSurvival(deltaTime);
    } else if (gameMode === 'mom') {
        updateMomMode(deltaTime);
    }
    
    // Update Bullets (Common)
    updateBullets();
    
    // Update Particles (Common)
    updateParticles();
}

function updateBattle(deltaTime) {
    // Player 1 Movement (WASD)
    let speed = finalMode ? PLAYER_SPEED * 2 : PLAYER_SPEED;
    
    if (keys.w && players[0].y > 0) players[0].y -= speed;
    if (keys.s && players[0].y < CANVAS_HEIGHT - PLAYER_SIZE) players[0].y += speed;
    if (keys.a && players[0].x > 0) {
        players[0].x -= speed;
        players[0].direction = -1;
    }
    if (keys.d && players[0].x < CANVAS_WIDTH - PLAYER_SIZE) {
        players[0].x += speed;
        players[0].direction = 1;
    }
    
    // Player 1 Shooting
    let cooldownTime = finalMode ? 5 : 20;
    if (keys[" "] && players[0].cooldown <= 0) {
        shoot(players[0]);
        players[0].cooldown = cooldownTime; 
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
}

function updateSurvival(deltaTime) {
    // Player 1 Movement (Same as Battle)
    let speed = finalMode ? PLAYER_SPEED * 2 : PLAYER_SPEED;

    if (keys.w && players[0].y > 0) players[0].y -= speed;
    if (keys.s && players[0].y < CANVAS_HEIGHT - PLAYER_SIZE) players[0].y += speed;
    if (keys.a && players[0].x > 0) {
        players[0].x -= speed;
        players[0].direction = -1;
    }
    if (keys.d && players[0].x < CANVAS_WIDTH - PLAYER_SIZE) {
        players[0].x += speed;
        players[0].direction = 1;
    }
    
    // Player 1 Shooting
    let cooldownTime = finalMode ? 5 : 20;
    if (keys[" "] && players[0].cooldown <= 0) {
        shoot(players[0]);
        players[0].cooldown = cooldownTime;
    }
    if (players[0].cooldown > 0) players[0].cooldown--;
    
    // Spawn Enemies
    if (enemies.length === 0) {
        startWave();
    }
    
    // Update Enemies
    for (let i = enemies.length - 1; i >= 0; i--) {
        let e = enemies[i];
        
        // Move towards player
        let dx = players[0].x - e.x;
        let dy = players[0].y - e.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        
        if (dist > 0) {
            e.x += (dx / dist) * e.speed;
            e.y += (dy / dist) * e.speed;
        }
        
        // Collision with player
        if (rectIntersect(e.x, e.y, e.width, e.height, players[0].x, players[0].y, players[0].width, players[0].height)) {
            if (!godMode) {
                players[0].health -= 1;
                if (players[0].health <= 0) {
                    gameOver("Game Over! You reached Wave " + wave);
                }
            }
        }
    }
}

function startWave() {
    wave++;
    let count = wave * 2 + 3;
    for (let i = 0; i < count; i++) {
        enemies.push({
            x: Math.random() < 0.5 ? -50 : CANVAS_WIDTH + 50,
            y: Math.random() * CANVAS_HEIGHT,
            width: 40,
            height: 40,
            color: '#e67e22', // Orange
            health: 20 + wave * 5,
            speed: 2 + Math.random() * 2
        });
    }
}

function updateMomMode(deltaTime) {
    // Player Movement
    let speed = finalMode ? PLAYER_SPEED * 2 : PLAYER_SPEED;
    if (keys.w && players[0].y > 0) players[0].y -= speed;
    if (keys.s && players[0].y < CANVAS_HEIGHT - PLAYER_SIZE) players[0].y += speed;
    if (keys.a && players[0].x > 0) {
        players[0].x -= speed;
        players[0].direction = -1;
    }
    if (keys.d && players[0].x < CANVAS_WIDTH - PLAYER_SIZE) {
        players[0].x += speed;
        players[0].direction = 1;
    }

    // Mom Logic (Chase Player)
    let mom = enemies[0];
    let dx = players[0].x - mom.x;
    let dy = players[0].y - mom.y;
    let dist = Math.sqrt(dx*dx + dy*dy);
    
    if (dist > 0) {
        mom.x += (dx / dist) * mom.speed;
        mom.y += (dy / dist) * mom.speed;
    }
    
    // Mom gets faster over time
    mom.speed += 0.001;

    // Collision with Mom
    if (rectIntersect(mom.x, mom.y, mom.width, mom.height, players[0].x, players[0].y, players[0].width, players[0].height)) {
        if (!godMode) {
            playSound('hit'); // Scream sound ideally
            gameOver("MOM CAUGHT YOU! RUN!");
        }
    }
    
    // Score increases over time
    players[0].score++;
}

function updateBullets() {
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
        if (gameMode === 'battle') {
            for (let p of players) {
                if (p === b.owner) continue; // Don't hit self
                
                if (rectIntersect(b.x, b.y, BULLET_SIZE, BULLET_SIZE, p.x, p.y, p.width, p.height)) {
                    if (p === players[0] && godMode) continue; // God mode protection

                    p.health -= 10;
                    playSound('hit');
                    createParticles(b.x, b.y, p.color);
                    bullets.splice(i, 1);
                    
                    if (p.health <= 0) {
                        playSound('win');
                        gameOver(b.owner.name + " Wins!");
                    }
                    break;
                }
            }
        } else if (gameMode === 'survival') {
            // Check enemy collisions
            for (let j = enemies.length - 1; j >= 0; j--) {
                let e = enemies[j];
                if (rectIntersect(b.x, b.y, BULLET_SIZE, BULLET_SIZE, e.x, e.y, e.width, e.height)) {
                    e.health -= 10;
                    playSound('hit');
                    createParticles(b.x, b.y, e.color);
                    bullets.splice(i, 1);
                    
                    if (e.health <= 0) {
                        enemies.splice(j, 1);
                        players[0].score += 10;
                    }
                    break;
                }
            }
        } else if (gameMode === 'mom') {
            // Bullets don't hurt Mom, but maybe slow her down?
            let mom = enemies[0];
            if (rectIntersect(b.x, b.y, BULLET_SIZE, BULLET_SIZE, mom.x, mom.y, mom.width, mom.height)) {
                playSound('hit');
                createParticles(b.x, b.y, mom.color);
                bullets.splice(i, 1);
                // Mom is invincible, no damage
            }
        }
    }
}

function updateParticles() {
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

    if (gameState === STATE_MENU) {
        drawMenu();
        return;
    } else if (gameState === STATE_GAMEOVER) {
        drawGameOver();
        return;
    }

    if (gameMode === 'battle') {
        // Draw Players
        for (let p of players) {
            drawPlayer(p);
        }
    } else if (gameMode === 'survival') {
        // Draw Player 1
        drawPlayer(players[0]);
        
        // Draw Enemies
        for (let e of enemies) {
            ctx.fillStyle = e.color;
            ctx.fillRect(e.x, e.y, e.width, e.height);
            
            // Enemy Health Bar
            ctx.fillStyle = 'red';
            ctx.fillRect(e.x, e.y - 10, e.width, 3);
            ctx.fillStyle = 'green';
            ctx.fillRect(e.x, e.y - 10, e.width * (e.health / (20 + wave * 5)), 3);
        }
        
        // Draw Wave Info
        ctx.fillStyle = 'white';
        ctx.font = '20px Arial';
        ctx.fillText("Wave: " + wave, 20, 30);
        ctx.fillText("Score: " + players[0].score, 20, 60);
    } else if (gameMode === 'mom') {
        // Draw Dark Background (Scary atmosphere)
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)'; // Dark overlay
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        // Draw Player (with flashlight effect?)
        drawPlayer(players[0]);
        
        // Draw Mom
        let mom = enemies[0];
        ctx.fillStyle = mom.color;
        ctx.fillRect(mom.x, mom.y, mom.width, mom.height);
        
        // Mom Eyes (Scary red eyes)
        ctx.fillStyle = 'red';
        ctx.beginPath();
        ctx.arc(mom.x + 30, mom.y + 30, 10, 0, Math.PI*2);
        ctx.arc(mom.x + 70, mom.y + 30, 10, 0, Math.PI*2);
        ctx.fill();
        
        // Score
        ctx.fillStyle = 'red';
        ctx.font = '20px Arial';
        ctx.fillText("SURVIVE TIME: " + Math.floor(players[0].score / 60), 20, 30);
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

    // Draw God Mode Indicator
    if (godMode) {
        ctx.fillStyle = 'gold';
        ctx.font = 'bold 20px Arial';
        ctx.fillText("GOD MODE", 10, CANVAS_HEIGHT - 10);
    }
    
    if (finalMode) {
        ctx.fillStyle = '#e74c3c';
        ctx.font = 'bold 20px Arial';
        ctx.fillText("FINAL MODE", 10, CANVAS_HEIGHT - 35);
    }
}

function drawMenu() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 60px Arial';
    ctx.textAlign = 'center';
    ctx.shadowColor = '#3498db';
    ctx.shadowBlur = 20;
    ctx.fillText("BATTLEGAME", CANVAS_WIDTH/2, 150);
    ctx.shadowBlur = 0;

    // Battle Mode Button
    ctx.fillStyle = '#3498db';
    ctx.fillRect(200, 250, 400, 70);
    ctx.fillStyle = '#fff';
    ctx.font = '30px Arial';
    ctx.fillText("1. BATTLE MODE", CANVAS_WIDTH/2, 295);

    // Survival Mode Button
    ctx.fillStyle = '#e74c3c';
    ctx.fillRect(200, 350, 400, 70);
    ctx.fillStyle = '#fff';
    ctx.fillText("2. SURVIVAL MODE", CANVAS_WIDTH/2, 395);

    // Mom Mode Button
    ctx.fillStyle = '#8e44ad'; // Purple
    ctx.fillRect(200, 450, 400, 70);
    ctx.fillStyle = '#fff';
    ctx.fillText("3. MOM MODE (SCARY)", CANVAS_WIDTH/2, 495);

    ctx.font = '20px Arial';
    ctx.fillStyle = '#bdc3c7';
    ctx.fillText("Press 1, 2 or 3 to Start", CANVAS_WIDTH/2, 580);
    ctx.fillText("Secret Code: ????", CANVAS_WIDTH/2, 620); // Adjusted Y
}

let gameOverMessage = "";

function drawGameOver() {
    // Draw the game state behind the overlay
    if (gameMode === 'battle') {
        for (let p of players) drawPlayer(p);
    } else if (gameMode === 'survival') {
        drawPlayer(players[0]);
        for (let e of enemies) {
            ctx.fillStyle = e.color;
            ctx.fillRect(e.x, e.y, e.width, e.height);
        }
    } else if (gameMode === 'mom') {
        // Draw Mom Mode background
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        // Draw Mom Jumpscare Face?
        ctx.fillStyle = 'red';
        ctx.font = '100px Arial';
        ctx.textAlign = 'center';
        ctx.fillText("👹", CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - 100);
    }

    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 50px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(gameOverMessage, CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - 50);

    // Restart Button
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(250, 400, 300, 70);
    ctx.fillStyle = '#fff';
    ctx.font = '30px Arial';
    ctx.fillText("PLAY AGAIN (R)", CANVAS_WIDTH/2, 445);
}

function drawPlayer(p) {
    // Final Mode Aura
    if (p === players[0] && finalMode) {
        ctx.shadowColor = 'gold';
        ctx.shadowBlur = 20;
    } else {
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 10;
    }

    if (p.isTralala) {
        // Draw Tralala Character
        // Skin
        ctx.fillStyle = '#d2b48c'; // Tan
        ctx.fillRect(p.x, p.y, p.width, p.height);
        
        // Hair
        ctx.fillStyle = '#2c3e50';
        ctx.fillRect(p.x, p.y, p.width, 15);
        
        // Face
        ctx.fillStyle = 'black';
        // Eyes
        let eyeOffset = (p.direction === 1) ? 10 : -10;
        ctx.beginPath();
        ctx.arc(p.x + p.width/2 + eyeOffset + 8, p.y + 25, 4, 0, Math.PI*2);
        ctx.arc(p.x + p.width/2 + eyeOffset - 8, p.y + 25, 4, 0, Math.PI*2);
        ctx.fill();
        
        // Smile
        ctx.beginPath();
        ctx.arc(p.x + p.width/2 + eyeOffset, p.y + 30, 8, 0, Math.PI, false);
        ctx.stroke();
        
    } else {
        // Standard Character
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.width, p.height);
        
        // Eyes (to show direction)
        ctx.fillStyle = 'white';
        let eyeX = (p.direction === 1) ? p.x + 30 : p.x + 10;
        ctx.fillRect(eyeX, p.y + 10, 10, 10);
    }
    
    ctx.shadowBlur = 0; // Reset shadow
    
    // Health Bar
    ctx.fillStyle = '#c0392b';
    ctx.fillRect(p.x, p.y - 15, p.width, 5);
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(p.x, p.y - 15, p.width * (p.health / p.maxHealth), 5);
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
        loadSound('music', 'assets/playmusic.mp3'); // Background music
        loadSound('select', 'assets/coin.mp3'); // Menu select sound
        
    } catch(e) {
        console.log('Web Audio API is not supported in this browser');
    }
}

function playMusic() {
    if (bgMusicNode) return; // Already playing
    
    if (sounds['music'] && audioContext) {
        bgMusicNode = audioContext.createBufferSource();
        bgMusicNode.buffer = sounds['music'];
        bgMusicNode.loop = true;
        
        // Create gain node for volume control
        const gainNode = audioContext.createGain();
        gainNode.gain.value = 0.3; // 30% volume
        
        bgMusicNode.connect(gainNode);
        gainNode.connect(audioContext.destination);
        bgMusicNode.start(0);
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
    // Deprecated, use gameOver instead
    gameOver(message);
}

function gameOver(message) {
    gameOverMessage = message;
    gameState = STATE_GAMEOVER;
}

function resetGameLogic() {
    players[0].health = 100;
    players[0].x = 100;
    players[0].y = CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2;
    
    players[1].health = 100;
    players[1].x = CANVAS_WIDTH - 100 - PLAYER_SIZE;
    players[1].y = CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2;
    
    bullets = [];
    particles = [];
    enemies = [];
    wave = 1;
    players[0].score = 0;
}
