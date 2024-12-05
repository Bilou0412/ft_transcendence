import { settings, startGame } from "./main.js";
import { sleep } from "./resetBall.js";
import { focusGame } from "./monitor.js";

/////////////////////////////////////Start Button///////////////////////////////////////
let buttonBackgroundMesh = null;
let buttonMesh = null;
export function initStartButton() {
	/////////////////////////////////Button design//////////////////////////////////////
	const buttonBackgroundTexture = new THREE.TextureLoader().load('texture/green_pixel_black.png');
	const buttonBackgroundMaterial = new THREE.MeshBasicMaterial({ map: buttonBackgroundTexture });
	const buttonBackgroundPlane = new THREE.PlaneGeometry(2, 1);
	buttonBackgroundMesh = new THREE.Mesh(buttonBackgroundPlane, buttonBackgroundMaterial);
	// buttonBackgroundMesh.scale.set(2, 3, 3);
	buttonBackgroundMesh.position.set(-0.25, 2.5, settings.platformLength / 2 + 6.1);
	settings.scene.add(buttonBackgroundMesh);

    ///////////////////////////////////Button Content//////////////////////////////////////
    const buttonCanvas = document.createElement('canvas');
    buttonCanvas.width = 600;
    buttonCanvas.height = 300;
    const buttonCtx = buttonCanvas.getContext('2d');

    ///////////////////////////////////Content design//////////////////////////////////////
    buttonCtx.fillStyle = '#0aa23b'; // Text color
    // buttonCtx.font = '50px "Digital-7"'; // Text font
    buttonCtx.font = '100px Courier New';
    buttonCtx.textAlign = 'center';
    buttonCtx.textBaseline = 'middle';
    buttonCtx.fillText('Start Game', buttonCanvas.width / 2, buttonCanvas.height / 2);

    const buttonTexture = new THREE.CanvasTexture(buttonCanvas);
    const buttonMaterial = new THREE.MeshBasicMaterial({ map: buttonTexture, transparent: true });
    const buttonPlane = new THREE.PlaneGeometry(1, 0.5); // Size of the button plane
    buttonMesh = new THREE.Mesh(buttonPlane, buttonMaterial);
    // Position the button in the scene
    buttonMesh.position.set(-0.25, 2.53, settings.platformLength / 2 + 6.11); // Adjust based on your scene's setup
    settings.scene.add(buttonMesh);


    ///////////////////////////////////Mouse click detection//////////////////////////////////////
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

	async function onButtonClick(event) {
        // Convert mouse position to normalized device coordinates
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        if (!settings)
            return;
        // Update raycaster with camera and mouse position
        raycaster.setFromCamera(mouse, settings.camera);

        // Check for intersections with the button
        const intersects = raycaster.intersectObject(buttonBackgroundMesh);
        if (intersects.length > 0 && settings.gameStatus === 'title' && settings.displayStatus == 'start') {
            startGame();
            focusGame();
            await sleep(2000);
            clearDisplay();
            pauseDisplay();
        }
    }

    // Event listener for mouse click
    window.addEventListener('click', onButtonClick, false);
}

function initScreenBackground() {
    const ScreenBackgroundTexture = new THREE.TextureLoader().load('../../texture/pong_screen.png');
	const ScreenBackgroundMaterial = new THREE.MeshBasicMaterial({ map: ScreenBackgroundTexture });
	const ScreenBackgroundPlane = new THREE.PlaneGeometry(2, 0.975);
	const ScreenBackgroundMesh = new THREE.Mesh(ScreenBackgroundPlane, ScreenBackgroundMaterial);
    ScreenBackgroundMesh.scale.set(2.53, 2.53, 2.53);
	ScreenBackgroundMesh.position.set(-0.03, 2.72, settings.platformLength / 2 + 6.1);
	settings.scene.add(ScreenBackgroundMesh);
}

export function titleDisplay() {
    initScreenBackground();
}

export function pauseDisplay() {
}