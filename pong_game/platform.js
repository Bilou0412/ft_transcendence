// game/platform.js - Platform creation and management
import { GAME_CONFIG } from './config.js';

export class Platform {
    constructor(scene) {
        this.scene = scene;
        this.cubes = [];
        this.createPlatform();
    }

    createRoundedBox(width, height, depth, radius, smoothness) {
        const shape = new THREE.Shape();
        const eps = 0.00001;
        const radius0 = radius - eps;
        
        shape.absarc(eps, eps, eps, -Math.PI / 2, -Math.PI, true);
        shape.absarc(eps, height - radius * 2, eps, Math.PI, Math.PI / 2, true);
        shape.absarc(width - radius * 2, height - radius * 2, eps, Math.PI / 2, 0, true);
        shape.absarc(width - radius * 2, eps, eps, 0, -Math.PI / 2, true);
        
        const geometry = new THREE.ExtrudeGeometry(shape, {
            depth: depth - radius0 * 2,
            bevelEnabled: true,
            bevelSegments: smoothness * 2,
            steps: 1,
            bevelSize: radius,
            bevelThickness: radius0,
            curveSegments: smoothness
        });
        
        geometry.center();
        return geometry;
    }

    createPlatform() {
        // Create left side cubes
        this.createSideCubes(-1, 2);
        // Create right side cubes
        this.createSideCubes(GAME_CONFIG.platformWidth - 2, GAME_CONFIG.platformWidth + 1);
    }

    createSideCubes(startX, endX) {
        for (let i = startX; i < endX; i++) {
            for (let j = -1; j < GAME_CONFIG.platformLength + 1; j++) {
                const cube = this.createCube(i, j);
                this.cubes.push(cube);
                this.scene.add(cube);
            }
        }
    }

    createCube(i, j) {
        const geometry = this.createRoundedBox(GAME_CONFIG.cubeSize, GAME_CONFIG.cubeSize, GAME_CONFIG.cubeSize, 0.18, 4);
        const material = new THREE.MeshPhongMaterial({ 
            color: 0x00ffff,
            shininess: 30,
            specular: 0x444444
        });
        const cube = new THREE.Mesh(geometry, material);
        cube.position.set(
            i - GAME_CONFIG.platformWidth / 2 + 0.5,
            0,
            j - GAME_CONFIG.platformLength / 2 + 0.5
        );
        cube.userData.gridPosition = { x: i, z: j };
        return cube;
    }

    update() {
        this.cubes.forEach(cube => {
            if (cube.userData.targetY !== undefined) {
                cube.position.y += (cube.userData.targetY - cube.position.y) * GAME_CONFIG.liftSpeed;
            }
        });
    }
}