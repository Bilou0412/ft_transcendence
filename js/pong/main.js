///////////////////////////////////////imports////////////////////////////////////////
import { initBall } from "./ball_init.js";
import { resetBall, sleep } from "./resetBall.js";
import { initMiddlePlatform, initSides } from "./roundedBox.js";
import { updateCubeSelection, updatePlayerPositions } from "./movements.js";
import { updateBallPosition } from "./ball_physics.js";
import { updateScoreDisplay, updateClock, initScoreboard, initClock} from "./display.js";
import { focusGame, initMonitor, focusMonitor, initTable} from "./monitor.js";
import { onKeyDown, onKeyUp, onMouseWheel } from "./keyEvents.js";
import { Settings } from "./settings.js";
import { titleDisplay } from "./monitor_display.js";

// ///////////////////////////////////environment settings///////////////////////////////
export let settings = null;
let started = false;

///////////////////////////////////main functions/////////////////////////////////////
export async function quitPong() {
    if (settings) {
        focusMonitor();
        await sleep(2000);
        settings.destroy();
        settings = null;
    }
    
    document.getElementById('nav').style.display = 'block';
    document.getElementById('Taskbar').style.display = 'block';

    //stop event listeners
    window.removeEventListener('keydown', onKeyDown, false);
    window.removeEventListener('keyup', onKeyUp, false);
    window.removeEventListener('wheel', onMouseWheel, false);
    //stop animation loop
    window.cancelAnimationFrame(animate);
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

function resetGame() {
    if (!settings) 
        return;
    settings.player1Score = 0;
    settings.player2Score = 0;
    updateScoreDisplay();
    resetBall();

}

export async function startGame() {
    if (!settings) return;
    settings.gameStatus = 'playing';
    initSides();
    initMiddlePlatform();
    initBall();
    initScoreboard();
    initClock();
    updateClock();
    resetGame();
}

function progressLoading() {
    //create a progress bar and puttin it in the middle of the screen
    const progressBar = document.createElement('progress');
    progressBar.value = 0;
    progressBar.style.position = 'absolute';
    progressBar.style.left = '50%';
    progressBar.style.top = '55%';
    progressBar.style.transform = 'translate(-50%, -50%)';
    progressBar.style.zIndex = '1000';
    document.body.appendChild(progressBar);

    //loading progress over 5 seconds
    let progress = 0;
    const interval = setInterval(() => {
        progress += 0.1;
        progressBar.value = progress;
        if (progress >= 100) {
            clearInterval(interval);
            progressBar.remove();
        }
    }, 500);

    //remove the progress bar after 5 seconds
    setTimeout(() => {
        progressBar.remove();
    }, 5000);
}

export async function initializeGame() {
    
    progressLoading();
    window.addEventListener('keydown', onKeyDown, false);
    window.addEventListener('keyup', onKeyUp, false);
    window.addEventListener('wheel', onMouseWheel, false);
    settings = new Settings();
    console.log('settings');
    initMonitor();
    initTable();
    titleDisplay();
    await sleep(5000);
    settings.updateTime();
    animate();
    startGame();
    document.getElementById('nav').style.display = 'none';
    document.getElementById('startButton').style.display = 'none';
    document.getElementById('Taskbar').style.display = 'none';
    focusGame();

}