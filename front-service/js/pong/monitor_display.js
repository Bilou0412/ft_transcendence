import { settings, startGame } from "./main.js";
import { sleep } from "./resetBall.js";
import { focusGame } from "./monitor.js";
import { clearBall } from "./ball_init.js";
import { clearSides, clearMiddle } from "./roundedBox.js";
import { clearScoreboard } from "./display.js";
import { gameMode } from "./gameModes.js";

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

// /////////////////////////////////////Gear Button///////////////////////////////////////
// let gearMesh = null;
// export function initGearButton() {
// 	/////////////////////////////////Button design//////////////////////////////////////
// 	const gearTexture = new THREE.TextureLoader().load('texture/gear.png');
// 	const gearMaterial = new THREE.MeshBasicMaterial({ map: gearTexture });
// 	const gearPlane = new THREE.PlaneGeometry(2, 1);
// 	gearMesh = new THREE.Mesh(gearPlane, gearMaterial);
// 	gearMesh.scale.set(0.2, 0.3, 0.2);
// 	gearMesh.position.set(1, 3.5, settings.platformLength / 2 + 6.1);
// 	settings.scene.add(gearMesh);

//     ///////////////////////////////////Mouse click detection//////////////////////////////////////
//     const raycaster = new THREE.Raycaster();
//     const mouse = new THREE.Vector2();

// 	async function onButtonClick(event) {
// 			// Convert mouse position to normalized device coordinates
// 			mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
// 			mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

// 			// Update raycaster with camera and mouse position
// 			raycaster.setFromCamera(mouse, settings.camera);

// 			// Check for intersections with the button
// 			const intersects = raycaster.intersectObject(gearMesh);
// 			if (intersects.length > 0) {
// 				settingDisplay();
//                 settings.updateDisplayStatus('settings');
// 			}
// 		}

//     // Event listener for mouse click
//     window.addEventListener('click', onButtonClick, false);
// }

// let settingMesh = null;
// export function settingDisplay() {
//     clearDisplay();
//     initGearButton();
//     ///////////////////////////////////Button Content//////////////////////////////////////
//     const settingCanvas = document.createElement('canvas');
//     settingCanvas.width = 500;
//     settingCanvas.height = 300;
//     const settingCtx = settingCanvas.getContext('2d');

//     ///////////////////////////////////Content design//////////////////////////////////////
//     settingCtx.fillStyle = '#0aa23b'; // Text color
//     // settingCtx.font = '50px "Digital-7"'; // Text font
//     settingCtx.font = '100px Courier New';
//     settingCtx.textAlign = 'center';
//     settingCtx.textBaseline = 'middle';
//     settingCtx.fillText('Settings', settingCanvas.width / 2, settingCanvas.height / 2);

//     const settingTexture = new THREE.CanvasTexture(settingCanvas);
//     const settingMaterial = new THREE.MeshBasicMaterial({ map: settingTexture, transparent: true });
//     const settingPlane = new THREE.PlaneGeometry(1, 0.5); // Size of the setting plane
//     settingMesh = new THREE.Mesh(settingPlane, settingMaterial);
//     // Position the setting in the scene
//     // settingMesh.position.set(-0.25, 3.5, settings.platformLength / 2 + 6.11); // Adjust based on your scene's setup
//     settingMesh.position.set(-0.25, 3.5, 30 / 2 + 6.11); // Adjust based on your scene's setup
//     settings.scene.add(settingMesh);

//     gameModesDisplay();
// }

// /////////////////////////////////////Game Modes///////////////////////////////////////
// let raycaster;
// let mouse;

// let modeMesh1 = null;
// let modeMesh2 = null;
// let modeMesh3 = null;

// export function createButton(y, text, action) {
//     ///////////////////////////////////Button Content//////////////////////////////////////
//     const buttonCanvas = document.createElement('canvas');
//     buttonCanvas.width = 300;
//     buttonCanvas.height = 200;
//     const buttonCtx = buttonCanvas.getContext('2d');

//     ///////////////////////////////////Content design//////////////////////////////////////
//     buttonCtx.fillStyle = '#0aa23b'; // Text color
//     if (settings.gameMode === text) {
//         buttonCtx.font = 'bold 80px Courier New';
//     } else {
//         buttonCtx.font = '50px Courier New';
//     }
//     buttonCtx.textAlign = 'center';
//     buttonCtx.textBaseline = 'middle';
//     buttonCtx.fillText(text, buttonCanvas.width / 2, buttonCanvas.height / 2);

//     const buttonTexture = new THREE.CanvasTexture(buttonCanvas);
//     const buttonMaterial = new THREE.MeshBasicMaterial({ map: buttonTexture, transparent: true });
//     const buttonPlane = new THREE.PlaneGeometry(1, 0.5); // Size of the button plane

//     // Create the mesh and add it to the scene
//     const mesh = new THREE.Mesh(buttonPlane, buttonMaterial);
//     mesh.position.set(-0.25, y, 30 / 2 + 6.11); // Adjust based on your scene's setup
//     settings.scene.add(mesh);

//     // Add click event listener
//     mesh.addEventListener('click', () => {
//         if (settings.gameStatus === 'paused') {
//             action();
//         }
//     });

//     return mesh;
// }

// function onButtonClick(event) {
//     // Convert mouse position to normalized device coordinates
//     mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
//     mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

//     // Update raycaster with camera and mouse position
//     raycaster.setFromCamera(mouse, settings.camera);

//     // Check for intersections with any object in the scene
//     const intersects = raycaster.intersectObjects(settings.scene.children);
//     if (intersects.length > 0) {
//         intersects[0].object.dispatchEvent({ type: 'click' });
//     }
// }

// export function gameModesDisplay() {
//     raycaster = new THREE.Raycaster();
//     mouse = new THREE.Vector2();

//     window.addEventListener('click', onButtonClick, false);
//     clearModes();

//     modeMesh1 = createButton(2.8, '10x30', () => gameMode(10, 30, 3));
//     modeMesh2 = createButton(2.5, '30x50', () => gameMode(30, 50, 5));
//     modeMesh3 = createButton(2.2, '50x70', () => gameMode(50, 70, 10));
// }

// export function clearModes() {
//     if (modeMesh1) {
//         settings.scene.remove(modeMesh1);
//         modeMesh1 = null;
//     }
//     if (modeMesh2) {
//         settings.scene.remove(modeMesh2);
//         modeMesh2 = null;
//     }
//     if (modeMesh3) {
//         settings.scene.remove(modeMesh3);
//         modeMesh3 = null;
//     }
// }


// /////////////////////////////////////Auth///////////////////////////////////////
// /////////////////////////////////////profile Button///////////////////////////////////////
// let profileIconMesh = null;
export function initProfileButton() {
// 	/////////////////////////////////Button design//////////////////////////////////////
// 	const profileTexture = new THREE.TextureLoader().load('texture/profile.jpg');
// 	const profileMaterial = new THREE.MeshBasicMaterial({ map: profileTexture });
// 	const profilePlane = new THREE.PlaneGeometry(2, 1);
// 	profileIconMesh = new THREE.Mesh(profilePlane, profileMaterial);
// 	profileIconMesh.scale.set(0.2, 0.3, 0.2);
// 	profileIconMesh.position.set(-1.5, 3.5, settings.platformLength / 2 + 6.1);
// 	settings.scene.add(profileIconMesh);

//     ///////////////////////////////////Mouse click detection//////////////////////////////////////
//     const raycaster = new THREE.Raycaster();
//     const mouse = new THREE.Vector2();

// 	async function onButtonClick(event) {
// 			// Convert mouse position to normalized device coordinates
// 			mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
// 			mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

// 			// Update raycaster with camera and mouse position
// 			raycaster.setFromCamera(mouse, settings.camera);

// 			// Check for intersections with the button
// 			const intersects = raycaster.intersectObject(profileIconMesh);
// 			if (intersects.length > 0) {
// 				profileDisplay();
//                 settings.updateDisplayStatus('auth');
//                 console.log(settings.game)
// 			}
// 		}

//     // Event listener for mouse click
//     window.addEventListener('click', onButtonClick, false);
}

// let profileMesh = null;
// export function profileDisplay(){
//     clearDisplay();
//     initGearButton();
//     ///////////////////////////////////Button Content//////////////////////////////////////
//     const profileCanvas = document.createElement('canvas');
//     profileCanvas.width = 500;
//     profileCanvas.height = 300;
//     const profileCtx = profileCanvas.getContext('2d');

//     ///////////////////////////////////Content design//////////////////////////////////////
//     profileCtx.fillStyle = '#0aa23b'; // Text color
//     // profileCtx.font = '50px "Digital-7"'; // Text font
//     profileCtx.font = '100px Courier New';
//     profileCtx.textAlign = 'center';
//     profileCtx.textBaseline = 'middle';
//     profileCtx.fillText('Profile', profileCanvas.width / 2, profileCanvas.height / 2);

//     const profileTexture = new THREE.CanvasTexture(profileCanvas);
//     const profileMaterial = new THREE.MeshBasicMaterial({ map: profileTexture, transparent: true });
//     const profilePlane = new THREE.PlaneGeometry(1, 0.5); // Size of the profile plane
//     profileMesh = new THREE.Mesh(profilePlane, profileMaterial);
//     // Position the profile in the scene
//     // profileMesh.position.set(-0.25, 3.5, profiles.platformLength / 2 + 6.11); // Adjust based on your scene's setup
//     profileMesh.position.set(-0.25, 3.5, 30 / 2 + 6.11); // Adjust based on your scene's setup
//     settings.scene.add(profileMesh);

//     authDisplay();
// }

// let usernameMesh = null;
// let passwordMesh = null;
// let loginButtonMesh = null;
// let activeField = null;  // Track which field is currently selected
// let usernameText = '';
// let passwordText = '';

// export function authDisplay() {
//     clearAuthMeshes();
    
//     // Create username field
//     usernameMesh = createAuthField(2.8, 'Username', usernameText);
    
//     // Create password field
//     passwordMesh = createAuthField(2.5, 'Password', passwordText);
    
//     // Create login button
//     loginButtonMesh = createAuthButton(2.2, 'Login', handleLogin);

//     // Add click detection for fields
//     const raycaster = new THREE.Raycaster();
//     const mouse = new THREE.Vector2();

//     window.addEventListener('click', (event) => {
//         mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
//         mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

//         raycaster.setFromCamera(mouse, settings.camera);

//         // Check intersections with all interactive elements
//         const intersects = raycaster.intersectObjects([usernameMesh, passwordMesh, loginButtonMesh]);
//         if (intersects.length > 0) {
//             if (intersects[0].object === loginButtonMesh) {
//                 handleLogin();
//             } else {
//                 activeField = intersects[0].object === usernameMesh ? 'username' : 'password';
//                 updateFieldVisuals();
//             }
//         } else {
//             activeField = null;
//             updateFieldVisuals();
//         }
//     });

//     // Add keyboard listener
//     window.addEventListener('keydown', handleKeyPress);
// }

// function handleKeyPress(event) {
//     if (!activeField) return;

//     if (event.key === 'Backspace') {
//         if (activeField === 'username') {
//             usernameText = usernameText.slice(0, -1);
//             updateField(usernameMesh, 'Username', usernameText);
//         } else {
//             passwordText = passwordText.slice(0, -1);
//             updateField(passwordMesh, 'Password', passwordText);
//         }
//     } else if (event.key.length === 1) { // Single character keys
//         if (activeField === 'username') {
//             usernameText += event.key;
//             updateField(usernameMesh, 'Username', usernameText);
//         } else {
//             passwordText += event.key;
//             updateField(passwordMesh, 'Password', passwordText, true);
//         }
//     }
// }

// function createAuthButton(y, text, action) {
//     const canvas = document.createElement('canvas');
//     canvas.width = 300;
//     canvas.height = 100;
//     const ctx = canvas.getContext('2d');

//     // Draw button text
//     ctx.fillStyle = '#0aa23b';
//     ctx.font = '40px Courier New';
//     ctx.textAlign = 'center';
//     ctx.textBaseline = 'middle';
//     ctx.fillText(text, canvas.width / 2, canvas.height / 2);

//     const texture = new THREE.CanvasTexture(canvas);
//     const material = new THREE.MeshBasicMaterial({ map: texture, transparent: true });
//     const plane = new THREE.PlaneGeometry(1, 0.3);
    
//     const mesh = new THREE.Mesh(plane, material);
//     mesh.position.set(-0.25, y, 30 / 2 + 6.11);
//     settings.scene.add(mesh);

//     // Add click event listener
//     mesh.addEventListener('click', action);

//     return mesh;
// }

export function handleLogin() {
    // Add your login logic here
    // console.log('Login attempted');
    const overlay  = document.createElement('div');
    overlay.style.position = 'absolute';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    // overlay.style.backgroundImage = 'url("../texture/screen.png")';
    overlay.style.backgroundColor = 'rgba(32, 32, 32)';
    overlay.style.backgroundSize = 'cover';
    // overlay.style.backgroundColor = 'rgba(0, 0, 0)';
    overlay.style.color = 'white';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    // overlay.innerHTML = 'Settings';
    document.body.appendChild(overlay);

    // const gear = document.createElement('img');
    // gear.src = '../texture/gear.png';
    // gear.style.width = '100px';
    // gear.style.height = '100px';
    // gear.style.position = 'absolute';
    // gear.style.top = '10px';
    // gear.style.right = '10px';
    // // gear.eventListener('click', () => {
    // //     alert('Settings');
    // // });
    // document.body.appendChild(gear);

    // Add an image button to close the overlay
    const closeButton = document.createElement('img');
    closeButton.src = 'texture/gear_clean.png';
    closeButton.style.width = '100px';
    closeButton.style.height = '100px';
    closeButton.style.position = 'absolute';
    closeButton.style.top = '10px';
    closeButton.style.right = '10px';
    closeButton.style.cursor = 'pointer';
    closeButton.addEventListener('click', () => {
        alert('Settings');
    }
    );
    document.body.appendChild(closeButton);


    //if p is pressed make overlay disappear
    window.addEventListener('keydown', (event) => {
        if (event.key === 'p') {
            overlay.style.display = 'none';
        }
    });
}


// function createAuthField(y, placeholder, text = '') {
//     const canvas = document.createElement('canvas');
//     canvas.width = 600;
//     canvas.height = 100;
//     const ctx = canvas.getContext('2d');
    
//     // Draw text
//     ctx.fillStyle = '#0aa23b';
//     ctx.font = '40px Courier New';
//     ctx.textAlign = 'left';
//     ctx.textBaseline = 'middle';
    
//     const displayText = placeholder + ': ' + (placeholder === 'Password' ? '*'.repeat(text.length) : text);
//     ctx.fillText(displayText, 20, canvas.height / 2);

//     const texture = new THREE.CanvasTexture(canvas);
//     const material = new THREE.MeshBasicMaterial({ map: texture, transparent: true });
//     const plane = new THREE.PlaneGeometry(2, 0.5);
    
//     const mesh = new THREE.Mesh(plane, material);
//     mesh.position.set(-0.25, y, 30 / 2 + 6.11);
//     settings.scene.add(mesh);

//     return mesh;
// }

// function updateField(mesh, placeholder, text, isPassword = false) {
//     const canvas = document.createElement('canvas');
//     canvas.width = 600;
//     canvas.height = 100;
//     const ctx = canvas.getContext('2d');

//     // Draw text
//     ctx.fillStyle = '#0aa23b';
//     ctx.font = '40px Courier New';
//     ctx.textAlign = 'left';
//     ctx.textBaseline = 'middle';
    
//     const displayText = placeholder + ': ' + (isPassword ? '*'.repeat(text.length) : text) + 
//         (mesh === (activeField === 'username' ? usernameMesh : passwordMesh) ? '|' : '');
//     ctx.fillText(displayText, 20, canvas.height / 2);

//     // Update the texture
//     mesh.material.map = new THREE.CanvasTexture(canvas);
//     mesh.material.map.needsUpdate = true;
// }

// function updateFieldVisuals() {
//     updateField(usernameMesh, 'Username', usernameText);
//     updateField(passwordMesh, 'Password', passwordText, true);
// }

// function clearAuthMeshes() {
//     if (usernameMesh) {
//         settings.scene.remove(usernameMesh);
//         usernameMesh = null;
//     }
//     if (passwordMesh) {
//         settings.scene.remove(passwordMesh);
//         passwordMesh = null;
//     }
//     if (loginButtonMesh) {
//         settings.scene.remove(loginButtonMesh);
//         loginButtonMesh = null;
//     }
// }

/////////////////////////////////////Display Functions///////////////////////////////////////
export function clearDisplay() {
    // if (buttonBackgroundMesh) {
    //     settings.scene.remove(buttonBackgroundMesh);
    // }
    // if (buttonMesh) {
    //     settings.scene.remove(buttonMesh);
    // }
    // if (gearMesh) {
    //     settings.scene.remove(gearMesh);
    // }
    // if (settingMesh) {
    //     settings.scene.remove(settingMesh);
    //     clearModes();
    // }
    // if (profileMesh) {
    //     settings.scene.remove(profileMesh);
    // }
}

export function titleDisplay() {
    initStartButton();
    // initGearButton();
    // initProfileButton();
}

export function pauseDisplay() {
    // initGearButton();
    // initProfileButton();
}