// ============================================================================
// BATTLEGAME - PART 3: Quiz, Makka Pakka, Relax Modes, Shop System, Effects
// ============================================================================

// ============================================================================
// QUIZ MODE
// ============================================================================

function initQuizMode() {
    quizMode.active = true;
    quizMode.currentQuestion = 0;
    quizMode.score = 0;
    quizMode.selectedAnswer = 0;
}

function updateQuizMode(dt) {
    // Handled by input
}

function drawQuizMode() {
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    const q = quizMode.questions[quizMode.currentQuestion];
    
    // Question
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 30px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`Question ${quizMode.currentQuestion + 1}/${quizMode.questions.length}`, CANVAS_WIDTH/2, 80);
    
    ctx.font = '24px Arial';
    ctx.fillText(q.q, CANVAS_WIDTH/2, 150);
    
    // Answers
    q.answers.forEach((answer, i) => {
        const y = 220 + i * 60;
        const isSelected = i === quizMode.selectedAnswer;
        
        ctx.fillStyle = isSelected ? '#3498db' : '#34495e';
        ctx.fillRect(200, y - 30, 400, 50);
        
        ctx.fillStyle = '#fff';
        ctx.fillText(`${i + 1}. ${answer}`, CANVAS_WIDTH/2, y);
    });
    
    // Score
    ctx.font = '20px Arial';
    ctx.fillText(`Score: ${quizMode.score}`, CANVAS_WIDTH/2, CANVAS_HEIGHT - 40);
    
    // Instructions
    ctx.font = '16px Arial';
    ctx.fillText("Use ↑↓ to select, ENTER to answer", CANVAS_WIDTH/2, CANVAS_HEIGHT - 10);
    
    ctx.textAlign = 'left';
}

function handleQuizInput(e) {
    if (e.key === 'ArrowUp') {
        quizMode.selectedAnswer = (quizMode.selectedAnswer - 1 + 4) % 4;
    } else if (e.key === 'ArrowDown') {
        quizMode.selectedAnswer = (quizMode.selectedAnswer + 1) % 4;
    } else if (e.key === 'Enter') {
        const q = quizMode.questions[quizMode.currentQuestion];
        if (quizMode.selectedAnswer === q.correct) {
            quizMode.score += 100;
            showMessage("Correct! ✅", "#2ecc71");
        } else {
            showMessage("Wrong! ❌", "#e74c3c");
        }
        
        quizMode.currentQuestion++;
        if (quizMode.currentQuestion >= quizMode.questions.length) {
            gameOver(`Quiz Complete! Score: ${quizMode.score}`);
        }
        quizMode.selectedAnswer = 0;
    }
}

// ============================================================================
// MAKKA PAKKA MODE (Face Washing Game)
// ============================================================================

function initMakkaPakkaMode() {
    makkaPakkaMode.active = true;
    makkaPakkaMode.player1Score = 0;
    makkaPakkaMode.player2Score = 0;
    makkaPakkaMode.timeLeft = 90;
    makkaPakkaMode.faces = [];
    
    for (let i = 0; i < 15; i++) {
        makkaPakkaMode.faces.push({
            x: 60 + Math.random() * (CANVAS_WIDTH - 120),
            y: 60 + Math.random() * (CANVAS_HEIGHT - 120),
            dirty: true,
            washProgress: 0
        });
    }
    
    players = [
        {
            x: CANVAS_WIDTH / 4,
            y: CANVAS_HEIGHT / 2,
            width: PLAYER_SIZE,
            height: PLAYER_SIZE,
            character: CHARACTERS[0]
        },
        {
            x: 3 * CANVAS_WIDTH / 4,
            y: CANVAS_HEIGHT / 2,
            width: PLAYER_SIZE,
            height: PLAYER_SIZE,
            character: CHARACTERS[1]
        }
    ];
}

function updateMakkaPakkaMode(dt) {
    makkaPakkaMode.timeLeft -= dt;
    
    if (makkaPakkaMode.timeLeft <= 0) {
        const winner = makkaPakkaMode.player1Score > makkaPakkaMode.player2Score ? "Player 1" : "Player 2";
        gameOver(`${winner} wins! Scores: P1:${makkaPakkaMode.player1Score} P2:${makkaPakkaMode.player2Score}`);
    }
    
    // Player 1 movement (WASD)
    const p1 = players[0];
    if (keys.w && p1.y > 0) p1.y -= PLAYER_SPEED;
    if (keys.s && p1.y < CANVAS_HEIGHT - p1.height) p1.y += PLAYER_SPEED;
    if (keys.a && p1.x > 0) p1.x -= PLAYER_SPEED;
    if (keys.d && p1.x < CANVAS_WIDTH - p1.width) p1.x += PLAYER_SPEED;
    
    // Player 2 movement (Arrows)
    const p2 = players[1];
    if (keys.ArrowUp && p2.y > 0) p2.y -= PLAYER_SPEED;
    if (keys.ArrowDown && p2.y < CANVAS_HEIGHT - p2.height) p2.y += PLAYER_SPEED;
    if (keys.ArrowLeft && p2.x > 0) p2.x -= PLAYER_SPEED;
    if (keys.ArrowRight && p2.x < CANVAS_WIDTH - p2.width) p2.x += PLAYER_SPEED;
    
    // Check face washing
    makkaPakkaMode.faces.forEach(face => {
        if (face.dirty) {
            // Player 1 washing
            if (rectIntersect(p1.x, p1.y, p1.width, p1.height, face.x, face.y, 40, 40)) {
                face.washProgress += dt * 2;
                if (face.washProgress >= 3) {
                    face.dirty = false;
                    makkaPakkaMode.player1Score++;
                    createParticles(face.x + 20, face.y + 20, '#3498db');
                }
            }
            // Player 2 washing
            if (rectIntersect(p2.x, p2.y, p2.width, p2.height, face.x, face.y, 40, 40)) {
                face.washProgress += dt * 2;
                if (face.washProgress >= 3) {
                    face.dirty = false;
                    makkaPakkaMode.player2Score++;
                    createParticles(face.x + 20, face.y + 20, '#e74c3c');
                }
            }
        }
    });
}

function drawMakkaPakkaMode() {
    // Background
    ctx.fillStyle = '#f0e68c';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw faces
    makkaPakkaMode.faces.forEach(face => {
        ctx.font = '40px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(face.dirty ? '😞' : '😊', face.x + 20, face.y + 30);
        
        // Wash progress bar
        if (face.dirty && face.washProgress > 0) {
            ctx.fillStyle = '#3498db';
            ctx.fillRect(face.x, face.y - 10, 40 * (face.washProgress / 3), 5);
        }
    });
    
    // Draw players
    players.forEach(p => drawPlayer(p));
    
    // UI
    ctx.textAlign = 'left';
    ctx.fillStyle = '#000';
    ctx.font = '24px Arial';
    ctx.fillText(`P1: ${makkaPakkaMode.player1Score}`, 10, 30);
    ctx.fillText(`P2: ${makkaPakkaMode.player2Score}`, 10, 60);
    ctx.fillText(`Time: ${Math.ceil(makkaPakkaMode.timeLeft)}s`, 10, 90);
    
    ctx.textAlign = 'center';
    ctx.font = 'bold 30px Arial';
    ctx.fillText("Wash the faces!", CANVAS_WIDTH/2, 40);
    ctx.textAlign = 'left';
}

// ============================================================================
// RELAX MODE - LETTER RAIN
// ============================================================================

let letterRainMode = {
    active: false,
    letters: [],
    time: 0
};

function initLetterRainMode() {
    letterRainMode.active = true;
    letterRainMode.letters = [];
    letterRainMode.time = 0;
}

function updateLetterRainMode(dt) {
    letterRainMode.time += dt;
    
    // Spawn letters
    if (Math.random() < 0.1) {
        const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        letterRainMode.letters.push({
            x: Math.random() * CANVAS_WIDTH,
            y: -30,
            letter: letters[Math.floor(Math.random() * letters.length)],
            speed: 50 + Math.random() * 100,
            rotation: Math.random() * Math.PI * 2,
            rotSpeed: (Math.random() - 0.5) * 2
        });
    }
    
    // Update letters
    for (let i = letterRainMode.letters.length - 1; i >= 0; i--) {
        const letter = letterRainMode.letters[i];
        letter.y += letter.speed * dt;
        letter.rotation += letter.rotSpeed * dt;
        
        if (letter.y > CANVAS_HEIGHT) {
            letterRainMode.letters.splice(i, 1);
        }
    }
}

function drawLetterRainMode() {
    // Calming background
    const gradient = ctx.createLinearGradient(0, 0, 0, CANVAS_HEIGHT);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw letters
    ctx.font = '40px Arial';
    ctx.textAlign = 'center';
    letterRainMode.letters.forEach(letter => {
        ctx.save();
        ctx.translate(letter.x, letter.y);
        ctx.rotate(letter.rotation);
        ctx.fillStyle = `hsla(${letter.y % 360}, 70%, 70%, 0.8)`;
        ctx.fillText(letter.letter, 0, 0);
        ctx.restore();
    });
    
    // Title
    ctx.textAlign = 'center';
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 40px Arial';
    ctx.shadowColor = '#000';
    ctx.shadowBlur = 10;
    ctx.fillText("Relax... Watch the letters fall...", CANVAS_WIDTH/2, 60);
    ctx.shadowBlur = 0;
    ctx.textAlign = 'left';
}

// ============================================================================
// RELAX MODE - COUNTING SHEEP
// ============================================================================

let sheepMode = {
    active: false,
    sheep: [],
    count: 0
};

function initSheepMode() {
    sheepMode.active = true;
    sheepMode.sheep = [];
    sheepMode.count = 0;
    secretHack.sheepModePlayed = true;
    secretHack.skibidiTriggered = true;
    saveGameData();
}

function updateSheepMode(dt) {
    // Spawn sheep
    if (sheepMode.sheep.length < 15 && Math.random() < 0.02) {
        sheepMode.sheep.push({
            x: -60,
            y: CANVAS_HEIGHT / 2 + (Math.random() - 0.5) * 100,
            speed: 100 + Math.random() * 50
        });
    }
    
    // Update sheep
    for (let i = sheepMode.sheep.length - 1; i >= 0; i--) {
        const sheep = sheepMode.sheep[i];
        sheep.x += sheep.speed * dt;
        
        if (sheep.x > CANVAS_WIDTH + 60) {
            sheepMode.sheep.splice(i, 1);
            sheepMode.count++;
        }
    }
}

function drawSheepMode() {
    // Night sky
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Stars
    ctx.fillStyle = '#fff';
    for (let i = 0; i < 50; i++) {
        const x = (i * 137) % CANVAS_WIDTH;
        const y = (i * 173) % CANVAS_HEIGHT;
        const size = (i % 3) + 1;
        ctx.fillRect(x, y, size, size);
    }
    
    // Moon
    ctx.fillStyle = '#f0e68c';
    ctx.beginPath();
    ctx.arc(CANVAS_WIDTH - 100, 100, 50, 0, Math.PI * 2);
    ctx.fill();
    
    // Fence
    ctx.fillStyle = '#8b4513';
    for (let i = 0; i < CANVAS_WIDTH; i += 60) {
        ctx.fillRect(i, CANVAS_HEIGHT / 2 + 50, 5, 80);
        ctx.fillRect(i, CANVAS_HEIGHT / 2 + 80, 60, 5);
        ctx.fillRect(i, CANVAS_HEIGHT / 2 + 110, 60, 5);
    }
    
    // Draw sheep
    ctx.font = '50px Arial';
    ctx.textAlign = 'center';
    sheepMode.sheep.forEach(sheep => {
        ctx.fillText('🐑', sheep.x, sheep.y);
    });
    
    // Counter
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 60px Arial';
    ctx.shadowColor = '#000';
    ctx.shadowBlur = 10;
    ctx.fillText(`${sheepMode.count} sheep...`, CANVAS_WIDTH/2, 100);
    ctx.font = '30px Arial';
    ctx.fillText("Zzz...", CANVAS_WIDTH/2, 150);
    ctx.shadowBlur = 0;
    ctx.textAlign = 'left';
}

// ============================================================================
// COIN COLLECTION MODE
// ============================================================================

let coinMode = {
    active: false,
    coins: [],
    collected: 0,
    timeLeft: 60
};

function initCoinCollection() {
    coinMode.active = true;
    coinMode.coins = [];
    coinMode.collected = 0;
    coinMode.timeLeft = 60;
    
    for (let i = 0; i < 30; i++) {
        coinMode.coins.push({
            x: Math.random() * CANVAS_WIDTH,
            y: Math.random() * CANVAS_HEIGHT,
            collected: false
        });
    }
    
    players = [{
        x: CANVAS_WIDTH / 2,
        y: CANVAS_HEIGHT / 2,
        width: PLAYER_SIZE,
        height: PLAYER_SIZE,
        character: CHARACTERS[selectedCharacters[0]]
    }];
}

function updateCoinCollection(dt) {
    coinMode.timeLeft -= dt;
    
    if (coinMode.timeLeft <= 0) {
        gameOver(`Collected ${coinMode.collected} coins!`);
    }
    
    // Player movement
    const p = players[0];
    if (keys.w && p.y > 0) p.y -= PLAYER_SPEED;
    if (keys.s && p.y < CANVAS_HEIGHT - p.height) p.y += PLAYER_SPEED;
    if (keys.a && p.x > 0) p.x -= PLAYER_SPEED;
    if (keys.d && p.x < CANVAS_WIDTH - p.width) p.x += PLAYER_SPEED;
    
    // Collect coins
    coinMode.coins.forEach(coin => {
        if (!coin.collected && rectIntersect(p.x, p.y, p.width, p.height, coin.x, coin.y, 30, 30)) {
            coin.collected = true;
            coinMode.collected++;
            createParticles(coin.x, coin.y, 'gold');
        }
    });
}

function drawCoinCollection() {
    ctx.fillStyle = '#34495e';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw coins
    ctx.font = '30px Arial';
    ctx.textAlign = 'center';
    coinMode.coins.forEach(coin => {
        if (!coin.collected) {
            ctx.fillText('🪙', coin.x, coin.y);
        }
    });
    
    // Draw player
    drawPlayer(players[0]);
    
    // UI
    ctx.textAlign = 'left';
    ctx.fillStyle = '#fff';
    ctx.font = '24px Arial';
    ctx.fillText(`Coins: ${coinMode.collected}`, 10, 30);
    ctx.fillText(`Time: ${Math.ceil(coinMode.timeLeft)}s`, 10, 60);
}

// ============================================================================
// ESCAPE MOM MODE, CAPTURE FLAG, 3D ADVENTURE (Simplified)
// ============================================================================

function initEscapeMom() {
    initMomMode(); // Reuse Mom Mode
}

function updateEscapeMom(dt) {
    updateMomMode(dt);
}

function drawEscapeMom() {
    drawMomMode();
}

function initCaptureFlag() {
    showMessage("Capture the Flag - Coming Soon!");
    gameState = STATE_MENU;
}

function updateCaptureFlag(dt) {}
function drawCaptureFlag() {}

function init3DAdventure() {
    showMessage("3D Adventure - Coming Soon!");
    gameState = STATE_MENU;
}

function update3DAdventure(dt) {}
function draw3DAdventure() {}

// ============================================================================
// AI HELPER MODE
// ============================================================================

function handleAIHelper() {
    showMessage("AI Helper: I'm here to help! Check the menu for all game modes. Secret: Type 'tralala' then '67' then '6776'!");
}

// ============================================================================
// SHOP SYSTEM (Complete)
// ============================================================================

function drawShop() {
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    ctx.fillStyle = '#f1c40f';
    ctx.font = 'bold 50px Arial';
    ctx.textAlign = 'center';
    ctx.fillText("THE SHOP", CANVAS_WIDTH/2, 80);
    
    ctx.font = '20px Arial';
    ctx.fillStyle = '#fff';
    ctx.fillText("Enter Code to Buy:", CANVAS_WIDTH/2, 140);
    
    // Input box
    ctx.fillStyle = '#34495e';
    ctx.fillRect(CANVAS_WIDTH/2 - 150, 160, 300, 50);
    ctx.fillStyle = '#fff';
    ctx.font = '30px Arial';
    const cursor = Math.floor(Date.now() / 500) % 2 === 0 ? "|" : "";
    ctx.fillText(shopCodeInput + cursor, CANVAS_WIDTH/2, 195);
    
    // Items
    const items = [
        { name: "Relax Mode", code: "relax", key: "relaxMode" },
        { name: "Makka Pakka", code: "makkapakka", key: "makkaPakkaMode" },
        { name: "Escape Mom", code: "escapemom", key: "escapeMomMode" },
        { name: "Capture Flag", code: "captureflag", key: "captureFlagMode" },
        { name: "Survival", code: "survival", key: "survivalMode" },
        { name: "3D Adventure", code: "3d", key: "adventure3dMode" },
        { name: "Dilly Dolly", code: "dillydolly", key: "dillyDollyMode" }
    ];
    
    ctx.font = '20px Arial';
    ctx.textAlign = 'left';
    let startY = 250;
    items.forEach((item, i) => {
        const y = startY + i * 40;
        const owned = sessionPurchases[item.key];
        
        ctx.fillStyle = owned ? '#2ecc71' : '#95a5a6';
        ctx.fillText(item.name, 200, y);
        
        ctx.fillStyle = '#bdc3c7';
        ctx.fillText(owned ? "OWNED ✅" : `Code: ${item.code}`, 500, y);
    });
    
    ctx.fillStyle = '#e74c3c';
    ctx.textAlign = 'center';
    ctx.fillText("Press ESC to Return", CANVAS_WIDTH/2, 550);
    ctx.textAlign = 'left';
}

function handleShopInput(e) {
    if (e.key === 'Escape') {
        gameState = STATE_MENU;
        shopCodeInput = "";
    } else if (e.key === 'Backspace') {
        shopCodeInput = shopCodeInput.slice(0, -1);
    } else if (e.key === 'Enter') {
        processShopCode(shopCodeInput);
        shopCodeInput = "";
    } else if (e.key.length === 1) {
        shopCodeInput += e.key.toLowerCase();
    }
}

function processShopCode(code) {
    const items = {
        "relax": "relaxMode",
        "makkapakka": "makkaPakkaMode",
        "escapemom": "escapeMomMode",
        "captureflag": "captureFlagMode",
        "survival": "survivalMode",
        "3d": "adventure3dMode",
        "dillydolly": "dillyDollyMode"
    };
    
    if (items[code]) {
        sessionPurchases[items[code]] = true;
        showMessage("Unlocked! ✅", "#2ecc71");
    } else {
        showMessage("Invalid code!", "#e74c3c");
    }
}

// ============================================================================
// SECRET HUNT & MATH CHALLENGE
// ============================================================================

function startSecretHunt() {
    gameState = STATE_SECRET_HUNT;
    secretHuntWrongRects = [];
    
    for (let i = 0; i < 20; i++) {
        secretHuntWrongRects.push({
            x: Math.random() * (CANVAS_WIDTH - 100),
            y: Math.random() * (CANVAS_HEIGHT - 50) + 100,
            w: 80,
            h: 40
        });
    }
    
    secretHuntShopRect = {
        x: Math.random() * (CANVAS_WIDTH - 100),
        y: Math.random() * (CANVAS_HEIGHT - 50) + 100,
        w: 80,
        h: 40
    };
}

function drawSecretHunt() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    ctx.fillStyle = '#e74c3c';
    ctx.font = 'bold 40px Arial';
    ctx.textAlign = 'center';
    ctx.fillText("SECRET HUNT", CANVAS_WIDTH/2, 60);
    
    ctx.fillStyle = '#fff';
    ctx.font = '20px Arial';
    ctx.fillText("Find the hidden 'SHOP' button!", CANVAS_WIDTH/2, 100);
    
    // Wrong buttons
    secretHuntWrongRects.forEach(rect => {
        ctx.fillStyle = '#c0392b';
        ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
        ctx.fillStyle = '#fff';
        ctx.font = '16px Arial';
        ctx.fillText("NOPE", rect.x + rect.w/2, rect.y + rect.h/2 + 5);
    });
    
    // Real button
    if (secretHuntShopRect) {
        ctx.fillStyle = '#27ae60';
        ctx.fillRect(secretHuntShopRect.x, secretHuntShopRect.y, secretHuntShopRect.w, secretHuntShopRect.h);
        ctx.fillStyle = '#fff';
        ctx.fillText("SHOP", secretHuntShopRect.x + secretHuntShopRect.w/2, secretHuntShopRect.y + secretHuntShopRect.h/2 + 5);
    }
    
    ctx.textAlign = 'left';
}

function drawMathChallenge() {
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    ctx.fillStyle = '#f1c40f';
    ctx.font = 'bold 40px Arial';
    ctx.textAlign = 'center';
    ctx.fillText("MATH CHALLENGE", CANVAS_WIDTH/2, 100);
    
    ctx.fillStyle = '#fff';
    ctx.font = '30px Arial';
    ctx.fillText("Solve to Unlock Shop:", CANVAS_WIDTH/2, 200);
    
    ctx.font = '50px Arial';
    ctx.fillText("10 + 10 = ?", CANVAS_WIDTH/2, 300);
    
    // Input
    ctx.fillStyle = '#34495e';
    ctx.fillRect(CANVAS_WIDTH/2 - 100, 350, 200, 60);
    ctx.fillStyle = '#fff';
    const cursor = Math.floor(Date.now() / 500) % 2 === 0 ? "|" : "";
    ctx.fillText(mathAnswerInput + cursor, CANVAS_WIDTH/2, 395);
    
    ctx.font = '20px Arial';
    ctx.fillText("Type answer and press ENTER", CANVAS_WIDTH/2, 500);
    ctx.textAlign = 'left';
}

function handleMathInput(e) {
    if (e.key === 'Enter') {
        if (mathAnswerInput === "20") {
            sessionPurchases.shopUnlocked = true;
            gameState = STATE_SHOP;
            mathAnswerInput = "";
            showMessage("Shop Unlocked! ✅", "#2ecc71");
        } else {
            mathAnswerInput = "";
            showMessage("Wrong answer! Try again.", "#e74c3c");
        }
    } else if (e.key === 'Backspace') {
        mathAnswerInput = mathAnswerInput.slice(0, -1);
    } else if (!isNaN(parseInt(e.key))) {
        mathAnswerInput += e.key;
    }
}

// ============================================================================
// LEADERBOARD
// ============================================================================

function showLeaderboardScreen(type) {
    currentLeaderboardType = type;
    gameState = STATE_LEADERBOARD;
}

let currentLeaderboardType = 'survival';

function drawLeaderboard() {
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    ctx.fillStyle = '#f1c40f';
    ctx.font = 'bold 40px Arial';
    ctx.textAlign = 'center';
    const title = currentLeaderboardType === 'survival' ? "Survival Leaderboard" : "Mom Mode Leaderboard";
    ctx.fillText(title, CANVAS_WIDTH/2, 60);
    
    const scores = leaderboards[currentLeaderboardType] || [];
    
    ctx.fillStyle = '#fff';
    ctx.font = '24px Arial';
    if (scores.length === 0) {
        ctx.fillText("No scores yet!", CANVAS_WIDTH/2, 200);
    } else {
        scores.slice(0, 10).forEach((entry, i) => {
            const y = 120 + i * 40;
            ctx.textAlign = 'left';
            ctx.fillText(`${i + 1}. ${entry.name}`, 100, y);
            ctx.textAlign = 'right';
            ctx.fillText(`${entry.score}`, CANVAS_WIDTH - 100, y);
        });
    }
    
    ctx.textAlign = 'center';
    ctx.font = '20px Arial';
    ctx.fillText("Press ESC to return", CANVAS_WIDTH/2, CANVAS_HEIGHT - 40);
    ctx.textAlign = 'left';
}

// Continue in final part...
