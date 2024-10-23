// game/players.js - Player management
import { GAME_CONFIG } from './config.js';

export class Players {
    constructor() {
        const centerZ = GAME_CONFIG.lineLength == GAME_CONFIG.platformLength ? 0 
            : Math.floor((GAME_CONFIG.platformLength - GAME_CONFIG.lineLength) / 2);
        
        this.player1Positions = Array(GAME_CONFIG.lineLength).fill()
            .map((_, index) => ({ x: 0, z: centerZ + index }));
        
        this.player2Positions = Array(GAME_CONFIG.lineLength).fill()
            .map((_, index) => ({ x: GAME_CONFIG.platformWidth - 1, z: centerZ + index }));
        
        this.player1Score = 0;
        this.player2Score = 0;
        this.player1HitCounter = 0;
        this.player2HitCounter = 0;
    }

    updatePositions(pressedKeys) {
        const movePlayer = (positions, direction) => {
            const newPositions = positions.map(pos => ({
                x: pos.x,
                z: pos.z + direction * GAME_CONFIG.moveSpeed
            }));

            if (newPositions.every(pos => pos.z >= 0 && pos.z < GAME_CONFIG.platformLength)) {
                return newPositions;
            }
            return positions;
        };

        // Player 1 movement
        if (pressedKeys['w'] || pressedKeys['a']) {
            this.player1Positions = movePlayer(this.player1Positions, -1);
        }
        if (pressedKeys['s'] || pressedKeys['d']) {
            this.player1Positions = movePlayer(this.player1Positions, 1);
        }

        // Player 2 movement
        if (pressedKeys['ArrowUp'] || pressedKeys['ArrowRight']) {
            this.player2Positions = movePlayer(this.player2Positions, -1);
        }
        if (pressedKeys['ArrowDown'] || pressedKeys['ArrowLeft']) {
            this.player2Positions = movePlayer(this.player2Positions, 1);
        }
    }

    updateScore(scoringPlayer) {
        if (scoringPlayer === 1) {
            this.player1Score++;
        } else {
            this.player2Score++;
        }
    }

    resetHitCounters() {
        this.player1HitCounter = 0;
        this.player2HitCounter = 0;
    }

    getPaddleMiddle(player) {
        const positions = player === 1 ? this.player1Positions : this.player2Positions;
        return positions[Math.floor(GAME_CONFIG.lineLength / 2)].z;
    }
}
