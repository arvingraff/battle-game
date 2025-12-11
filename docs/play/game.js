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
const STATE_SHOP = 3;
const STATE_SECRET_HUNT = 4;
const STATE_MATH_CHALLENGE = 5;

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
let dillyDollyMode = false;
let combineMode = false;

// Shop & Secrets
let sessionPurchases = {
    shopUnlocked: false,
    relaxMode: false,
    makkaPakkaMode: false,
    escapeMomMode: false,
    captureFlagMode: false,
    survivalMode: false,
    adventure3dMode: false,
    dillyDollyMode: false
};

let unlockProgress = {
    foundSecretGame: false,
    clickedShopWord: false,
    enteredLllooolll: false,
    answeredMath: false
};

let shopCodeInput = "";
let mathAnswerInput = "";
let secretHuntItems = [];
let secretHuntShopRect = null;
let secretHuntWrongRects = [];

// Combine Mode Variables
let dogX = 100;
let dogY = 0;
let dogVelocityY = 0;
let dogDirection = 1;
let transformation = 0;
let itemsCollected = 0;
let combineItems = [];
let combineObstacles = [];
let combineParticles = [];
let combineGameTime = 0;
let combineSpawnTimer = 0;
let combineObstacleTimer = 0;
let combineStoryPhase = 0;
let combineShowCelebration = false;
let combineCelebrationTimer = 0;
let combineLives = 5;
let combineHealth = 100;
let combineStamina = 100;
let isJumping = false;
let isSprinting = false;

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
    
    // Set canvas size
    canvas.width = CANVAS_WIDTH;
    canvas.height = CANVAS_HEIGHT;
    
    // Add event listeners
    window.addEventListener('keydown', (e) => {
        if (keys.hasOwnProperty(e.key)) keys[e.key] = true;
        handleInput(e);
    });
    
    window.addEventListener('keyup', (e) => {
        if (keys.hasOwnProperty(e.key)) keys[e.key] = false;
    });

    canvas.addEventListener('mousedown', handleMouseClick);
    
    // Initialize Audio
    initAudio();
    
    // Start Game Loop
    requestAnimationFrame(gameLoop);
};

function gameLoop(timestamp) {
    // Calculate delta time
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    
    // Update
    update(deltaTime);
    
    // Draw
    draw();
    
    // Loop
    requestAnimationFrame(gameLoop);
}

function update(deltaTime) {
    if (gameState === STATE_PLAYING) {
        if (combineMode) {
            updateCombineMode(deltaTime);
        } else {
            // Existing update logic for other modes
            // ... (This part would need to be refactored to support multiple modes cleanly)
            // For now, we assume the existing update logic handles battle/survival/mom/dillydolly
            // We need to ensure update() calls the right logic based on gameMode
            
            // Basic player movement (shared)
            if (keys.w && players[0].y > 0) players[0].y -= PLAYER_SPEED;
            if (keys.s && players[0].y < CANVAS_HEIGHT - players[0].height) players[0].y += PLAYER_SPEED;
            if (keys.a && players[0].x > 0) players[0].x -= PLAYER_SPEED;
            if (keys.d && players[0].x < CANVAS_WIDTH - players[0].width) players[0].x += PLAYER_SPEED;
            
            // ... (Rest of the update logic from original file)
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    if (gameState === STATE_MENU) {
        drawMenu();
    } else if (gameState === STATE_SHOP) {
        drawShop();
    } else if (gameState === STATE_SECRET_HUNT) {
        drawSecretHunt();
    } else if (gameState === STATE_MATH_CHALLENGE) {
        drawMathChallenge();
    } else if (gameState === STATE_PLAYING) {
        if (combineMode) {
            drawCombineMode();
        } else {
            // Existing draw logic
            // ...
            // We need to ensure draw() calls the right logic based on gameMode
            
            // For now, just call the main draw function if not combine mode
            // This assumes the original draw function is available or we need to inline it
            // Since we are appending, we might need to restructure the original draw function
            
            // Let's assume we have a drawBattleMode function or similar
            // For this snippet, I'll just put a placeholder
            
            // Draw Background
            ctx.fillStyle = '#2c3e50';
            ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
            
            // Draw Players
            for (let p of players) {
                drawPlayer(p);
            }
            
            // ... (Rest of drawing)
        }
    } else if (gameState === STATE_GAMEOVER) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        ctx.fillStyle = '#e74c3c';
        ctx.font = 'bold 60px Arial';
        ctx.textAlign = 'center';
        ctx.fillText("GAME OVER", CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - 50);
        
        ctx.fillStyle = '#fff';
        ctx.font = '30px Arial';
        ctx.fillText(gameOverMessage || "You Died!", CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 20);
        
        ctx.font = '20px Arial';
        ctx.fillText("Press R to Restart", CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 80);
    }
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
    } else if (gameMode === 'dilly') {
        updateDillyDolly(deltaTime);
    } else if (gameMode === 'combine') {
        updateCombineMode(deltaTime);
    }
    
    // Update Bullets (Common)
    if (gameMode !== 'combine') {
        updateBullets();
    }
    
    // Update Particles (Common)
    updateParticles();
}

function updateCombineMode(deltaTime) {
    // Convert deltaTime to seconds
    let dt = deltaTime / 1000;
    combineGameTime += dt;
    combineSpawnTimer += dt;
    combineObstacleTimer += dt;

    // Player Movement (Dog)
    let speed = 300 * dt; // Base speed
    isSprinting = keys.Shift && combineStamina > 0;
    
    if (isSprinting) {
        speed *= 1.8;
        combineStamina -= dt * 30;
        if (combineStamina < 0) combineStamina = 0;
    } else if (combineStamina < 100) {
        combineStamina += dt * 25;
    }

    if (keys.a || keys.ArrowLeft) {
        dogX -= speed;
        dogDirection = -1;
    }
    if (keys.d || keys.ArrowRight) {
        dogX += speed;
        dogDirection = 1;
    }

    // Jumping
    if ((keys.w || keys.ArrowUp || keys[" "]) && !isJumping) {
        if (combineStamina >= 20) {
            dogVelocityY = -600; // Jump force
            isJumping = true;
            combineStamina -= 20;
        }
    }

    // Gravity
    if (isJumping || dogY < CANVAS_HEIGHT - 150) {
        dogY += dogVelocityY * dt;
        dogVelocityY += 1500 * dt; // Gravity

        if (dogY >= CANVAS_HEIGHT - 150) {
            dogY = CANVAS_HEIGHT - 150;
            isJumping = false;
            dogVelocityY = 0;
        }
    }

    // Keep dog on screen
    if (dogX < 0) dogX = 0;
    if (dogX > CANVAS_WIDTH - 60) dogX = CANVAS_WIDTH - 60;

    // Spawn Items
    if (combineSpawnTimer > 0.8 && transformation < 100) {
        combineSpawnTimer = 0;
        let itemTypes = [
            {emoji: "👔", name: "Shirt", points: 3},
            {emoji: "👞", name: "Shoes", points: 3},
            {emoji: "🎩", name: "Hat", points: 3},
            {emoji: "👓", name: "Glasses", points: 3},
            {emoji: "📚", name: "Book", points: 3},
            {emoji: "☕", name: "Coffee", points: 3},
            {emoji: "🍔", name: "Burger", points: 3},
            {emoji: "💼", name: "Briefcase", points: 5},
            {emoji: "📱", name: "Phone", points: 5},
            {emoji: "💎", name: "Diamond", points: 10}
        ];
        let item = itemTypes[Math.floor(Math.random() * itemTypes.length)];
        combineItems.push({
            x: CANVAS_WIDTH + 50,
            y: CANVAS_HEIGHT - 200 + Math.random() * 100,
            emoji: item.emoji,
            name: item.name,
            points: item.points,
            collected: false,
            floatOffset: Math.random() * Math.PI * 2
        });
    }

    // Spawn Obstacles
    if (combineObstacleTimer > 2.0 && transformation < 100 && combineStoryPhase >= 1) {
        combineObstacleTimer = 0;
        let obsTypes = [
            {type: "car", damage: 10, width: 70, height: 40, color: '#c0392b'},
            {type: "trash", damage: 5, width: 35, height: 50, color: '#7f8c8d'},
            {type: "puddle", damage: 5, width: 60, height: 20, color: '#3498db'}
        ];
        let obs = obsTypes[Math.floor(Math.random() * obsTypes.length)];
        combineObstacles.push({
            x: CANVAS_WIDTH + 50,
            y: CANVAS_HEIGHT - 120 - (obs.type === 'puddle' ? -20 : 0),
            ...obs,
            speed: 200 + Math.random() * 100
        });
    }

    // Update Items
    for (let i = combineItems.length - 1; i >= 0; i--) {
        let item = combineItems[i];
        item.x -= 150 * dt; // Scroll speed
        
        // Collision
        if (!item.collected && rectIntersect(dogX, dogY, 60, 80, item.x, item.y, 40, 40)) {
            item.collected = true;
            transformation = Math.min(100, transformation + item.points);
            itemsCollected++;
            playSound('select'); // Use select sound for pickup
            createParticles(item.x, item.y, 'gold');
            combineItems.splice(i, 1);
        } else if (item.x < -50) {
            combineItems.splice(i, 1);
        }
    }

    // Update Obstacles
    for (let i = combineObstacles.length - 1; i >= 0; i--) {
        let obs = combineObstacles[i];
        obs.x -= obs.speed * dt;

        if (rectIntersect(dogX, dogY, 60, 80, obs.x, obs.y, obs.width, obs.height)) {
            combineHealth -= obs.damage;
            playSound('hit');
            createParticles(dogX, dogY, 'red');
            combineObstacles.splice(i, 1);

            if (combineHealth <= 0) {
                combineLives--;
                combineHealth = 100;
                if (combineLives <= 0) {
                    gameOver("Game Over! You collected " + itemsCollected + " items.");
                }
            }
        } else if (obs.x < -100) {
            combineObstacles.splice(i, 1);
        }
    }

    // Update Story Phase
    if (transformation < 20) combineStoryPhase = 0;
    else if (transformation < 40) combineStoryPhase = 1;
    else if (transformation < 70) combineStoryPhase = 2;
    else if (transformation < 100) combineStoryPhase = 3;
    else {
        combineStoryPhase = 4;
        if (!combineShowCelebration) {
            combineShowCelebration = true;
            playSound('win');
            godMode = true; // Reward
        }
    }
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
    let enemyCount = wave * 2 + 3;
    for (let i = 0; i < enemyCount; i++) {
        enemies.push({
            x: Math.random() < 0.5 ? -50 : CANVAS_WIDTH + 50,
            y: Math.random() * CANVAS_HEIGHT,
            width: 40,
            height: 40,
            color: '#e74c3c',
            health: 20 + wave * 5,
            speed: 1 + Math.random() * 2
        });
    }
}

function updateMomMode(deltaTime) {
    // Similar to Survival but with Mom boss logic
    updateSurvival(deltaTime);
    // Add Mom specific logic here if needed
}

function updateDillyDolly(deltaTime) {
    // Just a fun mode, maybe random colors or dancing
    updateBattle(deltaTime);
}

function updateBullets() {
    for (let i = bullets.length - 1; i >= 0; i--) {
        let b = bullets[i];
        b.x += b.vx;
        b.y += b.vy;
        
        // Remove if off screen
        if (b.x < 0 || b.x > CANVAS_WIDTH) {
            bullets.splice(i, 1);
            continue;
        }
        
        // Check collisions
        if (gameMode === 'battle') {
            // Check hit on other player
            let target = (b.owner === players[0]) ? players[1] : players[0];
            if (rectIntersect(b.x, b.y, BULLET_SIZE, BULLET_SIZE, target.x, target.y, target.width, target.height)) {
                target.health -= 10;
                playSound('hit');
                createParticles(target.x + target.width/2, target.y + target.height/2, 'red');
                bullets.splice(i, 1);
                
                if (target.health <= 0) {
                    gameOver(b.owner.name + " Wins!");
                }
            }
        } else if (gameMode === 'survival' || gameMode === 'mom') {
            // Check hit on enemies
            if (b.owner === players[0]) {
                for (let j = enemies.length - 1; j >= 0; j--) {
                    let e = enemies[j];
                    if (rectIntersect(b.x, b.y, BULLET_SIZE, BULLET_SIZE, e.x, e.y, e.width, e.height)) {
                        e.health -= 20;
                        playSound('hit');
                        createParticles(e.x + e.width/2, e.y + e.height/2, 'orange');
                        bullets.splice(i, 1);
                        
                        if (e.health <= 0) {
                            enemies.splice(j, 1);
                            players[0].score += 100;
                        }
                        break; // Bullet hits one enemy
                    }
                }
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
        
        if (p.life <= 0) {
            particles.splice(i, 1);
        }
    }
}

function resetCombineMode() {
    dogX = 100;
    dogY = CANVAS_HEIGHT - 150;
    dogVelocityY = 0;
    dogDirection = 1;
    transformation = 0;
    itemsCollected = 0;
    combineItems = [];
    combineObstacles = [];
    combineParticles = [];
    combineGameTime = 0;
    combineSpawnTimer = 0;
    combineObstacleTimer = 0;
    combineStoryPhase = 0;
    combineShowCelebration = false;
    combineCelebrationTimer = 0;
    combineLives = 5;
    combineHealth = 100;
    combineStamina = 100;
    isJumping = false;
    isSprinting = false;
}