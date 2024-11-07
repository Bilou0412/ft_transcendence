/////////////////////////////////Environment settings/////////////////////////////////
export class Settings {
    constructor() {
        /////////////////////////////////3D environment settings//////////////////////////////
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);

        // Load the background texture
        // this.backgroundTexture = new THREE.TextureLoader().load('texture/sky.jpg');
        // this.scene.background = this.backgroundTexture;

        ///////////////////////////////////game settings//////////////////////////////////////
        this.lineLength = 5; // Paddle length
        this.targetHeight = 0.6; // Lift height for the cubes
        this.liftSpeed = 0.1; // Speed of the cubes lift
        this.moveSpeed = 0.3; // Speed of the paddles
        this.initialBallSpeed = 0.3; // Initial speed of the ball
        this.ballSizeScale = 2; // Ball size
        this.speedIncreaseFactor = 1.0; // Speed increase factor after each hit
        this.superChargeCount = 5; // Number of hits to supercharge the ball
        this.platformWidth = 50; // Width of the platform
        this.platformLength = 30; // Length of the platform
        this.cubeSize = 1; // Size of the cubes
        this.cubes = [];

        ///////////////////////////////////useful variables///////////////////////////////////
        this.ballSpeed = this.initialBallSpeed;
        this.ballVelocity = new THREE.Vector3(this.ballSpeed, 0, this.ballSpeed);
        this.player1Score = 0;
        this.player2Score = 0;
        this.player1HitCounter = 0; // Number of hits by player 1 for supercharge
        this.player2HitCounter = 0; // Number of hits by player 2 for supercharge
        this.ServSide = 2; // Wich player will serve
        this.lastHit = 1; // Last player to hit the ball
        this.gameStatus = 'title';
		this.gameStartTime = Date.now();

        ///////////////////////////////////paddle settings////////////////////////////////////
        const centerZ = this.lineLength === this.platformLength ? 0 : Math.floor((this.platformLength - this.lineLength) / 2);
        this.player1Positions = Array(this.lineLength).fill().map((_, index) => ({ x: 0, z: centerZ + index }));
        this.player2Positions = Array(this.lineLength).fill().map((_, index) => ({ x: this.platformWidth - 1, z: centerZ + index }));

        ///////////////////////////////////visual settings////////////////////////////////////
        // this.camera.position.y = Math.max(this.platformWidth, this.platformLength) * 0.8;
        this.camera.position.y = 3;
        // this.camera.position.z = Math.max(this.platformWidth, this.platformLength) * 1;
        this.camera.position.z = 23.5;
        this.camera.lookAt(0, 0, 6);

        const ambientLight = new THREE.AmbientLight(0xffffff, 1);
        this.scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(1, 1, 1);
        this.scene.add(directionalLight);
    }

    ///////////////////////////////////update functions////////////////////////////////////
    updateBallSpeed(newValue) { this.ballSpeed = newValue; }
    updateBallVelocity(newValue) { this.ballVelocity = newValue; }
    updatePlayer1Score(newValue) { this.player1Score = newValue; }
    updatePlayer2Score(newValue) { this.player2Score = newValue; }
    updatePlayer1HitCounter(newValue) { this.player1HitCounter = newValue; }
    updatePlayer2HitCounter(newValue) { this.player2HitCounter = newValue; }
    updateServSide(newValue) { this.ServSide = newValue; }
    updateLastHit(newValue) { this.lastHit = newValue; }
    updateGameStatus(newValue) { this.gameStatus = newValue; }
    updatePlayer1Positions(newValue) { this.player1Positions = newValue; }
    updatePlayer2Positions(newValue) { this.player2Positions = newValue; }
}
