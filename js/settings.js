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
        this.backgroundTexture = new THREE.TextureLoader().load('texture/sky.jpg');
        this.scene.background = this.backgroundTexture;

        ///////////////////////////////////game settings//////////////////////////////////////
        this.lineLength = 5;
        this.targetHeight = 0.6;
        this.liftSpeed = 0.1;
        this.moveSpeed = 0.3;
        this.initialBallSpeed = 0.3;
        this.ballSizeScale = 2;
        this.speedIncreaseFactor = 1.0;
        this.superChargeCount = 1;
        this.platformWidth = 50;
        this.platformLength = 30;
        this.cubeSize = 1;
        this.cubes = [];

        ///////////////////////////////////useful variables///////////////////////////////////
        this.ballSpeed = this.initialBallSpeed;
        this.ballVelocity = new THREE.Vector3(this.ballSpeed, 0, this.ballSpeed);
        this.player1Score = 0;
        this.player2Score = 0;
        this.player1HitCounter = 0;
        this.player2HitCounter = 0;
        this.ServSide = 2;
        this.lastHit = 1;
        this.gameStatus = 'playing';
		this.gameStartTime = Date.now();

        ///////////////////////////////////paddle settings////////////////////////////////////
        const centerZ = this.lineLength === this.platformLength ? 0 : Math.floor((this.platformLength - this.lineLength) / 2);
        this.player1Positions = Array(this.lineLength).fill().map((_, index) => ({ x: 0, z: centerZ + index }));
        this.player2Positions = Array(this.lineLength).fill().map((_, index) => ({ x: this.platformWidth - 1, z: centerZ + index }));

        ///////////////////////////////////visual settings////////////////////////////////////
        this.camera.position.y = Math.max(this.platformWidth, this.platformLength) * 0.8;
        this.camera.position.z = Math.max(this.platformWidth, this.platformLength) * 1;
        this.camera.lookAt(0, 0, 6);

        const ambientLight = new THREE.AmbientLight(0x606060);
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
