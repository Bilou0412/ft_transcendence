// game/main.js - Main game orchestration
import { SceneManager } from './scene.js';
import { Platform } from './platform.js';
import { Ball } from './ball.js';
import { Players } from './players.js';
import { InputHandler } from './input.js';

export class Game {
    constructor() {
        this.sceneManager = new SceneManager();
        this.platform = new Platform(this.sceneManager.scene);
        this.ball = new Ball(this.sceneManager.scene);
        this.players = new Players();
        this.input = new InputHandler(this);
        this.isRunning = false;

        // Add window resize handler
        window.addEventListener('resize', () => {
            this.sceneManager.handleResize();
        });

        // Create UI elements if they don't exist
        this.createUIElements();
    }

    createUIElements() {
        if (!document.getElementById('scoreDisplay')) {
            const scoreDisplay = document.createElement('div');
            scoreDisplay.id = 'scoreDisplay';
            scoreDisplay.style.position = 'absolute';
            scoreDisplay.style.top = '20px';
            scoreDisplay.style.left = '50%';
            scoreDisplay.style.transform = 'translateX(-50%)';
            scoreDisplay.style.color = 'white';
            scoreDisplay.style.fontSize = '24px';
            document.body.appendChild(scoreDisplay);
        }

        if (!document.getElementById('hitCounter1Display')) {
            const hitCounter1 = document.createElement('div');
            hitCounter1.id = 'hitCounter1Display';
            hitCounter1.style.position = 'absolute';
            hitCounter1.style.top = '20px';
            hitCounter1.style.left = '20px';
            hitCounter1.style.color = 'white';
            document.body.appendChild(hitCounter1);
        }

        if (!document.getElementById('hitCounter2Display')) {
            const hitCounter2 = document.createElement('div');
            hitCounter2.id = 'hitCounter2Display';
            hitCounter2.style.position = 'absolute';
            hitCounter2.style.top = '20px';
            hitCounter2.style.right = '20px';
            hitCounter2.style.color = 'white';
            document.body.appendChild(hitCounter2);
        }
    }

    start() {
        console.log('Game starting...'); // Debug log
        this.isRunning = true;
        this.reset();
        this.animate();
    }

    animate() {
        if (!this.isRunning) return;
        
        requestAnimationFrame(() => this.animate());
        this.update();
        this.sceneManager.render();
    }

    update() {
        this.updatePlayerPositions();
        this.updateCubeSelection();
        this.updateBallPosition();
        this.platform.update();
        this.updateDisplays();
    }

    updatePlayerPositions() {
        this.players.updatePositions(this.input.pressedKeys);
    }

    updateCubeSelection() {
        this.platform.cubes.forEach(cube => {
            cube.material.color.setHex(0x00ffff);
            cube.userData.targetY = 0;
        });

        this.updatePlayerCubes(this.players.player1Positions, 1);
        this.updatePlayerCubes(this.players.player2Positions, 2);
    }

    updatePlayerCubes(positions, player) {
        const color = this.ball.ball.userData.heldBy === player ? 0xff0000 : 0xffffff;
        positions.forEach((pos) => {
            const cube = this.platform.cubes.find(cube =>
                cube.userData.gridPosition.x === Math.floor(pos.x) &&
                cube.userData.gridPosition.z === Math.floor(pos.z)
            );
            if (cube) {
                cube.material.color.setHex(color);
                cube.userData.targetY = GAME_CONFIG.targetHeight;
            }
        });
    }

    updateBallPosition() {
        this.ball.updatePosition(this.players, this.platform);
    }

    updateDisplays() {
		// alert('updateDisplays 0');
        document.getElementById('scoreDisplay').textContent = 
            `${this.players.player1Score} | ${this.players.player2Score}`;
		// alert('updateDisplays 1');
        // document.getElementById('hitCounter1Display').textContent = 
        //     `${this.players.player1HitCounter} / ${GAME_CONFIG.superChargeCount}`;
		// // alert('updateDisplays 2');
        // document.getElementById('hitCounter2Display').textContent = 
        //     `${this.players.player2HitCounter} / ${GAME_CONFIG.superChargeCount}`;
		// alert('updateDisplays 3');
    }

    reset() {
        this.players.player1Score = 0;
        this.players.player2Score = 0;
        this.players.resetHitCounters();
        this.ball.reset(2);
        this.updateDisplays();
    }
}

// Initialize and start the game
export function startGame() {
    const titleScreen = document.getElementById('titleScreen');
    if (titleScreen) {
        titleScreen.style.display = 'none';
    }

    // Clear any existing game elements
    const oldCanvas = document.querySelector('canvas');
    if (oldCanvas) {
        oldCanvas.remove();
    }

    const game = new Game();
    game.start();
}

// Make sure THREE.js is loaded before starting
if (typeof THREE === 'undefined') {
    console.error('THREE is not defined! Make sure Three.js is loaded before starting the game.');
} else {
    // Add start button event listener if it exists
    const startButton = document.getElementById('startButton');
    if (startButton) {
        startButton.addEventListener('click', startGame);
    }
}