import { settings, startGame } from "./main.js";
import { clearBall } from "./ball_init.js";
import { clearSides, clearMiddle } from "./roundedBox.js";
import { clearScoreboard } from "./display.js";
// import { clearModes, gameModesDisplay } from "./monitor_display.js";

export function gameMode(length, width, line){
	clearBall();
	clearSides();
	clearMiddle();
	clearScoreboard();
	settings.platformLength = length;
	settings.platformWidth = width;
	settings.lineLength = line;
	startGame();
	settings.gameStatus = 'paused';
	settings.gameMode = length + 'x' + width;
	//put the players paddle in the middle
	const centerZ = settings.lineLength === settings.platformLength ? 0 : Math.floor((settings.platformLength - settings.lineLength) / 2);
	settings.player1Positions = Array(settings.lineLength).fill().map((_, index) => ({ x: 0, z: centerZ + index }));
	settings.player2Positions = Array(settings.lineLength).fill().map((_, index) => ({ x: settings.platformWidth - 1, z: centerZ + index }));
	clearModes();
	gameModesDisplay();
}