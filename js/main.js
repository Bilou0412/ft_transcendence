///////////////////////////////////////imports////////////////////////////////////////
import { initBall } from "./ball_init.js";
import { resetBall } from "./resetBall.js";
import { initMiddlePlatform, initSides } from "./roundedBox.js";
import { updateCubeSelection, updatePlayerPositions } from "./movements.js";
import { updateBallPosition } from "./ball_physics.js";
import { updateScoreDisplay, updateClock, initScoreboard, initClock} from "./display.js";
import { initMonitor} from "./monitor.js";
import { onKeyDown, onKeyUp, onMouseWheel } from "./keyEvents.js";
import { Settings } from "./settings.js";
import { titleDisplay } from "./monitor_display.js";

// ///////////////////////////////////environment settings///////////////////////////////
export const settings = new Settings();

///////////////////////////////////main functions/////////////////////////////////////
// Animation loop
function animate() {
    requestAnimationFrame(animate);

    updatePlayerPositions();
    updateCubeSelection();
    updateBallPosition();

    // Raise/lower cubes animation
    settings.cubes.forEach(cube => {
        if (cube.userData.targetY !== undefined) {
            cube.position.y += (cube.userData.targetY - cube.position.y) * settings.liftSpeed;
        }
    });

    settings.renderer.render(settings.scene, settings.camera);
}

window.addEventListener('keydown', onKeyDown, false);
window.addEventListener('keyup', onKeyUp, false);
window.addEventListener('wheel', onMouseWheel, false);

function resetGame() {
    settings.player1Score = 0;
    settings.player2Score = 0;
    updateScoreDisplay();
    resetBall();
}

export function startGame() {
    settings.gameStatus = 'playing';
    initSides();
    initMiddlePlatform();
    initBall();
    initScoreboard();
    initClock();
    updateClock();
    resetGame();

}

// document.getElementById('startButton').addEventListener('click', function() {
//     // Cacher l'écran titre
//     document.getElementById('titleScreen').style.display = 'none';
//     // Lancer le jeu
//     startGame();
// });
initMonitor();
titleDisplay();
animate();
// startGame();