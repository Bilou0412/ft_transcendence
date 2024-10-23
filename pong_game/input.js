// game/input.js - Input handling
export class InputHandler {
    constructor(game) {
        this.game = game;
        this.pressedKeys = {};
        this.setupEventListeners();
    }

    setupEventListeners() {
        window.addEventListener('keydown', this.onKeyDown.bind(this));
        window.addEventListener('keyup', this.onKeyUp.bind(this));
        window.addEventListener('wheel', this.onMouseWheel.bind(this));
    }

    onKeyDown(event) {
        this.pressedKeys[event.key] = true;

        if (event.key === ' ' && this.game.ball.ball.userData.heldBy !== null) {
            const direction = this.game.ball.ball.userData.heldBy === 1 ? 1 : -1;
            this.game.ball.velocity.set(direction * this.game.ball.speed * 8, 0, 0);
            this.game.ball.ball.userData.heldBy = null;
        }
    }

    onKeyUp(event) {
        this.pressedKeys[event.key] = false;
    }

    onMouseWheel(event) {
        const zoomSpeed = 0.1;
        const zoomFactor = event.deltaY > 0 ? 1 + zoomSpeed : 1 - zoomSpeed;
        
        this.game.sceneManager.camera.position.y *= zoomFactor;
        this.game.sceneManager.camera.position.z *= zoomFactor;
        
        this.game.sceneManager.camera.lookAt(0, 0, 0);
    }
}