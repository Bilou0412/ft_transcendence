// game/scene.js - Scene setup and management
import { GAME_CONFIG } from './config.js';

export class SceneManager {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.setupRenderer();
        this.setupCamera();
        this.setupLighting();
    }

    setupRenderer() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setClearColor(0x000000);
        document.body.appendChild(this.renderer.domElement);
    }

    setupCamera() {
        const maxDimension = Math.max(GAME_CONFIG.platformWidth, GAME_CONFIG.platformLength);
        this.camera.position.set(0, maxDimension * 0.8, maxDimension * 1);
        this.camera.lookAt(0, 0, 0);
    }

    setupLighting() {
        // Add ambient light
        const ambientLight = new THREE.AmbientLight(0x606060);
        this.scene.add(ambientLight);

        // Add directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(1, 1, 1);
        this.scene.add(directionalLight);

        // Add point lights for better visibility
        const pointLight1 = new THREE.PointLight(0xffffff, 0.5);
        pointLight1.position.set(20, 20, 20);
        this.scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0xffffff, 0.5);
        pointLight2.position.set(-20, 20, -20);
        this.scene.add(pointLight2);
    }

    handleResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    render() {
        this.renderer.render(this.scene, this.camera);
    }
}
