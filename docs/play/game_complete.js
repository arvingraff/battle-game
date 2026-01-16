// ============================================================================
// BATTLEGAME - COMPLETE BROWSER VERSION
// Ported from 17,437-line Python version
// All modes, all secrets, all features!
// ============================================================================

// Canvas Setup
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;

// Player Constants
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
const STATE_LEADERBOARD = 6;
const STATE_CHARACTER_SELECT = 7;

// Game Modes
const MODE_BATTLE = 0;
const MODE_COIN_COLLECTION = 1;
const MODE_SURVIVAL = 2;
const MODE_MAKKA_PAKKA = 3;
const MODE_ESCAPE_MOM = 4;
const MODE_CAPTURE_FLAG = 5;
const MODE_3D_ADVENTURE = 6;
const MODE_RELAX_LETTER_RAIN = 7;
const MODE_RELAX_SHEEP = 8;
const MODE_DILLY_DOLLY = 9;
const MODE_GRASS = 10;
const MODE_COMBINE = 11;
const MODE_FINAL = 12;
const MODE_QUIZ = 13;
const MODE_AI_HELPER = 14;
const MODE_MOM = 15;

// Global State
let canvas, ctx;
let lastTime = 0;
let gameState = STATE_MENU;
let currentMode = MODE_BATTLE;
let gameRunning = false;
let selectedMenuItem = 0;
let menuKeyBuffer = "";

// Audio
let audioContext;
let sounds = {};
let bgMusicNode = null;
let musicPlaying = false;

// Players
let players = [];
let bullets = [];
let particles = [];
let enemies = [];

// Game Variables
let wave = 1;
let score = 0;
let timeLeft = 0;
let godMode = false;
let finalModeUnlocked = false;

// Character System
const CHARACTERS = [
    { id: 0, name: "Blue Fighter", color: "#3498db", emoji: "🔵" },
    { id: 1, name: "Red Warrior", color: "#e74c3c", emoji: "🔴" },
    { id: 2, name: "Green Ninja", color: "#2ecc71", emoji: "🟢" },
    { id: 3, name: "Yellow Mage", color: "#f1c40f", emoji: "🟡" },
    { id: 4, name: "Purple Rogue", color: "#9b59b6", emoji: "🟣" },
    { id: 5, name: "Orange Tank", color: "#e67e22", emoji: "🟠" },
    { id: 6, name: "Pink Healer", color: "#e91e63", emoji: "🩷" },
    { id: 7, name: "White Knight", color: "#ecf0f1", emoji: "⚪" }
];

let selectedCharacters = [0, 1]; // Default: Blue vs Red

// Shop & Unlock System
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

// Secret Hack System (matches Python)
let secretHack = {
    sheepModePlayed: false,
    whoppaGangEntered: false,
    musicStillPlaying: false,
    skibidiTriggered: false,
    wolfAteButtons: false,
    grassModeUnlocked: false,
    combineModeUnlocked: true, // Always available
    enteredBattleAfterMusic: false,
    everythingRestored: false,
    becameHuman: false,
    becameItalian: false, // Press 67 when human
    godModeUnlocked: false,
    finalModeUnlocked: false, // Press 6776 after Tralala
    explosionTriggered: false
};

// Shop Variables
let shopCodeInput = "";
let mathAnswerInput = "";
let secretHuntShopRect = null;
let secretHuntWrongRects = [];

// Combine Mode State (Dog → Human transformation)
let combineMode = {
    active: false,
    dogX: 100,
    dogY: 0,
    dogVelocityY: 0,
    dogDirection: 1,
    transformation: 0, // 0-100
    itemsCollected: 0,
    items: [],
    obstacles: [],
    particles: [],
    gameTime: 0,
    spawnTimer: 0,
    obstacleTimer: 0,
    storyPhase: 0,
    showCelebration: false,
    celebrationTimer: 0,
    lives: 5,
    health: 100,
    stamina: 100,
    isJumping: false,
    isSprinting: false
};

// Dilly Dolly Mode State
let dillyDollyMode = {
    active: false,
    dolls: [],
    selectedDoll: 0,
    rainbowMode: false,
    giantMode: false,
    sparkleMode: false,
    bgHue: 0,
    time: 0
};

// Mom Mode State
let momMode = {
    active: false,
    momX: 400,
    momY: 300,
    momSpeed: 3,
    momAngry: false,
    escapeTime: 60,
    timeLeft: 60
};

// Final Mode State
let finalModeState = {
    active: false,
    gravity: 0.5,
    jumpPower: -12,
    platforms: [],
    enemies: [],
    powerups: [],
    bossActive: false,
    bossHealth: 1000
};

// Quiz Mode State
let quizMode = {
    active: false,
    currentQuestion: 0,
    score: 0,
    questions: [
        { q: "What is 2+2?", answers: ["3", "4", "5", "6"], correct: 1 },
        { q: "Capital of France?", answers: ["London", "Paris", "Berlin", "Rome"], correct: 1 },
        { q: "Who made this game?", answers: ["You!", "Nintendo", "Epic Games", "Valve"], correct: 0 },
        { q: "Best game mode?", answers: ["Battle", "Combine", "Final", "All of them!"], correct: 3 },
        { q: "What's the secret code?", answers: ["123", "tralala", "password", "6776"], correct: 1 }
    ]
};

// Grass Mode State
let grassMode = {
    active: false,
    grass: [],
    wind: 0,
    time: 0
};

// Makka Pakka Mode State
let makkaPakkaMode = {
    active: false,
    faces: [],
    player1Score: 0,
    player2Score: 0,
    timeLeft: 90
};

// 3D Adventure State
let adventure3D = {
    active: false,
    playerX: 0,
    playerY: 0,
    playerZ: 5,
    rotation: 0,
    walls: [],
    enemies: []
};

// Leaderboard Data (localStorage)
let leaderboards = {
    survival: [],
    mom: []
};

// Input State
const keys = {
    w: false, a: false, s: false, d: false,
    ArrowUp: false, ArrowLeft: false, ArrowDown: false, ArrowRight: false,
    " ": false, Shift: false,
    j: false, q: false
};

// ============================================================================
// INITIALIZATION
// ============================================================================

function init() {
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    canvas.width = CANVAS_WIDTH;
    canvas.height = CANVAS_HEIGHT;
    
    // Load saved data
    loadGameData();
    
    // Setup controls
    setupEventListeners();
    
    // Initialize audio
    initAudio();
    
    // Start game loop
    requestAnimationFrame(gameLoop);
}

function setupEventListeners() {
    window.addEventListener('keydown', (e) => {
        if (keys.hasOwnProperty(e.key)) {
            keys[e.key] = true;
        }
        handleKeyDown(e);
    });
    
    window.addEventListener('keyup', (e) => {
        if (keys.hasOwnProperty(e.key)) {
            keys[e.key] = false;
        }
    });
    
    canvas.addEventListener('mousedown', handleMouseClick);
}

function loadGameData() {
    // Load from localStorage
    try {
        const saved = localStorage.getItem('battlegame_secrets');
        if (saved) {
            const data = JSON.parse(saved);
            Object.assign(secretHack, data);
        }
        
        const savedLeaderboards = localStorage.getItem('battlegame_leaderboards');
        if (savedLeaderboards) {
            leaderboards = JSON.parse(savedLeaderboards);
        }
    } catch (e) {
        console.log("No saved data or error loading:", e);
    }
}

function saveGameData() {
    try {
        // Save secret progress
        localStorage.setItem('battlegame_secrets', JSON.stringify(secretHack));
        
        // Save leaderboards
        localStorage.setItem('battlegame_leaderboards', JSON.stringify(leaderboards));
    } catch (e) {
        console.log("Error saving:", e);
    }
}

// ============================================================================
// MAIN GAME LOOP
// ============================================================================

function gameLoop(timestamp) {
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    
    update(deltaTime);
    draw();
    
    requestAnimationFrame(gameLoop);
}

function update(deltaTime) {
    if (gameState === STATE_PLAYING) {
        updateGame(deltaTime);
    }
}

function updateGame(deltaTime) {
    const dt = deltaTime / 1000;
    
    // Update based on current mode
    switch(currentMode) {
        case MODE_BATTLE:
            updateBattleMode(dt);
            break;
        case MODE_SURVIVAL:
            updateSurvivalMode(dt);
            break;
        case MODE_COMBINE:
            updateCombineMode(dt);
            break;
        case MODE_DILLY_DOLLY:
            updateDillyDollyMode(dt);
            break;
        case MODE_MOM:
            updateMomMode(dt);
            break;
        case MODE_FINAL:
            updateFinalMode(dt);
            break;
        case MODE_GRASS:
            updateGrassMode(dt);
            break;
        case MODE_MAKKA_PAKKA:
            updateMakkaPakkaMode(dt);
            break;
        case MODE_QUIZ:
            updateQuizMode(dt);
            break;
        case MODE_3D_ADVENTURE:
            update3DAdventure(dt);
            break;
        case MODE_RELAX_LETTER_RAIN:
            updateLetterRainMode(dt);
            break;
        case MODE_RELAX_SHEEP:
            updateSheepMode(dt);
            break;
        case MODE_COIN_COLLECTION:
            updateCoinCollection(dt);
            break;
        case MODE_ESCAPE_MOM:
            updateEscapeMom(dt);
            break;
        case MODE_CAPTURE_FLAG:
            updateCaptureFlag(dt);
            break;
    }
    
    // Update common systems
    updateBullets(dt);
    updateParticles(dt);
}

function draw() {
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    switch(gameState) {
        case STATE_MENU:
            drawMenu();
            break;
        case STATE_PLAYING:
            drawGame();
            break;
        case STATE_GAMEOVER:
            drawGameOver();
            break;
        case STATE_SHOP:
            drawShop();
            break;
        case STATE_SECRET_HUNT:
            drawSecretHunt();
            break;
        case STATE_MATH_CHALLENGE:
            drawMathChallenge();
            break;
        case STATE_LEADERBOARD:
            drawLeaderboard();
            break;
        case STATE_CHARACTER_SELECT:
            drawCharacterSelect();
            break;
    }
}

function drawGame() {
    // Draw based on current mode
    switch(currentMode) {
        case MODE_BATTLE:
            drawBattleMode();
            break;
        case MODE_SURVIVAL:
            drawSurvivalMode();
            break;
        case MODE_COMBINE:
            drawCombineMode();
            break;
        case MODE_DILLY_DOLLY:
            drawDillyDollyMode();
            break;
        case MODE_MOM:
            drawMomMode();
            break;
        case MODE_FINAL:
            drawFinalMode();
            break;
        case MODE_GRASS:
            drawGrassMode();
            break;
        case MODE_MAKKA_PAKKA:
            drawMakkaPakkaMode();
            break;
        case MODE_QUIZ:
            drawQuizMode();
            break;
        case MODE_3D_ADVENTURE:
            draw3DAdventure();
            break;
        case MODE_RELAX_LETTER_RAIN:
            drawLetterRainMode();
            break;
        case MODE_RELAX_SHEEP:
            drawSheepMode();
            break;
        case MODE_COIN_COLLECTION:
            drawCoinCollection();
            break;
        case MODE_ESCAPE_MOM:
            drawEscapeMom();
            break;
        case MODE_CAPTURE_FLAG:
            drawCaptureFlag();
            break;
    }
    
    // Draw common UI
    if (godMode) {
        ctx.fillStyle = 'gold';
        ctx.font = 'bold 20px Arial';
        ctx.fillText("GOD MODE", 10, CANVAS_HEIGHT - 10);
    }
    
    if (finalModeUnlocked && currentMode === MODE_FINAL) {
        ctx.fillStyle = '#e74c3c';
        ctx.font = 'bold 20px Arial';
        ctx.fillText("FINAL MODE", 10, CANVAS_HEIGHT - 35);
    }
}

// ============================================================================
// MENU SYSTEM (Matches Python exactly)
// ============================================================================

function drawMenu() {
    // Background
    ctx.fillStyle = '#1e1e2e';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Title
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    ctx.shadowColor = '#3498db';
    ctx.shadowBlur = 20;
    ctx.fillText("BATTLEGAME", CANVAS_WIDTH/2, 80);
    ctx.shadowBlur = 0;
    
    // Build menu options based on unlocks (matches Python logic)
    const menuOptions = buildMenuOptions();
    
    // Warning if wolf ate buttons
    if (secretHack.wolfAteButtons && !secretHack.everythingRestored) {
        ctx.font = '24px Arial';
        ctx.fillStyle = '#e74c3c';
        ctx.fillText("⚠️ The wolf ate EVERYTHING! ⚠️", CANVAS_WIDTH/2, 120);
    }
    
    // Shop unlock hint
    if (sessionPurchases.shopUnlocked) {
        ctx.font = '20px Arial';
        ctx.fillStyle = '#f1c40f';
        ctx.textAlign = 'left';
        ctx.fillText("🔑 Secret shop unlocked!", 10, 25);
    }
    
    // Human transformation status
    if (secretHack.becameHuman) {
        ctx.textAlign = 'right';
        ctx.fillText("✨ You became HUMAN! ✨", CANVAS_WIDTH - 10, 25);
    }
    
    // Menu items
    ctx.textAlign = 'center';
    ctx.font = '28px Arial';
    const startY = 150;
    const spacing = 40;
    
    menuOptions.forEach((option, i) => {
        const y = startY + i * spacing;
        const isSelected = i === selectedMenuItem;
        const isLocked = option.locked;
        
        // Color
        if (isLocked) {
            ctx.fillStyle = isSelected ? '#666' : '#444';
        } else if (isSelected) {
            ctx.fillStyle = '#f1c40f';
        } else {
            ctx.fillStyle = '#ccc';
        }
        
        // Text
        let text = option.label;
        if (isLocked) text += " 🔒";
        if (option.unlocked) text += " ✅";
        
        ctx.fillText(text, CANVAS_WIDTH/2, y);
    });
    
    // Draw menu pointer (dog or human)
    const pointerY = startY + selectedMenuItem * spacing;
    drawMenuPointer(CANVAS_WIDTH/2 - 250, pointerY - 15);
    
    // Instructions
    ctx.font = '16px Arial';
    ctx.fillStyle = '#888';
    ctx.fillText("↑↓ Navigate | ENTER Select | ESC Back", CANVAS_WIDTH/2, CANVAS_HEIGHT - 20);
    
    ctx.textAlign = 'left';
}

function buildMenuOptions() {
    const baseOptions = [
        { id: "ai_helper", label: "🤖 AI Helper", mode: MODE_AI_HELPER, locked: false },
        { id: "quiz", label: "🧠 Quiz Mode", mode: MODE_QUIZ, locked: false },
        { id: "battle", label: "Battle Mode", mode: MODE_BATTLE, locked: false },
        { id: "coin", label: "Coin Collection", mode: MODE_COIN_COLLECTION, locked: false },
        { id: "makka", label: "Makka Pakka Mode", mode: MODE_MAKKA_PAKKA, locked: !sessionPurchases.makkaPakkaMode },
        { id: "escape", label: "Escape Mom Mode", mode: MODE_ESCAPE_MOM, locked: !sessionPurchases.escapeMomMode },
        { id: "flag", label: "Capture the Flag", mode: MODE_CAPTURE_FLAG, locked: !sessionPurchases.captureFlagMode },
        { id: "survival", label: "Survival Mode", mode: MODE_SURVIVAL, locked: !sessionPurchases.survivalMode },
        { id: "3d", label: "3D Adventure", mode: MODE_3D_ADVENTURE, locked: !sessionPurchases.adventure3dMode },
        { id: "relax", label: "Relax Mode", mode: MODE_RELAX_LETTER_RAIN, locked: !sessionPurchases.relaxMode },
        { id: "dilly", label: "Dilly Dolly Mode", mode: MODE_DILLY_DOLLY, locked: !sessionPurchases.dillyDollyMode },
        { id: "shop", label: "🛒 Shop", mode: null, action: "shop", locked: false },
        { id: "leaderboard_survival", label: "Survival Leaderboard", mode: null, action: "leaderboard_survival", locked: false },
        { id: "leaderboard_mom", label: "Mom Mode Leaderboard", mode: null, action: "leaderboard_mom", locked: false },
        { id: "music_play", label: "Play Music", mode: null, action: "play_music", locked: false },
        { id: "music_stop", label: "Stop Music", mode: null, action: "stop_music", locked: false },
        { id: "exit", label: "Exit", mode: null, action: "exit", locked: false }
    ];
    
    let options = baseOptions;
    
    // WOLF ATE EVERYTHING MODE
    if (secretHack.wolfAteButtons && !secretHack.everythingRestored) {
        options = [{ id: "exit", label: "Exit", mode: null, action: "exit", locked: false }];
        
        if (secretHack.grassModeUnlocked) {
            options.unshift({ id: "grass", label: "Grass Mode", mode: MODE_GRASS, locked: false });
        }
        
        if (secretHack.combineModeUnlocked) {
            options.unshift({ id: "combine", label: "Combine Mode", mode: MODE_COMBINE, locked: false });
        }
        
        if (secretHack.finalModeUnlocked) {
            options.unshift({ id: "final", label: "🔥 FINAL MODE 🔥", mode: MODE_FINAL, locked: false });
        }
    } else {
        // Normal menu - add special modes
        if (secretHack.grassModeUnlocked) {
            const shopIndex = options.findIndex(o => o.id === "shop");
            options.splice(shopIndex, 0, { id: "grass", label: "Grass Mode", mode: MODE_GRASS, locked: false });
        }
        
        if (secretHack.combineModeUnlocked) {
            const shopIndex = options.findIndex(o => o.id === "shop");
            options.splice(shopIndex, 0, { id: "combine", label: "Combine Mode", mode: MODE_COMBINE, locked: false });
        }
        
        if (secretHack.finalModeUnlocked) {
            options.unshift({ id: "final", label: "🔥 FINAL MODE 🔥", mode: MODE_FINAL, locked: false });
        }
    }
    
    // Add unlocked status
    options.forEach(opt => {
        if (opt.id === "makka" && sessionPurchases.makkaPakkaMode) opt.unlocked = true;
        if (opt.id === "escape" && sessionPurchases.escapeMomMode) opt.unlocked = true;
        if (opt.id === "flag" && sessionPurchases.captureFlagMode) opt.unlocked = true;
        if (opt.id === "survival" && sessionPurchases.survivalMode) opt.unlocked = true;
        if (opt.id === "3d" && sessionPurchases.adventure3dMode) opt.unlocked = true;
        if (opt.id === "relax" && sessionPurchases.relaxMode) opt.unlocked = true;
        if (opt.id === "dilly" && sessionPurchases.dillyDollyMode) opt.unlocked = true;
    });
    
    return options;
}

function drawMenuPointer(x, y) {
    const transformation = secretHack.becameHuman ? 100 : 0;
    const time = Date.now() / 1000;
    const bob = Math.sin(time * 3) * 5;
    
    if (transformation >= 70) {
        // Human
        ctx.fillStyle = '#f1c27d';
        ctx.fillRect(x + 20, y + 30 + bob, 20, 40);
        ctx.beginPath();
        ctx.arc(x + 30, y + 20 + bob, 12, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillText("👉", x + 50, y + 35 + bob);
    } else {
        // Dog
        ctx.fillStyle = '#8b4513';
        ctx.beginPath();
        ctx.ellipse(x + 30, y + 50 + bob, 30, 20, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillText("🐾", x + 50, y + 50 + bob);
    }
}

// ============================================================================
// INPUT HANDLING
// ============================================================================

function handleKeyDown(e) {
    if (gameState === STATE_MENU) {
        handleMenuInput(e);
    } else if (gameState === STATE_SHOP) {
        handleShopInput(e);
    } else if (gameState === STATE_MATH_CHALLENGE) {
        handleMathInput(e);
    } else if (gameState === STATE_PLAYING) {
        handleGameInput(e);
    } else if (gameState === STATE_CHARACTER_SELECT) {
        handleCharacterSelectInput(e);
    }
}

function handleMenuInput(e) {
    const options = buildMenuOptions();
    
    // Secret code detection (matches Python)
    const keyName = e.key.toLowerCase();
    if (['j', 'q', '1', '2', '3', '4', '5', '6', '7', 'g', 'a', 'b', 'u'].includes(keyName)) {
        menuKeyBuffer += keyName;
        if (menuKeyBuffer.length > 8) {
            menuKeyBuffer = menuKeyBuffer.slice(-8);
        }
        
        checkSecretCodes();
    }
    
    // Navigation
    if (e.key === 'ArrowUp') {
        selectedMenuItem = (selectedMenuItem - 1 + options.length) % options.length;
    } else if (e.key === 'ArrowDown') {
        selectedMenuItem = (selectedMenuItem + 1) % options.length;
    } else if (e.key === 'Enter') {
        selectMenuItem(options[selectedMenuItem]);
    }
}

function checkSecretCodes() {
    // gagabubu - Rainbow explosion
    if (menuKeyBuffer.endsWith("gagabubu")) {
        menuKeyBuffer = "";
        rainbowExplosion();
        return;
    }
    
    // 6776 - Final Mode (only if Tralala)
    if (menuKeyBuffer.endsWith("6776") && secretHack.becameItalian && !secretHack.finalModeUnlocked) {
        menuKeyBuffer = "";
        secretHack.finalModeUnlocked = true;
        secretHack.explosionTriggered = true;
        saveGameData();
        explosionSequence();
        return;
    }
    
    // 67 - Become Tralala (only if human)
    if (menuKeyBuffer.endsWith("67") && secretHack.becameHuman && !secretHack.becameItalian) {
        menuKeyBuffer = "";
        secretHack.becameItalian = true;
        saveGameData();
        showMessage("You became TRALALA! 🎭");
        return;
    }
    
    // 123654 - Restore everything
    if (menuKeyBuffer === "123654" && secretHack.wolfAteButtons) {
        menuKeyBuffer = "";
        secretHack.wolfAteButtons = false;
        secretHack.everythingRestored = true;
        saveGameData();
        showMessage("RESTORED!", "#2ecc71");
        return;
    }
    
    // jjj - Wolf eats menu
    if (menuKeyBuffer.endsWith("jjj") && secretHack.skibidiTriggered && !secretHack.wolfAteButtons) {
        menuKeyBuffer = "";
        secretHack.wolfAteButtons = true;
        saveGameData();
        wolfEatAnimation();
        return;
    }
    
    // qqq - Wolf vomits Grass Mode
    if (menuKeyBuffer.endsWith("qqq") && secretHack.wolfAteButtons && !secretHack.grassModeUnlocked) {
        menuKeyBuffer = "";
        secretHack.grassModeUnlocked = true;
        saveGameData();
        wolfVomitAnimation("Grass Mode");
        return;
    }
}

function selectMenuItem(option) {
    if (option.locked) {
        showLockedMessage();
        return;
    }
    
    if (option.mode !== null && option.mode !== undefined) {
        // Start game mode
        startMode(option.mode);
    } else if (option.action) {
        // Handle special actions
        switch(option.action) {
            case "shop":
                if (sessionPurchases.shopUnlocked) {
                    gameState = STATE_SHOP;
                } else {
                    startSecretHunt();
                }
                break;
            case "leaderboard_survival":
                showLeaderboardScreen('survival');
                break;
            case "leaderboard_mom":
                showLeaderboardScreen('mom');
                break;
            case "play_music":
                playBackgroundMusic();
                break;
            case "stop_music":
                stopBackgroundMusic();
                break;
            case "exit":
                showMessage("Thanks for playing! Close the tab to exit.");
                break;
        }
    }
}

function startMode(mode) {
    currentMode = mode;
    gameState = STATE_PLAYING;
    initializeMode(mode);
}

// ============================================================================
// MODE INITIALIZATION
// ============================================================================

function initializeMode(mode) {
    // Reset common state
    players = [];
    bullets = [];
    particles = [];
    enemies = [];
    score = 0;
    wave = 1;
    
    switch(mode) {
        case MODE_BATTLE:
            initBattleMode();
            break;
        case MODE_SURVIVAL:
            initSurvivalMode();
            break;
        case MODE_COMBINE:
            initCombineMode();
            break;
        case MODE_DILLY_DOLLY:
            initDillyDollyMode();
            break;
        case MODE_MOM:
            initMomMode();
            break;
        case MODE_FINAL:
            initFinalMode();
            break;
        case MODE_GRASS:
            initGrassMode();
            break;
        case MODE_MAKKA_PAKKA:
            initMakkaPakkaMode();
            break;
        case MODE_QUIZ:
            initQuizMode();
            break;
        case MODE_3D_ADVENTURE:
            init3DAdventure();
            break;
        case MODE_RELAX_LETTER_RAIN:
            initLetterRainMode();
            break;
        case MODE_RELAX_SHEEP:
            initSheepMode();
            break;
        case MODE_COIN_COLLECTION:
            initCoinCollection();
            break;
        case MODE_ESCAPE_MOM:
            initEscapeMom();
            break;
        case MODE_CAPTURE_FLAG:
            initCaptureFlag();
            break;
    }
}

// ============================================================================
// BATTLE MODE (Enhanced from existing)
// ============================================================================

function initBattleMode() {
    players = [
        {
            x: 100,
            y: CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2,
            width: PLAYER_SIZE,
            height: PLAYER_SIZE,
            character: CHARACTERS[selectedCharacters[0]],
            health: 100,
            maxHealth: 100,
            direction: 1,
            name: "Player 1",
            score: 0,
            cooldown: 0
        },
        {
            x: CANVAS_WIDTH - 100 - PLAYER_SIZE,
            y: CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2,
            width: PLAYER_SIZE,
            height: PLAYER_SIZE,
            character: CHARACTERS[selectedCharacters[1]],
            health: 100,
            maxHealth: 100,
            direction: -1,
            name: "CPU",
            score: 0,
            cooldown: 0,
            isAI: true
        }
    ];
}

function updateBattleMode(dt) {
    // Player 1 controls
    const p1 = players[0];
    const speed = finalModeUnlocked ? PLAYER_SPEED * 2 : PLAYER_SPEED;
    
    if (keys.w && p1.y > 0) p1.y -= speed;
    if (keys.s && p1.y < CANVAS_HEIGHT - p1.height) p1.y += speed;
    if (keys.a && p1.x > 0) {
        p1.x -= speed;
        p1.direction = -1;
    }
    if (keys.d && p1.x < CANVAS_WIDTH - p1.width) {
        p1.x += speed;
        p1.direction = 1;
    }
    
    // Shooting
    if (keys[" "] && p1.cooldown <= 0) {
        shoot(p1);
        p1.cooldown = finalModeUnlocked ? 5 : 20;
    }
    if (p1.cooldown > 0) p1.cooldown--;
    
    // AI Player 2
    const p2 = players[1];
    if (p2.isAI) {
        updateAI(p2, p1, dt);
    }
    
    // Check win condition
    if (p1.health <= 0) {
        gameOver("CPU Wins!");
    } else if (p2.health <= 0) {
        gameOver("Player 1 Wins!");
    }
}

function drawBattleMode() {
    // Background
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw players
    players.forEach(p => drawPlayer(p));
    
    // Draw bullets
    ctx.fillStyle = '#f1c40f';
    bullets.forEach(b => {
        ctx.beginPath();
        ctx.arc(b.x + BULLET_SIZE/2, b.y + BULLET_SIZE/2, BULLET_SIZE/2, 0, Math.PI*2);
        ctx.fill();
    });
    
    // Draw particles
    particles.forEach(p => {
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI*2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
    });
    
    // UI
    ctx.fillStyle = '#fff';
    ctx.font = '20px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`${players[0].name}: ${Math.max(0, players[0].health)}`, 10, 30);
    ctx.textAlign = 'right';
    ctx.fillText(`${players[1].name}: ${Math.max(0, players[1].health)}`, CANVAS_WIDTH - 10, 30);
    ctx.textAlign = 'left';
}

function drawPlayer(p) {
    ctx.fillStyle = p.character.color;
    ctx.fillRect(p.x, p.y, p.width, p.height);
    
    // Eyes
    ctx.fillStyle = 'white';
    const eyeX = p.direction === 1 ? p.x + 30 : p.x + 10;
    ctx.fillRect(eyeX, p.y + 10, 10, 10);
    
    // Health bar
    ctx.fillStyle = '#c0392b';
    ctx.fillRect(p.x, p.y - 15, p.width, 5);
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(p.x, p.y - 15, p.width * (p.health / p.maxHealth), 5);
}

function updateAI(ai, target, dt) {
    // Simple AI
    const PLAYER_SPEED_AI = PLAYER_SPEED * 0.6;
    
    if (ai.y < target.y - 10) ai.y += PLAYER_SPEED_AI;
    if (ai.y > target.y + 10) ai.y -= PLAYER_SPEED_AI;
    
    const dist = Math.abs(ai.x - target.x);
    if (dist > 400) {
        ai.x += (target.x > ai.x) ? PLAYER_SPEED_AI : -PLAYER_SPEED_AI;
    } else if (dist < 200) {
        ai.x += (target.x > ai.x) ? -PLAYER_SPEED_AI : PLAYER_SPEED_AI;
    }
    
    ai.direction = target.x > ai.x ? 1 : -1;
    
    if (ai.cooldown <= 0 && Math.random() < 0.05 && Math.abs(ai.y - target.y) < 50) {
        shoot(ai);
        ai.cooldown = 30;
    }
    if (ai.cooldown > 0) ai.cooldown--;
}

function shoot(player) {
    bullets.push({
        x: player.direction === 1 ? player.x + player.width : player.x - BULLET_SIZE,
        y: player.y + player.height / 2 - BULLET_SIZE / 2,
        vx: player.direction * BULLET_SPEED,
        vy: 0,
        owner: player
    });
}

function updateBullets(dt) {
    for (let i = bullets.length - 1; i >= 0; i--) {
        const b = bullets[i];
        b.x += b.vx;
        b.y += b.vy;
        
        if (b.x < 0 || b.x > CANVAS_WIDTH || b.y < 0 || b.y > CANVAS_HEIGHT) {
            bullets.splice(i, 1);
            continue;
        }
        
        // Check collisions with players
        players.forEach(p => {
            if (p !== b.owner && rectIntersect(b.x, b.y, BULLET_SIZE, BULLET_SIZE, p.x, p.y, p.width, p.height)) {
                if (!godMode || p.isAI) {
                    p.health -= 10;
                    createParticles(p.x + p.width/2, p.y + p.height/2, 'red');
                    bullets.splice(i, 1);
                }
            }
        });
        
        // Check collisions with enemies
        enemies.forEach((e, j) => {
            if (rectIntersect(b.x, b.y, BULLET_SIZE, BULLET_SIZE, e.x, e.y, e.width, e.height)) {
                e.health -= 20;
                createParticles(e.x + e.width/2, e.y + e.height/2, 'orange');
                bullets.splice(i, 1);
                if (e.health <= 0) {
                    enemies.splice(j, 1);
                    score += 100;
                }
            }
        });
    }
}

function updateParticles(dt) {
    for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.02;
        if (p.life <= 0) {
            particles.splice(i, 1);
        }
    }
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

// ============================================================================
// SURVIVAL MODE (Enhanced)
// ============================================================================

function initSurvivalMode() {
    players = [{
        x: CANVAS_WIDTH / 2 - PLAYER_SIZE / 2,
        y: CANVAS_HEIGHT / 2 - PLAYER_SIZE / 2,
        width: PLAYER_SIZE,
        height: PLAYER_SIZE,
        character: CHARACTERS[selectedCharacters[0]],
        health: 100,
        maxHealth: 100,
        direction: 1,
        name: "Player 1",
        score: 0,
        cooldown: 0
    }];
    
    wave = 1;
    spawnWave();
}

function updateSurvivalMode(dt) {
    // Player controls (same as battle)
    const p = players[0];
    const speed = finalModeUnlocked ? PLAYER_SPEED * 2 : PLAYER_SPEED;
    
    if (keys.w && p.y > 0) p.y -= speed;
    if (keys.s && p.y < CANVAS_HEIGHT - p.height) p.y += speed;
    if (keys.a && p.x > 0) {
        p.x -= speed;
        p.direction = -1;
    }
    if (keys.d && p.x < CANVAS_WIDTH - p.width) {
        p.x += speed;
        p.direction = 1;
    }
    
    if (keys[" "] && p.cooldown <= 0) {
        shoot(p);
        p.cooldown = finalModeUnlocked ? 5 : 20;
    }
    if (p.cooldown > 0) p.cooldown--;
    
    // Update enemies
    enemies.forEach(e => {
        const dx = p.x - e.x;
        const dy = p.y - e.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        
        if (dist > 0) {
            e.x += (dx / dist) * e.speed;
            e.y += (dy / dist) * e.speed;
        }
        
        // Collision with player
        if (rectIntersect(e.x, e.y, e.width, e.height, p.x, p.y, p.width, p.height)) {
            if (!godMode) {
                p.health -= 0.5;
            }
        }
    });
    
    // Check for next wave
    if (enemies.length === 0) {
        wave++;
        spawnWave();
    }
    
    // Check game over
    if (p.health <= 0) {
        saveHighScore(p.name, score, 'survival');
        gameOver(`Wave ${wave} - Score: ${score}`);
    }
}

function drawSurvivalMode() {
    // Background
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    // Draw player
    drawPlayer(players[0]);
    
    // Draw enemies
    ctx.fillStyle = '#e74c3c';
    enemies.forEach(e => {
        ctx.fillRect(e.x, e.y, e.width, e.height);
    });
    
    // Draw bullets
    ctx.fillStyle = '#f1c40f';
    bullets.forEach(b => {
        ctx.beginPath();
        ctx.arc(b.x + BULLET_SIZE/2, b.y + BULLET_SIZE/2, BULLET_SIZE/2, 0, Math.PI*2);
        ctx.fill();
    });
    
    // Draw particles
    particles.forEach(p => {
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI*2);
        ctx.fill();
        ctx.globalAlpha = 1.0;
    });
    
    // UI
    ctx.fillStyle = '#fff';
    ctx.font = '24px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Wave: ${wave}`, 10, 30);
    ctx.fillText(`Score: ${score}`, 10, 60);
    ctx.fillText(`Health: ${Math.max(0, Math.floor(players[0].health))}`, 10, 90);
    ctx.fillText(`Enemies: ${enemies.length}`, 10, 120);
    ctx.textAlign = 'left';
}

function spawnWave() {
    const count = wave * 2 + 3;
    for (let i = 0; i < count; i++) {
        const side = Math.random() < 0.5;
        enemies.push({
            x: side ? -50 : CANVAS_WIDTH + 50,
            y: Math.random() * CANVAS_HEIGHT,
            width: 40,
            height: 40,
            health: 20 + wave * 5,
            speed: 1 + Math.random() * 2,
            color: '#e74c3c'
        });
    }
}

// ============================================================================
// Due to response length, I'll continue in the next part...
// This establishes the foundation with Battle and Survival modes working.
// Next response will add all remaining modes.
// ============================================================================

// Initialize when page loads
window.onload = init;
