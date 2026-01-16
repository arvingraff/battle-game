// ============================================================================
// BATTLEGAME - PART 4: Effects, Utilities, Input, Character Select
// ============================================================================

// ============================================================================
// SPECIAL EFFECTS & ANIMATIONS
// ============================================================================

function rainbowExplosion() {
    const duration = 3000; // 3 seconds
    const startTime = Date.now();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress >= 1) {
            return;
        }
        
        // Rainbow background
        const hue = (elapsed / 10) % 360;
        ctx.fillStyle = `hsl(${hue}, 70%, 50%)`;
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        // Fireworks
        for (let i = 0; i < 50; i++) {
            const angle = (i / 50) * Math.PI * 2;
            const dist = progress * 300;
            const x = CANVAS_WIDTH / 2 + Math.cos(angle) * dist;
            const y = CANVAS_HEIGHT / 2 + Math.sin(angle) * dist;
            const size = 10 - progress * 8;
            
            ctx.fillStyle = `hsl(${(hue + i * 7) % 360}, 100%, 50%)`;
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Text
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 60px Arial';
        ctx.textAlign = 'center';
        ctx.shadowColor = '#000';
        ctx.shadowBlur = 20;
        ctx.fillText("RAINBOW EXPLOSION!", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
        ctx.font = '30px Arial';
        ctx.fillText("gagabubu activated!", CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 50);
        ctx.shadowBlur = 0;
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

function explosionSequence() {
    const duration = 3000;
    const startTime = Date.now();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress >= 1) {
            showMessage("FINAL MODE UNLOCKED!", "#e74c3c");
            return;
        }
        
        // Flash
        const flashIntensity = Math.floor(Math.abs(Math.sin(elapsed / 50)) * 255);
        ctx.fillStyle = `rgb(${flashIntensity}, ${flashIntensity/2}, 0)`;
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        // Explosion circles
        for (let i = 0; i < 10; i++) {
            const radius = progress * 500 * (1 + i * 0.1);
            ctx.strokeStyle = `rgba(255, ${100 - i * 10}, 0, ${1 - progress})`;
            ctx.lineWidth = 10 - i;
            ctx.beginPath();
            ctx.arc(CANVAS_WIDTH/2, CANVAS_HEIGHT/2, radius, 0, Math.PI * 2);
            ctx.stroke();
        }
        
        // Particles
        for (let i = 0; i < 100; i++) {
            const angle = (i / 100) * Math.PI * 2;
            const speed = 200 + i * 2;
            const dist = progress * speed;
            const x = CANVAS_WIDTH / 2 + Math.cos(angle) * dist;
            const y = CANVAS_HEIGHT / 2 + Math.sin(angle) * dist;
            
            ctx.fillStyle = `rgba(255, ${200 - progress * 200}, 0, ${1 - progress})`;
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Text
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 80px Arial';
        ctx.textAlign = 'center';
        ctx.shadowColor = 'red';
        ctx.shadowBlur = 30;
        ctx.fillText("💥 EXPLOSION! 💥", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
        ctx.shadowBlur = 0;
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

function wolfEatAnimation() {
    const duration = 2000;
    const startTime = Date.now();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress >= 1) {
            return;
        }
        
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        // Wolf
        ctx.font = `${100 + progress * 100}px Arial`;
        ctx.textAlign = 'center';
        ctx.fillText('🐺', CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
        
        // Text
        ctx.fillStyle = '#e74c3c';
        ctx.font = 'bold 40px Arial';
        ctx.fillText("THE WOLF ATE EVERYTHING!", CANVAS_WIDTH/2, 100);
        
        ctx.fillStyle = '#fff';
        ctx.font = '20px Arial';
        ctx.fillText("All menu options are gone!", CANVAS_WIDTH/2, 150);
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

function wolfVomitAnimation(modeName) {
    const duration = 2000;
    const startTime = Date.now();
    
    function animate() {
        const elapsed = Date.now() - startTime;
        const progress = elapsed / duration;
        
        if (progress >= 1) {
            showMessage(`${modeName} unlocked!`, "#2ecc71");
            return;
        }
        
        ctx.fillStyle = '#0a5f0a';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        // Wolf
        ctx.font = '100px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('🐺', CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - 100);
        
        // Vomit particles
        for (let i = 0; i < 30; i++) {
            const angle = (i / 30) * Math.PI * 2;
            const dist = progress * 200;
            const x = CANVAS_WIDTH / 2 + Math.cos(angle) * dist;
            const y = CANVAS_HEIGHT / 2 - 50 + Math.sin(angle) * dist;
            
            ctx.fillStyle = '#90ee90';
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Text
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 40px Arial';
        ctx.fillText(`The wolf vomited ${modeName}!`, CANVAS_WIDTH/2, 100);
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function showMessage(msg, color = "#f1c40f") {
    const messageEl = document.createElement('div');
    messageEl.style.position = 'fixed';
    messageEl.style.top = '50%';
    messageEl.style.left = '50%';
    messageEl.style.transform = 'translate(-50%, -50%)';
    messageEl.style.background = color;
    messageEl.style.color = '#fff';
    messageEl.style.padding = '20px 40px';
    messageEl.style.borderRadius = '10px';
    messageEl.style.fontSize = '24px';
    messageEl.style.fontWeight = 'bold';
    messageEl.style.zIndex = '10000';
    messageEl.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
    messageEl.textContent = msg;
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.remove();
    }, 2000);
}

function showLockedMessage() {
    showMessage("🔒 This mode is locked! Buy it from the shop.", "#e74c3c");
}

function gameOver(message) {
    gameState = STATE_GAMEOVER;
    gameOverMessage = message;
}

let gameOverMessage = "";

function drawGameOver() {
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
    ctx.textAlign = 'left';
}

function handleGameInput(e) {
    if (e.key === 'r' || e.key === 'R') {
        if (gameState === STATE_GAMEOVER) {
            gameState = STATE_MENU;
            stopBackgroundMusic();
        } else {
            gameState = STATE_MENU;
        }
    } else if (e.key === 'Escape') {
        gameState = STATE_MENU;
        stopBackgroundMusic();
    }
    
    // Quiz mode specific input
    if (currentMode === MODE_QUIZ) {
        handleQuizInput(e);
    }
}

function rectIntersect(x1, y1, w1, h1, x2, y2, w2, h2) {
    return x2 < x1 + w1 && x2 + w2 > x1 && y2 < y1 + h1 && y2 + h2 > y1;
}

function saveHighScore(name, score, mode) {
    if (!leaderboards[mode]) {
        leaderboards[mode] = [];
    }
    
    leaderboards[mode].push({
        name: name,
        score: score,
        date: new Date().toISOString()
    });
    
    leaderboards[mode].sort((a, b) => b.score - a.score);
    leaderboards[mode] = leaderboards[mode].slice(0, 10);
    
    saveGameData();
}

// ============================================================================
// CHARACTER SELECT
// ============================================================================

function drawCharacterSelect() {
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    ctx.fillStyle = '#f1c40f';
    ctx.font = 'bold 40px Arial';
    ctx.textAlign = 'center';
    ctx.fillText("SELECT CHARACTER", CANVAS_WIDTH/2, 60);
    
    // Draw characters
    CHARACTERS.forEach((char, i) => {
        const x = 100 + (i % 4) * 150;
        const y = 150 + Math.floor(i / 4) * 150;
        
        const isSelected = i === selectedCharacters[0];
        
        ctx.fillStyle = isSelected ? char.color : '#333';
        ctx.fillRect(x, y, 100, 100);
        
        if (isSelected) {
            ctx.strokeStyle = '#f1c40f';
            ctx.lineWidth = 4;
            ctx.strokeRect(x, y, 100, 100);
        }
        
        ctx.font = '50px Arial';
        ctx.fillText(char.emoji, x + 50, y + 65);
        
        ctx.font = '14px Arial';
        ctx.fillStyle = '#fff';
        ctx.fillText(char.name, x + 50, y + 130);
    });
    
    ctx.font = '20px Arial';
    ctx.fillText("Use Arrow Keys to select, ENTER to confirm", CANVAS_WIDTH/2, CANVAS_HEIGHT - 40);
    ctx.textAlign = 'left';
}

function handleCharacterSelectInput(e) {
    const cols = 4;
    const current = selectedCharacters[0];
    
    if (e.key === 'ArrowLeft') {
        selectedCharacters[0] = (current - 1 + CHARACTERS.length) % CHARACTERS.length;
    } else if (e.key === 'ArrowRight') {
        selectedCharacters[0] = (current + 1) % CHARACTERS.length;
    } else if (e.key === 'ArrowUp') {
        selectedCharacters[0] = (current - cols + CHARACTERS.length) % CHARACTERS.length;
    } else if (e.key === 'ArrowDown') {
        selectedCharacters[0] = (current + cols) % CHARACTERS.length;
    } else if (e.key === 'Enter') {
        gameState = STATE_MENU;
    }
}

// ============================================================================
// MOUSE HANDLING
// ============================================================================

function handleMouseClick(e) {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    if (gameState === STATE_SECRET_HUNT) {
        if (secretHuntShopRect && 
            rectIntersect(mouseX, mouseY, 1, 1, 
                         secretHuntShopRect.x, secretHuntShopRect.y, 
                         secretHuntShopRect.w, secretHuntShopRect.h)) {
            gameState = STATE_MATH_CHALLENGE;
            mathAnswerInput = "";
        }
    }
}

// ============================================================================
// AUDIO SYSTEM
// ============================================================================

function initAudio() {
    try {
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioContext();
    } catch(e) {
        console.log('Audio not supported');
    }
}

function playBackgroundMusic() {
    if (musicPlaying) return;
    musicPlaying = true;
    secretHack.musicStillPlaying = true;
    showMessage("♪ Music Playing ♪", "#3498db");
}

function stopBackgroundMusic() {
    if (!secretHack.musicStillPlaying) {
        musicPlaying = false;
    }
}

// ============================================================================
// MERGE INSTRUCTIONS
// ============================================================================

/*
TO MERGE ALL FILES INTO ONE game.js:

1. Start with game_complete.js (foundation)
2. Add all functions from game_modes.js (Combine, Dilly Dolly, Mom, Final, Grass)
3. Add all functions from game_systems.js (Quiz, Makka Pakka, Relax modes, Shop)
4. Add all functions from this file (Effects, utilities, character select)
5. Make sure window.onload = init is at the very end

The complete merged file should be around 3000-4000 lines and include:
- All game modes working
- All secret codes functional
- Shop system complete
- Leaderboards with persistence
- Character selection
- All effects and animations
- Complete menu system matching Python version

Test each mode after merging to ensure everything works!
*/

// ============================================================================
// INITIALIZATION (Should be at end of merged file)
// ============================================================================

// window.onload = init; // Uncomment in merged file
