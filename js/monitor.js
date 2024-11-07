///////////////////////////////////////imports////////////////////////////////////////
import { settings } from './main.js';


///////////////////////////////////////monitor////////////////////////////////////////
let MonitorDisplay = null;
let MonitorDisplayCtx = null;
let MonitorDisplayTexture = null;
export function initMonitor(){
	const glftLoader = new THREE.GLTFLoader();
    glftLoader.load('./models/new_retro_computer/scene.gltf', (gltfScene) => {
        // Set position and scale of the model
        gltfScene.scene.position.z = settings.platformLength / 2 + 8;
        gltfScene.scene.scale.set(2, 2, 2);

        settings.scene.add(gltfScene.scene);

    });
	
	MonitorDisplay = document.createElement('canvas');
	MonitorDisplay.width = 500;
	MonitorDisplay.height = 300;
	MonitorDisplayCtx = MonitorDisplay.getContext('2d');

	MonitorDisplayTexture = new THREE.CanvasTexture(MonitorDisplay);
	const MonitorDisplayMaterial = new THREE.MeshBasicMaterial({ map: MonitorDisplayTexture, transparent: true });
	const MonitorDisplayPlane = new THREE.PlaneGeometry(2, 1);
	const MonitorDisplayMesh = new THREE.Mesh(MonitorDisplayPlane, MonitorDisplayMaterial);
	MonitorDisplayMesh.scale.set(2, 3, 3);
	MonitorDisplayMesh.position.set(-0.2, 2.5, settings.platformLength / 2 + 6.1);
	settings.scene.add(MonitorDisplayMesh);
}

export const updateMonitorDisplay = () => {
    MonitorDisplayCtx.clearRect(0, 0, MonitorDisplay.width, MonitorDisplay.height);

    MonitorDisplayCtx.fillStyle = 'green';
    MonitorDisplayCtx.font = 'bold 100px "Digital-7"';

    const characters = 'abcdefghijklmnopqrstuvwxyz';
    let result = '';
    for (let i = 0; i < 8; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    const formattedTime = result;
    MonitorDisplayCtx.fillText(formattedTime, 60, 100);

    // Update the texture to reflect the new score
    MonitorDisplayTexture.needsUpdate = true;
    setTimeout(updateMonitorDisplay, 100);
};


/////////////////////////////////////View Focus///////////////////////////////////////
export function focusGame() {
	// Define target positions and orientations for each focus
	const gameView = {
		position: { x: 0, y: settings.platformWidth * 0.6, z: settings.platformLength * 1},
		rotation: { x: -0.9, y: 0, z: 0 }
	};

    gsap.to(settings.camera.position, {
        duration: 2,  // Duration of the animation in seconds
        x: gameView.position.x,
        y: gameView.position.y,
        z: gameView.position.z,
        ease: "power2.inOut"
    });

    gsap.to(settings.camera.rotation, {
        duration: 2,
        x: gameView.rotation.x,
        y: gameView.rotation.y,
        z: gameView.rotation.z,
        ease: "power2.inOut"
    });
}

export function focusMonitor() {
	const monitorView = {
		position: { x: 0, y: 3, z: 23.5 },
		rotation: { x: -0.2, y: 0, z: 0 }
	};
	
    gsap.to(settings.camera.position, {
        duration: 2,
        x: monitorView.position.x,
        y: monitorView.position.y,
        z: monitorView.position.z,
        ease: "power2.inOut"
    });

    gsap.to(settings.camera.rotation, {
        duration: 2,
        x: monitorView.rotation.x,
        y: monitorView.rotation.y,
        z: monitorView.rotation.z,
        ease: "power2.inOut"
    });
}