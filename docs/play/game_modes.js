// ============================================================================
// BATTLEGAME - PART 2: ALL REMAINING GAME MODES
// Combine Mode, Dilly Dolly, Mom Mode, Final Mode, Grass Mode, Quiz, etc.
// ============================================================================

// IMPORTANT: This file contains the remaining game modes.
// It should be appended to game_complete.js or merged into it.

// ============================================================================
// COMBINE MODE (Dog → Human transformation) - ALREADY WORKING
// ============================================================================

function initCombineMode() {
    combineMode.active = true;
    combineMode.dogX = 100;
    combineMode.dogY = CANVAS_HEIGHT - 150;
    combineMode.dogVelocityY = 0;
    combineMode.dogDirection = 1;
    combineMode.transformation = 0;
    combineMode.itemsCollected = 0;
    combineMode.items = [];
    combineMode.obstacles = [];
    combineMode.particles = [];
    combineMode.gameTime = 0;
    combineMode.spawnTimer = 0;
    combineMode.obstacleTimer = 0;
    combineMode.storyPhase = 0;
    combineMode.showCelebration = false;
    combineMode.lives = 5;
    combineMode.health = 100;
    combineMode.stamina = 100;
    combineMode.isJumping = false;
}

function updateCombineMode(dt) {
    const state = combineMode;
    state.gameTime += dt;
    state.spawnTimer += dt;
    state.obstacleTimer += dt;
    
    // Movement
    let speed = 300 * dt;
    state.isSprinting = keys.Shift && state.stamina > 0;
    
    if (state.isSprinting) {
        speed *= 1.8;
        state.stamina -= dt * 30;
        if (state.stamina < 0) state.stamina = 0;
    } else if (state.stamina < 100) {
        state.stamina += dt * 25;
    }
    
    if (keys.a || keys.ArrowLeft) {
        state.dogX -= speed;
        state.dogDirection = -1;
    }
    if (keys.d || keys.ArrowRight) {
        state.dogX += speed;
        state.dogDirection = 1;
    }
    
    // Jumping
    if ((keys.w || keys.ArrowUp || keys[" "]) && !state.isJumping && state.stamina >= 20) {
        state.dogVelocityY = -600;
        state.isJumping = true;
        state.stamina -= 20;
    }
    
    // Gravity
    const groundY = CANVAS_HEIGHT - 150;
    if (state.isJumping || state.dogY < groundY) {
        state.dogVelocityY += 1500 * dt; // Gravity
        state.dogY += state.dogVelocityY * dt;
        
        if (state.dogY >= groundY) {
            state.dogY = groundY;
            state.dogVelocityY = 0;
            state.isJumping = false;
        }
    }
    
    // Spawn items
    if (state.spawnTimer > 1.5 && state.transformation < 100) {
        state.spawnTimer = 0;
        const itemTypes = [
            {emoji: "👕", name: "Shirt", points: 5},
            {emoji: "👖", name: "Pants", points: 5},
            {emoji: "👞", name: "Shoes", points: 5},
            {emoji: "🎩", name: "Hat", points: 5},
            {emoji: "👓", name: "Glasses", points: 3},
            {emoji: "📚", name: "Book", points: 3},
            {emoji: "☕", name: "Coffee", points: 3},
            {emoji: "🍔", name: "Burger", points: 3},
            {emoji: "💼", name: "Briefcase", points: 5},
            {emoji: "📱", name: "Phone", points: 5},
            {emoji: "💎", name: "Diamond", points: 10}
        ];
        const item = itemTypes[Math.floor(Math.random() * itemTypes.length)];
        state.items.push({
            x: CANVAS_WIDTH + 50,
            y: CANVAS_HEIGHT - 200 + Math.random() * 100,
            emoji: item.emoji,
            points: item.points,
            floatOffset: Math.random() * Math.PI * 2
        });
    }
    
    // Update items
    for (let i = state.items.length - 1; i >= 0; i--) {
        const item = state.items[i];
        item.x -= 150 * dt;
        
        if (rectIntersect(state.dogX, state.dogY, 60, 80, item.x, item.y, 40, 40)) {
            state.transformation = Math.min(100, state.transformation + item.points);
            state.itemsCollected++;
            createParticles(item.x, item.y, 'gold');
            state.items.splice(i, 1);
        } else if (item.x < -50) {
            state.items.splice(i, 1);
        }
    }
    
    // Update story phase
    if (state.transformation < 20) state.storyPhase = 0;
    else if (state.transformation < 40) state.storyPhase = 1;
    else if (state.transformation < 70) state.storyPhase = 2;
    else if (state.transformation < 100) state.storyPhase = 3;
    else {
        state.storyPhase = 4;
        if (!state.showCelebration) {
            state.showCelebration = true;
            secretHack.becameHuman = true;
            secretHack.godModeUnlocked = true;
            godMode = true;
            saveGameData();
        }
    }
}

function drawCombineMode() {
    const state = combineMode;
    
    // Background
    const bgColors = ['#2c3e50', '#34495e', '#7f8c8d', '#3498db', '#87ceeb'];
    ctx.fillStyle = bgColors[state.storyPhase];
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Ground
    ctx.fillStyle = state.storyPhase < 2 ? '#5d4037' : '#7f8c8d';
    ctx.fillRect(0, CANVAS_HEIGHT - 80, CANVAS_WIDTH, 80);
    
    // Draw character
    drawCombineCharacter(state.dogX, state.dogY, state.transformation, state.dogDirection);
    
    // Draw items
    ctx.font = '40px Arial';
    state.items.forEach(item => {
        const floatY = item.y + Math.sin(state.gameTime * 5 + item.floatOffset) * 10;
        ctx.fillText(item.emoji, item.x, floatY);
    });
    
    // UI
    ctx.fillStyle = '#c0392b';
    ctx.fillRect(20, 20, 200, 20);
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(20, 20, 200 * (state.health / 100), 20);
    ctx.strokeStyle = 'white';
    ctx.strokeRect(20, 20, 200, 20);
    ctx.fillStyle = 'white';
    ctx.font = '16px Arial';
    ctx.fillText("Health", 25, 36);
    
    ctx.fillStyle = '#e67e22';
    ctx.fillRect(20, 50, 200, 15);
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(20, 50, 200 * (state.stamina / 100), 15);
    ctx.strokeRect(20, 50, 200, 15);
    ctx.fillText("Stamina", 25, 63);
    
    ctx.font = '20px Arial';
    ctx.fillText(`Lives: ${"💖".repeat(state.lives)}`, 20, 90);
    
    // Progress bar
    const barWidth = 400;
    const barX = CANVAS_WIDTH / 2 - barWidth / 2;
    ctx.fillStyle = '#333';
    ctx.fillRect(barX, 20, barWidth, 30);
    ctx.fillStyle = `hsl(${state.transformation * 1.2}, 70%, 50%)`;
    ctx.fillRect(barX, 20, barWidth * (state.transformation / 100), 30);
    ctx.strokeRect(barX, 20, barWidth, 30);
    ctx.textAlign = 'center';
    ctx.fillStyle = 'white';
    ctx.fillText(Math.floor(state.transformation) + "% Human", CANVAS_WIDTH / 2, 42);
    
    // Story text
    const stories = [
        "A lonely dog dreaming of being human...",
        "Learning to walk upright...",
        "Becoming civilized...",
        "Almost human!",
        "YOU ARE HUMAN! (God Mode Unlocked)"
    ];
    ctx.font = '24px Arial';
    ctx.fillText(stories[state.storyPhase], CANVAS_WIDTH / 2, 80);
    
    if (state.showCelebration) {
        ctx.fillStyle = 'gold';
        ctx.font = 'bold 60px Arial';
        ctx.fillText("CONGRATULATIONS!", CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
        ctx.font = '30px Arial';
        ctx.fillText("You are now fully HUMAN!", CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 50);
    }
    
    ctx.textAlign = 'left';
}

function drawCombineCharacter(x, y, progress, dir) {
    ctx.save();
    if (dir === -1) {
        ctx.translate(x + 60, 0);
        ctx.scale(-1, 1);
        x = 0;
    }
    
    if (progress < 30) {
        // Dog
        ctx.fillStyle = '#8b4513';
        ctx.beginPath();
        ctx.ellipse(x + 30, y + 50, 30, 20, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(x + 50, y + 30, 15, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillRect(x + 10, y + 60, 10, 20);
        ctx.fillRect(x + 40, y + 60, 10, 20);
    } else if (progress < 70) {
        // Hybrid
        ctx.fillStyle = '#8b4513';
        ctx.fillRect(x + 20, y + 30, 20, 40);
        ctx.beginPath();
        ctx.arc(x + 30, y + 20, 15, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillRect(x + 10, y + 30, 10, 25);
        ctx.fillRect(x + 40, y + 30, 10, 25);
        ctx.fillRect(x + 15, y + 70, 10, 20);
        ctx.fillRect(x + 35, y + 70, 10, 20);
    } else {
        // Human
        ctx.fillStyle = '#f1c27d';
        ctx.fillRect(x + 20, y + 30, 20, 40);
        ctx.beginPath();
        ctx.arc(x + 30, y + 20, 12, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#3498db';
        ctx.fillRect(x + 20, y + 30, 20, 25);
        ctx.fillStyle = '#2c3e50';
        ctx.fillRect(x + 20, y + 55, 20, 25);
        ctx.fillStyle = '#f1c27d';
        ctx.fillRect(x + 10, y + 30, 10, 25);
        ctx.fillRect(x + 40, y + 30, 10, 25);
    }
    ctx.restore();
}

// ============================================================================
// DILLY DOLLY MODE (Dancing/Party Mode)
// ============================================================================

function initDillyDollyMode() {
    dillyDollyMode.active = true;
    dillyDollyMode.bgHue = 0;
    dillyDollyMode.time = 0;
    dillyDollyMode.dolls = [];
    
    for (let i = 0; i < 20; i++) {
        dillyDollyMode.dolls.push({
            x: Math.random() * CANVAS_WIDTH,
            y: Math.random() * CANVAS_HEIGHT,
            size: 20 + Math.random() * 40,
            speed: 1 + Math.random() * 3,
            angle: Math.random() * Math.PI * 2,
            rotSpeed: (Math.random() - 0.5) * 0.1,
            emoji: ["💃", "🕺", "🎭", "🎪", "🎨", "🎵", "🎶", "✨", "🌈", "🎉"][Math.floor(Math.random() * 10)]
        });
    }
}

function updateDillyDollyMode(dt) {
    const state = dillyDollyMode;
    state.time += dt;
    state.bgHue = (state.bgHue + dt * 50) % 360;
    
    state.dolls.forEach(doll => {
        doll.x += Math.cos(doll.angle) * doll.speed;
        doll.y += Math.sin(doll.angle) * doll.speed;
        doll.angle += doll.rotSpeed;
        
        if (doll.x < 0) doll.x = CANVAS_WIDTH;
        if (doll.x > CANVAS_WIDTH) doll.x = 0;
        if (doll.y < 0) doll.y = CANVAS_HEIGHT;
        if (doll.y > CANVAS_HEIGHT) doll.y = 0;
    });
}

function drawDillyDollyMode() {
    const state = dillyDollyMode;
    
    // Rainbow background
    ctx.fillStyle = `hsl(${state.bgHue}, 70%, 50%)`;
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw dolls
    state.dolls.forEach(doll => {
        ctx.save();
        ctx.translate(doll.x, doll.y);
        ctx.rotate(state.time + doll.angle);
        ctx.font = `${doll.size}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(doll.emoji, 0, 0);
        ctx.restore();
    });
    
    // Title
    ctx.fillStyle = 'white';
    ctx.font = 'bold 60px Arial';
    ctx.textAlign = 'center';
    ctx.shadowColor = 'black';
    ctx.shadowBlur = 10;
    ctx.fillText("DILLY DOLLY PARTY!", CANVAS_WIDTH/2, 60);
    ctx.shadowBlur = 0;
    
    // Instructions
    ctx.font = '20px Arial';
    ctx.fillText("Just dance! Press R to return", CANVAS_WIDTH/2, CANVAS_HEIGHT - 30);
    ctx.textAlign = 'left';
}

// ============================================================================
// MOM MODE (Escape from Mom)
// ============================================================================

function initMomMode() {
    momMode.active = true;
    momMode.momX = CANVAS_WIDTH / 2;
    momMode.momY = CANVAS_HEIGHT / 2;
    momMode.momSpeed = 3;
    momMode.momAngry = false;
    momMode.timeLeft = 60;
    
    players = [{
        x: 100,
        y: 100,
        width: PLAYER_SIZE,
        height: PLAYER_SIZE,
        character: CHARACTERS[selectedCharacters[0]],
        health: 100,
        maxHealth: 100
    }];
}

function updateMomMode(dt) {
    const state = momMode;
    state.timeLeft -= dt;
    
    if (state.timeLeft <= 0) {
        saveHighScore("Player", Math.floor(60 - state.timeLeft), 'mom');
        gameOver("You survived Mom Mode!");
    }
    
    // Player movement
    const p = players[0];
    if (keys.w && p.y > 0) p.y -= PLAYER_SPEED;
    if (keys.s && p.y < CANVAS_HEIGHT - p.height) p.y += PLAYER_SPEED;
    if (keys.a && p.x > 0) p.x -= PLAYER_SPEED;
    if (keys.d && p.x < CANVAS_WIDTH - p.width) p.x += PLAYER_SPEED;
    
    // Mom chases player
    const dx = p.x - state.momX;
    const dy = p.y - state.momY;
    const dist = Math.sqrt(dx*dx + dy*dy);
    
    if (dist > 0) {
        state.momX += (dx / dist) * state.momSpeed;
        state.momY += (dy / dist) * state.momSpeed;
    }
    
    // Collision
    if (dist < 60) {
        if (!godMode) {
            gameOver("Mom caught you!");
        }
    }
    
    // Mom gets angrier over time
    if (state.timeLeft < 30) {
        state.momAngry = true;
        state.momSpeed = 4;
    }
}

function drawMomMode() {
    const state = momMode;
    
    // Background
    ctx.fillStyle = state.momAngry ? '#8b0000' : '#ffc0cb';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw player
    drawPlayer(players[0]);
    
    // Draw Mom
    ctx.font = '80px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const momEmoji = state.momAngry ? '😡' : '👩';
    ctx.fillText(momEmoji, state.momX, state.momY);
    
    // UI
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = 'white';
    ctx.font = '30px Arial';
    ctx.fillText(`Time Left: ${Math.ceil(state.timeLeft)}s`, 10, 40);
    ctx.fillText(`Escape from Mom!`, 10, 80);
}

// ============================================================================
// FINAL MODE (Ultimate Challenge)
// ============================================================================

function initFinalMode() {
    finalModeState.active = true;
    finalModeState.platforms = [];
    finalModeState.enemies = [];
    finalModeState.bossActive = false;
    
    // Create platforms
    for (let i = 0; i < 10; i++) {
        finalModeState.platforms.push({
            x: i * 150,
            y: CANVAS_HEIGHT - 100 - Math.random() * 200,
            width: 120,
            height: 20
        });
    }
    
    players = [{
        x: 100,
        y: 300,
        width: PLAYER_SIZE,
        height: PLAYER_SIZE,
        character: CHARACTERS[selectedCharacters[0]],
        health: 100,
        maxHealth: 100,
        velocityY: 0,
        onGround: false
    }];
}

function updateFinalMode(dt) {
    const p = players[0];
    
    // Movement
    if (keys.a && p.x > 0) p.x -= PLAYER_SPEED * 2;
    if (keys.d && p.x < CANVAS_WIDTH - p.width) p.x += PLAYER_SPEED * 2;
    
    // Jumping
    if ((keys.w || keys[" "]) && p.onGround) {
        p.velocityY = finalModeState.jumpPower;
        p.onGround = false;
    }
    
    // Gravity
    p.velocityY += finalModeState.gravity;
    p.y += p.velocityY;
    
    // Platform collision
    p.onGround = false;
    finalModeState.platforms.forEach(plat => {
        if (p.velocityY >= 0 && 
            p.x + p.width > plat.x && 
            p.x < plat.x + plat.width &&
            p.y + p.height >= plat.y && 
            p.y + p.height <= plat.y + plat.height) {
            p.y = plat.y - p.height;
            p.velocityY = 0;
            p.onGround = true;
        }
    });
    
    // Ground
    if (p.y >= CANVAS_HEIGHT - p.height) {
        p.y = CANVAS_HEIGHT - p.height;
        p.velocityY = 0;
        p.onGround = true;
    }
}

function drawFinalMode() {
    // Epic background
    const gradient = ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT);
    gradient.addColorStop(0, '#1a0033');
    gradient.addColorStop(1, '#330066');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw platforms
    ctx.fillStyle = '#9b59b6';
    finalModeState.platforms.forEach(plat => {
        ctx.fillRect(plat.x, plat.y, plat.width, plat.height);
    });
    
    // Draw player
    drawPlayer(players[0]);
    
    // Title
    ctx.fillStyle = '#e74c3c';
    ctx.font = 'bold 40px Arial';
    ctx.textAlign = 'center';
    ctx.shadowColor = 'red';
    ctx.shadowBlur = 20;
    ctx.fillText("🔥 FINAL MODE 🔥", CANVAS_WIDTH/2, 50);
    ctx.shadowBlur = 0;
    ctx.textAlign = 'left';
}

// ============================================================================
// GRASS MODE (Secret Mode - Wolf Vomited)
// ============================================================================

function initGrassMode() {
    grassMode.active = true;
    grassMode.grass = [];
    grassMode.time = 0;
    
    for (let i = 0; i < 100; i++) {
        grassMode.grass.push({
            x: Math.random() * CANVAS_WIDTH,
            y: CANVAS_HEIGHT - 100 + Math.random() * 50,
            height: 30 + Math.random() * 40,
            offset: Math.random() * Math.PI * 2
        });
    }
}

function updateGrassMode(dt) {
    grassMode.time += dt;
    grassMode.wind = Math.sin(grassMode.time) * 10;
}

function drawGrassMode() {
    // Sky
    ctx.fillStyle = '#87ceeb';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Ground
    ctx.fillStyle = '#228b22';
    ctx.fillRect(0, CANVAS_HEIGHT - 100, CANVAS_WIDTH, 100);
    
    // Grass
    grassMode.grass.forEach(g => {
        const sway = Math.sin(grassMode.time * 2 + g.offset) * grassMode.wind;
        ctx.strokeStyle = '#32cd32';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(g.x, g.y);
        ctx.lineTo(g.x + sway, g.y - g.height);
        ctx.stroke();
    });
    
    // Title
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 50px Arial';
    ctx.textAlign = 'center';
    ctx.shadowColor = '#000';
    ctx.shadowBlur = 5;
    ctx.fillText("🌿 GRASS MODE 🌿", CANVAS_WIDTH/2, 60);
    ctx.font = '20px Arial';
    ctx.fillText("So peaceful... Press R to return", CANVAS_WIDTH/2, 100);
    ctx.shadowBlur = 0;
    ctx.textAlign = 'left';
}

// Continue in next file for remaining modes...
