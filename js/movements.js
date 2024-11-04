///////////////////////////////////////imports////////////////////////////////////////
import { settings } from './main.js';
import { ball } from './ball_init.js';

// Object to track pressed keys
export const pressedKeys = {};

/////////////////////////////////////////cubes////////////////////////////////////////
export function updateCubeSelection() {
    settings.cubes.forEach(cube => {
        cube.material.color.setHex(0x00ffff);
        cube.userData.targetY = 0;
    });

    const updatePlayerCubes = (positions, player) => {
        const color = ball.userData.heldBy === player ? 0xff0000 : 0xffffff;
        positions.forEach((pos) => {
            const cube = settings.cubes.find(cube =>
                cube.userData.gridPosition.x === Math.floor(pos.x) &&
                cube.userData.gridPosition.z === Math.floor(pos.z)
            );
            if (cube) {
                cube.material.color.setHex(color);
                cube.userData.targetY = settings.targetHeight;
            }
        });
    };

    updatePlayerCubes(settings.player1Positions, 1);
    updatePlayerCubes(settings.player2Positions, 2);
}

////////////////////////////////////////paddles///////////////////////////////////////
export function updatePlayerPositions() {
    const movePlayer = (positions, direction) => {
        const newPositions = positions.map(pos => ({
            x: pos.x,
            z: pos.z + direction * settings.moveSpeed
        }));

        // Check if any cube in the line would go out of bounds
        if (newPositions.every(pos => pos.z >= 0 && pos.z < settings.platformLength)) {
            return newPositions;
        }
        return positions;
    };

    if (settings.gameStatus === 'paused') {
        return;
    }

    // Player 1 movement
    if (pressedKeys['w'] || pressedKeys['a']) {
		settings.updatePlayer1Positions(movePlayer(settings.player1Positions, -1));
    }
    if (pressedKeys['s'] || pressedKeys['d']) {
		settings.updatePlayer1Positions(movePlayer(settings.player1Positions, 1));
    }

    // Player 2 movement
    if (pressedKeys['ArrowUp'] || pressedKeys['ArrowRight']) {
		settings.updatePlayer2Positions(movePlayer(settings.player2Positions, -1));
    }
    if (pressedKeys['ArrowDown'] || pressedKeys['ArrowLeft']) {
		settings.updatePlayer2Positions(movePlayer(settings.player2Positions, 1));
    }
}

export function updatePaddleColor(player, color) 
{
    const positions = player === 1 ? settings.player1Positions : settings.player2Positions;
    positions.forEach((pos) => {
        const cube = settings.cubes.find(cube =>
            cube.userData.gridPosition.x === Math.floor(pos.x) &&
            cube.userData.gridPosition.z === Math.floor(pos.z)
        );
        if (cube) {
            cube.material.color.setHex(color);
        }
    });
}