///////////////////////////////////////imports////////////////////////////////////////
import { initBall } from "./ball_init.js";
import { resetBall, sleep } from "./resetBall.js";
import { initMiddlePlatform, initSides } from "./roundedBox.js";
import { updateCubeSelection, updatePlayerPositions } from "./movements.js";
import { updateBallPosition } from "./ball_physics.js";
import { updateScoreDisplay, updateClock, initScoreboard, initClock} from "./display.js";
import { focusGame, initMonitor, focusMonitor} from "./monitor.js";
import { onKeyDown, onKeyUp, onMouseWheel } from "./keyEvents.js";
import { Settings } from "./settings.js";
import { titleDisplay } from "./monitor_display.js";
import { route } from "./router.js";

// ///////////////////////////////////environment settings///////////////////////////////
export let settings = new Settings();

///////////////////////////////////main functions/////////////////////////////////////
export async function quitPong() {
    settings.updateGameStatus('paused');
    focusMonitor();
    await sleep(2000);
    settings.destroy();
    document.getElementById('root').style.display = 'block';
    route(null, '/');

    //stop event listeners
    window.removeEventListener('keydown', onKeyDown, false);
    window.removeEventListener('keyup', onKeyUp, false);
    window.removeEventListener('wheel', onMouseWheel, false);
    //stop animation loop
    window.cancelAnimationFrame(animate);

    settings = null;
}


// Animation loop
function animate() {
    if (settings)
    {
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
}

window.addEventListener('keydown', onKeyDown, false);
window.addEventListener('keyup', onKeyUp, false);
window.addEventListener('wheel', onMouseWheel, false);

function resetGame() {
    if (!settings) 
        return;
    settings.player1Score = 0;
    settings.player2Score = 0;
    updateScoreDisplay();
    resetBall();
}

export async function startGame() {
    settings.gameStatus = 'playing';
    initSides();
    initMiddlePlatform();
    initBall();
    initScoreboard();
    initClock();
    updateClock();
    await sleep(10000);
    resetGame();

}

if (settings) {
    await sleep(2000);
    document.getElementById('root').style.display = 'none';
    initMonitor();
    titleDisplay();
    animate();
    focusGame();
    startGame();
}

