// game/ball.js - Ball creation and management
import { GAME_CONFIG } from './config.js';

export class Ball {
    constructor(scene) {
        this.scene = scene;
        this.ball = this.createBall();
        this.velocity = new THREE.Vector3(GAME_CONFIG.initialBallSpeed, 0, GAME_CONFIG.initialBallSpeed);
        this.speed = GAME_CONFIG.initialBallSpeed;
    }

    createBall() {
        const geometry = new THREE.SphereGeometry(0.2 * GAME_CONFIG.ballSizeScale, 32, 32);
        const material = new THREE.MeshPhongMaterial({
            color: 0xff0000,
            specular: 0x888888,
            shininess: 30
        });
        const ball = new THREE.Mesh(geometry, material);
        ball.position.set(0, 1, 0);
        ball.castShadow = true;
        ball.receiveShadow = true;
        ball.userData.heldBy = null;
        this.scene.add(ball);
        return ball;
    }

	updatePosition(players, platform) {
        if (this.ball.userData.heldBy !== null) {
            const playerPositions = this.ball.userData.heldBy === 1 ? 
                players.player1Positions : players.player2Positions;
            const middlePos = playerPositions[Math.floor(GAME_CONFIG.lineLength / 2)];
            
            if (this.ball.userData.heldBy === 1) {
                this.ball.position.set(middlePos.x - 23, 1, middlePos.z - 14);
            } else {
                this.ball.position.set(middlePos.x - 26, 1, middlePos.z - 14);
            }
            return;
        }

        const potentialPosition = this.ball.position.clone().add(this.velocity);
        const rayDirection = new THREE.Vector3(this.velocity.x, -0.2, this.velocity.z).normalize();
        const ray = new THREE.Ray(this.ball.position, rayDirection);
        const rayLength = 0.2;

        this.handleCollisions(ray, rayLength, potentialPosition, platform, players);
        this.handleWallBounce();
        this.checkScoring(players);
    }

    handleCollisions(ray, rayLength, potentialPosition, platform, players) {
        let collision = false;
        let closestIntersection = null;
        let closestCube = null;

        platform.cubes.forEach(cube => {
            if (cube.material.color.getHex() === 0xffffff || cube.material.color.getHex() === 0xff0000) {
                const cubeBoundingBox = new THREE.Box3().setFromObject(cube);
                const intersection = ray.intersectBox(cubeBoundingBox, new THREE.Vector3());

                if (intersection && intersection.distanceTo(this.ball.position) <= rayLength) {
                    if (!closestIntersection || intersection.distanceTo(this.ball.position) < closestIntersection.distanceTo(this.ball.position)) {
                        closestIntersection = intersection;
                        closestCube = cube;
                        collision = true;
                    }
                }
            }
        });

        if (collision) {
            this.handlePaddleCollision(closestCube, closestIntersection, potentialPosition, players);
        } else {
            this.ball.position.copy(potentialPosition);
        }
    }

    handlePaddleCollision(cube, intersection, potentialPosition, players) {
        const player = cube.position.x < 0 ? 1 : 2;
        const hitCounter = player === 1 ? players.player1HitCounter : players.player2HitCounter;

        if (hitCounter >= GAME_CONFIG.superChargeCount) {
            this.grabBall(player, players);
        } else {
            this.calculateRebound(cube, intersection, player, players);
        }
    }

    async reset(servingSide) {
        this.ball.position.set(0, 1, 0);
        this.speed = 0;
        this.velocity.set(0, 0, 0);
        this.ball.userData.heldBy = null;

        await new Promise(resolve => setTimeout(resolve, 1000));

        this.speed = GAME_CONFIG.initialBallSpeed;
        this.velocity = new THREE.Vector3(
            this.speed * (servingSide === 1 ? -1 : 1),
            0,
            this.speed * (Math.random() > 0.5 ? 1 : -1)
        );
    }

    grabBall(player, players) {
        this.ball.userData.heldBy = player;
        if (player === 1) {
            players.player1HitCounter = 0;
        } else {
            players.player2HitCounter = 0;
        }
    }

}