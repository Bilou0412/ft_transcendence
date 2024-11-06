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
    buttonCanvas.width = 300;
    buttonCanvas.height = 200;
    const buttonCtx = buttonCanvas.getContext('2d');

    ///////////////////////////////////Content design//////////////////////////////////////
    buttonCtx.fillStyle = '#0aa23b'; // Text color
    // buttonCtx.font = '50px "Digital-7"'; // Text font
    buttonCtx.font = '50px Courier New';
    buttonCtx.textAlign = 'center';
    buttonCtx.textBaseline = 'middle';
    buttonCtx.fillText('Start Game', buttonCanvas.width / 2, buttonCanvas.height / 2);

    const buttonTexture = new THREE.CanvasTexture(buttonCanvas);
    const buttonMaterial = new THREE.MeshBasicMaterial({ map: buttonTexture, transparent: true });
    const buttonPlane = new THREE.PlaneGeometry(1, 0.5); // Size of the button plane
    buttonMesh = new THREE.Mesh(buttonPlane, buttonMaterial);
    // Position the button in the scene
    buttonMesh.position.set(-0.25, 2.55, settings.platformLength / 2 + 6.11); // Adjust based on your scene's setup
    settings.scene.add(buttonMesh);


    ///////////////////////////////////Mouse click detection//////////////////////////////////////
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

	async function onButtonClick(event) {
        // Convert mouse position to normalized device coordinates
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        // Update raycaster with camera and mouse position
        raycaster.setFromCamera(mouse, settings.camera);

        // Check for intersections with the button
        const intersects = raycaster.intersectObject(buttonMesh);
        if (intersects.length > 0 && settings.gameStatus === 'title') {
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

/////////////////////////////////////Gear Button///////////////////////////////////////
let gearMesh = null;
export function initGearButton() {
	/////////////////////////////////Button design//////////////////////////////////////
	const gearTexture = new THREE.TextureLoader().load('texture/gear.png');
	const gearMaterial = new THREE.MeshBasicMaterial({ map: gearTexture });
	const gearPlane = new THREE.PlaneGeometry(2, 1);
	gearMesh = new THREE.Mesh(gearPlane, gearMaterial);
	gearMesh.scale.set(0.2, 0.3, 0.2);
	gearMesh.position.set(1, 3.5, settings.platformLength / 2 + 6.1);
	settings.scene.add(gearMesh);

    ///////////////////////////////////Mouse click detection//////////////////////////////////////
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

	async function onButtonClick(event) {
			// Convert mouse position to normalized device coordinates
			mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
			mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

			// Update raycaster with camera and mouse position
			raycaster.setFromCamera(mouse, settings.camera);

			// Check for intersections with the button
			const intersects = raycaster.intersectObject(gearMesh);
			if (intersects.length > 0 && settings.gameStatus === 'paused') {
				settingDisplay();
			}
		}

    // Event listener for mouse click
    window.addEventListener('click', onButtonClick, false);
}

export function settingDisplay() {
    clearDisplay();
    ///////////////////////////////////Button Content//////////////////////////////////////
    const settingCanvas = document.createElement('canvas');
    settingCanvas.width = 500;
    settingCanvas.height = 300;
    const settingCtx = settingCanvas.getContext('2d');

    ///////////////////////////////////Content design//////////////////////////////////////
    settingCtx.fillStyle = '#0aa23b'; // Text color
    // settingCtx.font = '50px "Digital-7"'; // Text font
    settingCtx.font = '100px Courier New';
    settingCtx.textAlign = 'center';
    settingCtx.textBaseline = 'middle';
    settingCtx.fillText('Settings', settingCanvas.width / 2, settingCanvas.height / 2);

    const settingTexture = new THREE.CanvasTexture(settingCanvas);
    const settingMaterial = new THREE.MeshBasicMaterial({ map: settingTexture, transparent: true });
    const settingPlane = new THREE.PlaneGeometry(1, 0.5); // Size of the setting plane
    const settingMesh = new THREE.Mesh(settingPlane, settingMaterial);
    // Position the setting in the scene
    settingMesh.position.set(-0.25, 2.55, settings.platformLength / 2 + 6.11); // Adjust based on your scene's setup
    settings.scene.add(settingMesh);
}

/////////////////////////////////////Display Functions///////////////////////////////////////
export function clearDisplay() {
    if (buttonBackgroundMesh) {
        settings.scene.remove(buttonBackgroundMesh);
    }
    if (buttonMesh) {
        settings.scene.remove(buttonMesh);
    }
    if (gearMesh) {
        settings.scene.remove(gearMesh);
    }
}

export function titleDisplay() {
    initStartButton();
    initGearButton();
}

export function pauseDisplay() {
    initGearButton();
}