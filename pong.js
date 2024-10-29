//#region settings

// Environment settings
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
// Load the background texture
const backgroundTexture = new THREE.TextureLoader().load('texture/sky.jpg');

// Set the background texture
scene.background = backgroundTexture;

// Game settings
const lineLength = 5; // Length of the player lines
const targetHeight = 0.6; // Height at which the cubes should be raised
const liftSpeed = 0.1; // Speed at which the cubes should be raised/lowered
const moveSpeed = 0.3; // Speed at which the players can move
const initialBallSpeed = 0.3; // Initial speed of the ball
const ballSizeScale = 2; // Size of the ball
const speedIncreaseFactor = 1.0; // Factor by which the ball speed increases on player's collision
const superChargeCount = 5; // Number of hits required to supercharge the ball

// Platform dimensions
const platformWidth = 50;  // Platform width
const platformLength = 30; // Platform length
const cubeSize = 1;
const cubes = [];

// Scores
let player1Score = 0;
let player2Score = 0;

// Add hit counters for players
let player1HitCounter = 0;
let player2HitCounter = 0;
let ServSide = 2;
let lastHit = 1;

//#endregion

//#region construction
const createRoundedBox = (width, height, depth, radius, smoothness) => {
    const shape = new THREE.Shape();
    // epsilon to prevent rendering errors
    const eps = 0.00001;
    const radius0 = radius - eps;
    //shape each corner as quarter circle
    shape.absarc(eps, eps, eps, -Math.PI / 2, -Math.PI, true);
    shape.absarc(eps, height - radius * 2, eps, Math.PI, Math.PI / 2, true);
    shape.absarc(width - radius * 2, height - radius * 2, eps, Math.PI / 2, 0, true);
    shape.absarc(width - radius * 2, eps, eps, 0, -Math.PI / 2, true);
    //extrude the shape to the depth
    const geometry = new THREE.ExtrudeBufferGeometry(shape, {
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
};

// Left side cubes
for (let i = -1; i < 2; i++) {
    for (let j = -1; j < platformLength + 1; j++) {
        const geometry = createRoundedBox(cubeSize, cubeSize, cubeSize, 0.18, 4);
        const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        const cube = new THREE.Mesh(geometry, material);
        cube.position.set(i - platformWidth / 2 + 0.5, 0, j - platformLength / 2 + 0.5);
        cube.userData.gridPosition = { x: i, z: j };
        cubes.push(cube);
        scene.add(cube);
    }
}

// Right side cubes
for (let i = platformWidth - 2; i < platformWidth + 1; i++) {
    for (let j = -1; j < platformLength + 1; j++) {
        const geometry = createRoundedBox(cubeSize, cubeSize, cubeSize, 0.18, 4);
        const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        const cube = new THREE.Mesh(geometry, material);
        cube.position.set(i - platformWidth / 2 + 0.5, 0, j - platformLength / 2 + 0.5);
        cube.userData.gridPosition = { x: i, z: j };
        cubes.push(cube);
        scene.add(cube);
    }
}

// Load the textures
const textureLoader = new THREE.TextureLoader();
const platformTexture = textureLoader.load('texture/50x30.png');
const sideTexture = textureLoader.load('texture/side50.png');

// Create materials
const platformMaterial = new THREE.MeshPhongMaterial({ map: platformTexture });
// platformMaterial.map.minFilter = THREE.LinearFilter;
const sideMaterial = new THREE.MeshPhongMaterial({ map: sideTexture });

// Create an array of materials for each face of the box
const materials = [
    sideMaterial, // Right side
    sideMaterial, // Left side
    platformMaterial, // Top side
    sideMaterial, // Bottom side
    sideMaterial, // Front side
    sideMaterial  // Back side
];

// Create middle platform with different textures
const platformGeometry = new THREE.BoxGeometry(platformWidth - 4, cubeSize, platformLength + 2);
const platform = new THREE.Mesh(platformGeometry, materials);
scene.add(platform);

// Add lighting to see the rounded edges better
const ambientLight = new THREE.AmbientLight(0x606060);
scene.add(ambientLight);
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight.position.set(1, 1, 1);
scene.add(directionalLight);

// Adjust the position of the camera for the new platform
camera.position.y = Math.max(platformWidth, platformLength) * 0.8;
camera.position.z = Math.max(platformWidth, platformLength) * 1;
camera.lookAt(0, 0, 6);

// Variables to track the current position of the cursors
const centerZ = lineLength == platformLength ? 0 : Math.floor((platformLength - lineLength) / 2);
let player1Positions = Array(lineLength).fill().map((_, index) => ({ x: 0, z: centerZ + index }));
let player2Positions = Array(lineLength).fill().map((_, index) => ({ x: platformWidth - 1, z: centerZ + index }));

// Create ball
const ballGeometry = new THREE.SphereGeometry(0.2 * ballSizeScale, 32, 32);
const ballMaterial = new THREE.MeshPhongMaterial({ 
    color: 0xff0000,
    specular: 0x888888,
    shininess: 30
});
const ball = new THREE.Mesh(ballGeometry, ballMaterial);
ball.position.set(0, 1, 0);cubeSize/2 
ball.castShadow = true;
ball.receiveShadow = true;
ball.userData.heldBy = null; // Add this line to track which player is holding the ball
scene.add(ball);

// Ball movement
let ballSpeed = initialBallSpeed;
let ballVelocity = new THREE.Vector3(ballSpeed, 0, ballSpeed);

//#endregion

//#region user interactions
// Object to track pressed keys
const pressedKeys = {};

// Update player's cube positions
function updateCubeSelection() {
    cubes.forEach(cube => {
        cube.material.color.setHex(0x00ffff);
        cube.userData.targetY = 0;
    });

    const updatePlayerCubes = (positions, player) => {
        const color = ball.userData.heldBy === player ? 0xff0000 : 0xffffff;
        positions.forEach((pos) => {
            const cube = cubes.find(cube =>
                cube.userData.gridPosition.x === Math.floor(pos.x) &&
                cube.userData.gridPosition.z === Math.floor(pos.z)
            );
            if (cube) {
                cube.material.color.setHex(color);
                cube.userData.targetY = targetHeight;
            }
        });
    };

    updatePlayerCubes(player1Positions, 1);
    updatePlayerCubes(player2Positions, 2);
}

// Update player positions based on pressed keys
function updatePlayerPositions() {
    const movePlayer = (positions, direction) => {
        const newPositions = positions.map(pos => ({
            x: pos.x,
            z: pos.z + direction * moveSpeed
        }));

        // Check if any cube in the line would go out of bounds
        if (newPositions.every(pos => pos.z >= 0 && pos.z < platformLength)) {
            return newPositions;
        }
        return positions;
    };

    // Player 1 movement
    if (pressedKeys['w'] || pressedKeys['a']) {
        player1Positions = movePlayer(player1Positions, -1);
    }
    if (pressedKeys['s'] || pressedKeys['d']) {
        player1Positions = movePlayer(player1Positions, 1);
    }

    // Player 2 movement
    if (pressedKeys['ArrowUp'] || pressedKeys['ArrowRight']) {
        player2Positions = movePlayer(player2Positions, -1);
    }
    if (pressedKeys['ArrowDown'] || pressedKeys['ArrowLeft']) {
        player2Positions = movePlayer(player2Positions, 1);
    }
}

function updatePaddleColor(player, color) 
{
    const positions = player === 1 ? player1Positions : player2Positions;
    positions.forEach((pos) => {
        const cube = cubes.find(cube =>
            cube.userData.gridPosition.x === Math.floor(pos.x) &&
            cube.userData.gridPosition.z === Math.floor(pos.z)
        );
        if (cube) {
            cube.material.color.setHex(color);
        }
    });
}

//#endregion

//#region ball physics
function grabBall(player) 
{
    ball.userData.heldBy = player;
	if (player === 1)
	{
		player1HitCounter = 0;
		updatePaddleColor(1, 0xff0000);
	}
	else
	{
		player2HitCounter = 0;
		updatePaddleColor(2, 0xff0000);
	}
	updateHitCounter1Display();
	updateHitCounter2Display();
}

function updateBallPosition() {
    if (ball.userData.heldBy !== null) {
        // If the ball is held by a player, update its position to follow the paddle
        const playerPositions = ball.userData.heldBy === 1 ? player1Positions : player2Positions;
        const middlePos = playerPositions[Math.floor(lineLength / 2)];
        ball.position.set(
            middlePos.x - platformWidth / 2 + (ball.userData.heldBy === 1 ? 2 : -1),
            1,
            middlePos.z - platformLength / 2
        )
        return;
    }

    // Calculate potential new position (only in XZ plane)
    const potentialPosition = ball.position.clone().add(new THREE.Vector3(ballVelocity.x, 0, ballVelocity.z));

    // Create a ray for collision detection (only in XZ plane)
    const rayDirection = new THREE.Vector3(ballVelocity.x, -0.2, ballVelocity.z).normalize();
    const ray = new THREE.Ray(ball.position, rayDirection);
    // const rayLength = new THREE.Vector3(ballVelocity.x, -0.2, ballVelocity.z).length();
    const rayLength = 0.2;

    // Check for collisions with raised cubes
    let collision = false;
    let closestIntersection = null;
    let closestCube = null;

    cubes.forEach(cube => {
        if (cube.material.color.getHex() === 0xffffff || cube.material.color.getHex() === 0xff0000) {
            const cubeBoundingBox = new THREE.Box3().setFromObject(cube);
            const intersection = ray.intersectBox(cubeBoundingBox, new THREE.Vector3());


            if (intersection && intersection.distanceTo(ball.position) <= rayLength) {
                if (!closestIntersection || intersection.distanceTo(ball.position) < closestIntersection.distanceTo(ball.position)) {
                    closestIntersection = intersection;
                    closestCube = cube;
                    collision = true;
                }
            }
        }
    });

    if (collision) {
        // Handle collision using your original angle-based rebound method
        const player = closestCube.position.x < 0 ? 1 : 2;
        const hitCounter = player === 1 ? player1HitCounter : player2HitCounter;

        if (hitCounter >= superChargeCount) 
            grabBall(player);
        else 
        {
            // Increment hit counter
            if (player === 1 && lastHit != 1) {
                player1HitCounter++;
                lastHit = 1;
            } 
            else if (player === 2 && lastHit != 2)
            {
                player2HitCounter++;
                lastHit = 2;    
            }
            updateHitCounter1Display();
            updateHitCounter2Display();

            let paddleMiddle;
            if (player === 1)
                paddleMiddle = player1Positions[Math.floor(lineLength / 2)].z;
            else
                paddleMiddle = player2Positions[Math.floor(lineLength / 2)].z;
            const paddleMiddleOnplane = paddleMiddle - ((platformLength / 2) * cubeSize);
            let side = 0;

            // Check if the collision is on the front face or top/bottom edges
            if (Math.abs(closestIntersection.z - paddleMiddleOnplane) < lineLength / 2 - 0.1) 
            {
                // Front face collision - use angle-based rebound
                const maxAngle = 0.3;
                const angle = Math.max(maxAngle * -1, Math.min(maxAngle, ((potentialPosition.z - paddleMiddleOnplane) / (lineLength / 2)) * maxAngle));

                ballVelocity.z = angle;
                ballVelocity.x *= -1;
                side = 0;
            } 
            else 
            {
                // Top or bottom edge collision - reverse Z velocity
                ballVelocity.z *= -1;
                if (closestIntersection.z < paddleMiddleOnplane) 
                {
                    // ballVelocity.z = Math.abs(ballVelocity.z) * -1;
                    side = 0.2;
                }
                else
                    side = -0.2;
            }

            // Adjust ball position to prevent sticking to the position of the impact
            let positionOnPaddle = new THREE.Vector3(closestCube.position.x + (ballVelocity.x > 0 ? 1.1: -1.1), 1, closestCube.position.z + side);
            ball.position.copy(positionOnPaddle);
            // ball.position.copy(closestIntersection);

            // Increase ball speed on collision with player
            ballSpeed = ballSpeed * speedIncreaseFactor;
            ballVelocity.normalize().multiplyScalar(ballSpeed);
        }
    } 
    else 
    {
        // Update ball position if no collision occurred
        ball.position.copy(potentialPosition);
    }

    // Make ball bounce on walls
    if (ball.position.z < -platformLength / 2 + 0.5 || ball.position.z > platformLength / 2 - 0.5) {
        ballVelocity.z *= -1;
        ball.position.z = Math.max(Math.min(ball.position.z, platformLength / 2 - 0.5), -platformLength / 2 + 0.5);
    }

    // Check if ball is behind player lines
    if (ball.position.x < -platformWidth / 2 - 1) //left side
    {
        player2Score++;
        updateScoreDisplay();
		ServSide = 1;
        resetBall();

    }
    else if (ball.position.x > platformWidth / 2 + 1) //right side
    {
        player1Score++;
        updateScoreDisplay();
		ServSide = 2;
        resetBall();
    }
}
//#endregion

//#region utils functions

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function resetBall() {
    ball.position.set(0, 1, 0);
    ballSpeed = 0; // La balle reste immobile après le reset
    ballVelocity.set(0, 0, 0); // Pas de mouvement initial
    ball.userData.heldBy = null;
    player1HitCounter = 0;
    player2HitCounter = 0;
    updateHitCounter1Display();
    updateHitCounter2Display();
    updatePaddleColor(1, 0xffffff); // Réinitialise la couleur du paddle du joueur 1
    updatePaddleColor(2, 0xffffff); // Réinitialise la couleur du paddle du joueur 2

    // Attendre 1 seconde avant de relancer la balle
    await sleep(1000);

    // Relance la balle après 1 seconde
    ballSpeed = initialBallSpeed;
    ballVelocity = new THREE.Vector3(ballSpeed * (ServSide == 1 ? -1 : 1), 0, ballSpeed * (Math.random() > 0.5 ? 1 : -1));
}
//#endregion

//#region scoreboard
// Load the scoreboard image texture
const scoreboardTexture = new THREE.TextureLoader().load('texture/Scoreboard.png');
const scoreboardMaterial = new THREE.MeshBasicMaterial({ map: scoreboardTexture });

// Create the scoreboard plane
const scoreboardWidth = 20; // Adjust the width as needed
const scoreboardHeight = 10; // Adjust the height as needed
const scoreboardGeometry = new THREE.PlaneGeometry(scoreboardWidth, scoreboardHeight);
const scoreboardMesh = new THREE.Mesh(scoreboardGeometry, scoreboardMaterial);
scoreboardMesh.position.set(0, 10, -platformLength / 2 - 2); // Adjust the position as needed
scene.add(scoreboardMesh);

const scoreDisplay = document.createElement('canvas');
scoreDisplay.width = 1200;
scoreDisplay.height = 600;
const scoreDisplayCtx = scoreDisplay.getContext('2d');
const updateScoreDisplay = () => {
    scoreDisplayCtx.clearRect(0, 0, scoreDisplay.width, scoreDisplay.height);
    scoreDisplayCtx.fillStyle = 'white';
    scoreDisplayCtx.font = 'bold 100px "Digital-7"';

    // Calculate text widths for each part of the scoreboard
    const player1ScoreText = `${player1Score}`;
    const player2ScoreText = `${player2Score}`;


    // Draw the scores and separator at calculated positions
    scoreDisplayCtx.fillText(player1ScoreText, 300, 300);
    scoreDisplayCtx.fillText(player2ScoreText, 850, 300);

    // Update the texture to reflect the new score
    scoreDisplayTexture.needsUpdate = true;
};


const scoreDisplayTexture = new THREE.CanvasTexture(scoreDisplay);
const scoreDisplayMaterial = new THREE.MeshBasicMaterial({ map: scoreDisplayTexture, transparent: true });
const scoreDisplayPlane = new THREE.PlaneGeometry(2, 1);
const scoreDisplayMesh = new THREE.Mesh(scoreDisplayPlane, scoreDisplayMaterial);
scoreDisplayMesh.scale.set(10, 10, 10);
scoreDisplayMesh.position.set(0, 10, -platformLength / 2 - 1.9);
scene.add(scoreDisplayMesh);
//#endregion

//#region clock

const Clock = document.createElement('canvas');
Clock.width = 1200;
Clock.height = 600;
const ClockCtx = Clock.getContext('2d');
const updateClock = () => {
    ClockCtx.clearRect(0, 0, Clock.width, Clock.height);
    ClockCtx.fillStyle = 'white';
    ClockCtx.font = 'bold 100px "Digital-7"';

    const elapsedTime = Math.floor((Date.now() - gameStartTime) / 1000); // Get elapsed time
    const minutes = Math.floor(elapsedTime / 60);
    const seconds = elapsedTime % 60;
    
    const formattedTime = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    


    // Draw the scores and separator at calculated positions
    ClockCtx.fillText(formattedTime, 500, 100);

    // Update the texture to reflect the new score
    ClockTexture.needsUpdate = true;
    setTimeout(updateClock, 1000);
};


const ClockTexture = new THREE.CanvasTexture(Clock);
const ClockMaterial = new THREE.MeshBasicMaterial({ map: ClockTexture, transparent: true });
const ClockPlane = new THREE.PlaneGeometry(2, 1);
const ClockMesh = new THREE.Mesh(ClockPlane, ClockMaterial);
ClockMesh.scale.set(10, 10, 10);
ClockMesh.position.set(0, 10, -platformLength / 2 - 1.9);
scene.add(ClockMesh);

//#endregion

//#region hit counter
let charge1 = null;
let charge2 = null;

function updateHitCounter1Display() {
    // Remove the previous charge1 rectangle
    if (charge1) {
        scene.remove(charge1);
        charge1 = null;
    }

    if (player1HitCounter > 0) {
        const length_max = 5.5;
        const width_max = 0.5;
        const length = length_max * (player1HitCounter / superChargeCount);
        const charge1Geometry = new THREE.PlaneGeometry(length, width_max); // Width and height of the charge1
        const charge1Material = new THREE.MeshBasicMaterial({ color: 0xff0000, side: THREE.DoubleSide });
        charge1 = new THREE.Mesh(charge1Geometry, charge1Material);

        // Set the position of the charge1
        const middle = -4.75;
        const x = middle - (length_max / 2) + (length / 2);
        charge1.position.set(x, 8.25, -platformLength / 2 - 1.9); // Adjust the position as needed

        // Add the charge1 to the scene
        scene.add(charge1);
    }
}

function updateHitCounter2Display() {
    // Remove the previous charge2 rectangle
    if (charge2) {
        scene.remove(charge2);
        charge2 = null;
    }

    if (player2HitCounter > 0) {
        const length_max = 5.5;
        const width_max = 0.5;
        const length = length_max * (player2HitCounter / superChargeCount);
        const charge2Geometry = new THREE.PlaneGeometry(length, width_max); // Width and height of the charge2
        const charge2Material = new THREE.MeshBasicMaterial({ color: 0xff0000, side: THREE.DoubleSide });
        charge2 = new THREE.Mesh(charge2Geometry, charge2Material);

        // Set the position of the charge2
        const middle = 4.75;
        const x = middle - (length_max / 2) + (length / 2);
        charge2.position.set(x, 8.25, -platformLength / 2 - 1.9); // Adjust the position as needed

        // Add the charge2 to the scene
        scene.add(charge2);
    }
}
//#endregion

//#region monitor
// Load the monitor model
let loadedModel;
const glftLoader = new THREE.GLTFLoader();
glftLoader.load('./models/new_retro_computer/scene.gltf', (gltfScene) => {
    gltfScene.scene.position.z = platformLength / 2 + 8;
    gltfScene.scene.scale.set(2, 2, 2);

    scene.add(gltfScene.scene);
});

const MonitorDisplay = document.createElement('canvas');
MonitorDisplay.width = 500;
MonitorDisplay.height = 300;
const MonitorDisplayCtx = MonitorDisplay.getContext('2d');
const updateMonitorDisplay = () => {
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


const MonitorDisplayTexture = new THREE.CanvasTexture(MonitorDisplay);
const MonitorDisplayMaterial = new THREE.MeshBasicMaterial({ map: MonitorDisplayTexture, transparent: true });
const MonitorDisplayPlane = new THREE.PlaneGeometry(2, 1);
const MonitorDisplayMesh = new THREE.Mesh(MonitorDisplayPlane, MonitorDisplayMaterial);
MonitorDisplayMesh.scale.set(2, 3, 3);
MonitorDisplayMesh.position.set(-0.2, 2.5, platformLength / 2 + 6.1);
scene.add(MonitorDisplayMesh);


// #endregion

//#region focus
// Define target positions and orientations for each focus
const gameView = {
    position: { x: 0, y: platformWidth * 0.8, z: platformLength },
    rotation: { x: -0.8, y: 0, z: 0 }
};

const monitorView = {
    position: { x: 0, y: 3, z: 23.5 },
    rotation: { x: -0.2, y: 0, z: 0 }
};

// Function to smoothly transition to the game view
function focusGame() {
    gsap.to(camera.position, {
        duration: 2,  // Duration of the animation in seconds
        x: gameView.position.x,
        y: gameView.position.y,
        z: gameView.position.z,
        ease: "power2.inOut"
    });

    gsap.to(camera.rotation, {
        duration: 2,
        x: gameView.rotation.x,
        y: gameView.rotation.y,
        z: gameView.rotation.z,
        ease: "power2.inOut"
    });
}

// Function to smoothly transition to the monitor view
function focusMonitor() {
    gsap.to(camera.position, {
        duration: 2,
        x: monitorView.position.x,
        y: monitorView.position.y,
        z: monitorView.position.z,
        ease: "power2.inOut"
    });

    gsap.to(camera.rotation, {
        duration: 2,
        x: monitorView.rotation.x,
        y: monitorView.rotation.y,
        z: monitorView.rotation.z,
        ease: "power2.inOut"
    });
}
//#endregion

//#region game loop
// Animation loop
function animate() {
    requestAnimationFrame(animate);

    updatePlayerPositions();
    updateCubeSelection();
    updateBallPosition();

    // Raise/lower cubes animation
    cubes.forEach(cube => {
        if (cube.userData.targetY !== undefined) {
            cube.position.y += (cube.userData.targetY - cube.position.y) * liftSpeed;
        }
    });

    renderer.render(scene, camera);
}

// Keyboard event handlers
function onKeyDown(event) {
    pressedKeys[event.key] = true;

    // Release the ball when space is pressed
	if (event.key === ' ' && ball.userData.heldBy !== null) {
        const direction = ball.userData.heldBy === 1 ? 1 : -1;
        ballVelocity.set(direction * ballSpeed * 8, 0, 0);
        const player = ball.userData.heldBy;
        ball.userData.heldBy = null;
        updatePaddleColor(player, 0xffffff); // Reset paddle color to white
    }

    if (event.key === 'Escape'){
        if ( gameStatus === 'playing') {
            focusMonitor();
            gameStatus = 'paused';
        } else {
            focusGame();
            gameStatus = 'playing';
        }
    }
}

function onKeyUp(event) {
    pressedKeys[event.key] = false;
}

// Mouse wheel event handler
function onMouseWheel(event) {
    const zoomSpeed = 0.1;
    const zoomFactor = event.deltaY > 0 ? 1 + zoomSpeed : 1 - zoomSpeed;
    
    camera.position.y *= zoomFactor;
    camera.position.z *= zoomFactor;
    
    camera.lookAt(0, 0, 6);
}

window.addEventListener('keydown', onKeyDown, false);
window.addEventListener('keyup', onKeyUp, false);
window.addEventListener('wheel', onMouseWheel, false);

// Start the animation loop
// animate();

function resetGame() {
    player1Score = 0;
    player2Score = 0;
    updateScoreDisplay();
    resetBall();
}

let gameStatus = 'playing';

let gameStartTime;
function startGame() {
    gameStartTime = Date.now();
    updateClock();
    updateMonitorDisplay();
    resetGame();
    animate();
}

document.getElementById('startButton').addEventListener('click', function() {
    // Cacher l'écran titre
    document.getElementById('titleScreen').style.display = 'none';

    // Lancer le jeu
    startGame();
});

//#endregion