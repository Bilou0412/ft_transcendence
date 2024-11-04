import { settings, startGame } from "./main.js";
import { sleep } from "./resetBall.js";
import { focusGame } from "./monitor.js";

/////////////////////////////////////Start Button///////////////////////////////////////
export function initButton() {
	/////////////////////////////////Button design//////////////////////////////////////
	const buttonBackgroundTexture = new THREE.TextureLoader().load('texture/green_pixel_black.png');
	const buttonBackgroundMaterial = new THREE.MeshBasicMaterial({ map: buttonBackgroundTexture });
	const buttonBackgroundPlane = new THREE.PlaneGeometry(2, 1);
	const buttonBackgroundMesh = new THREE.Mesh(buttonBackgroundPlane, buttonBackgroundMaterial);
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
    buttonCtx.font = '50px "Digital-7"'; // Text font
    buttonCtx.font = '50px Courier New';
    buttonCtx.textAlign = 'center';
    buttonCtx.textBaseline = 'middle';
    buttonCtx.fillText('Start Game', buttonCanvas.width / 2, buttonCanvas.height / 2);

    const buttonTexture = new THREE.CanvasTexture(buttonCanvas);
    const buttonMaterial = new THREE.MeshBasicMaterial({ map: buttonTexture, transparent: true });
    const buttonPlane = new THREE.PlaneGeometry(1, 0.5); // Size of the button plane
    const buttonMesh = new THREE.Mesh(buttonPlane, buttonMaterial);
    // Position the button in the scene
    buttonMesh.position.set(-0.25, 2.55, settings.platformLength / 2 + 6.11); // Adjust based on your scene's setup
    settings.scene.add(buttonMesh);


    ///////////////////////////////////Mouse click detection//////////////////////////////////////
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
0
	async function onButtonClick(event) {
			// Convert mouse position to normalized device coordinates
			mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
			mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

			// Update raycaster with camera and mouse position
			raycaster.setFromCamera(mouse, settings.camera);

			// Check for intersections with the button
			const intersects = raycaster.intersectObject(buttonMesh);
			if (intersects.length > 0 && settings.gameStatus === 'paused') {
				// settings.scene.remove(buttonMesh);
				startGame();
				focusGame();
				await sleep(2000);
			}
		}

    // Add event listener for mouse click
    window.addEventListener('click', onButtonClick, false);
}