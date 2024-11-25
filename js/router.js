// Double click handler
const lastClickTimes = new Map();
const DOUBLE_CLICK_DELAY = 300;

// Keep track of the current pong script and module
let currentPongScript = null;
let pongModule = null;
let startButtonListener = null;

const attachStartButtonListener = async () => {
    const startButton = document.getElementById('startButton');
    if (startButton && !startButton.hasListener) {
        startButtonListener = async () => {
            const { initializeGame } = await import('./main.js');
            initializeGame();
        };
        startButton.addEventListener('click', startButtonListener);
        startButton.hasListener = true;
    }
};

export const route = (event = null, forcedPath = null) => {
    event = event || window.event;
    if (event) {
        event.preventDefault();
    }

    let path = forcedPath;
    let link = null;

    if (!path) {
        link = event?.target.closest('a');
        if (link) {
            path = link.href;
        }
    }

    if (path && link) {
        const currentTime = new Date().getTime();
        const lastClickTime = lastClickTimes.get(path) || 0;
        
        if (currentTime - lastClickTime <= DOUBLE_CLICK_DELAY) {
            window.history.pushState({}, "", path);
            handleLocation();
            lastClickTimes.delete(path);
        } else {
            lastClickTimes.set(path, currentTime);
        }
    } else if (forcedPath) {
        window.history.pushState({}, "", path);
        handleLocation();
    }
};

const routes = {
    404: "/html/404.html",
    "/": "/html/index.html",
    "/settings": "/html/settings.html",
    "/profile": "/html/profile.html",
    "/pong": "/html/pong.html"
};

const cleanupPongScript = async () => {
    if (pongModule && typeof pongModule.quitPong === 'function') {
        await pongModule.quitPong();
    }
    
    const startButton = document.getElementById('startButton');
    if (startButton && startButtonListener) {
        startButton.removeEventListener('click', startButtonListener);
        startButton.hasListener = false;
    }
    
    if (currentPongScript) {
        currentPongScript.remove();
        currentPongScript = null;
    }

    pongModule = null;
};

const insertHTMLAndWaitForButton = async (html) => {
    document.getElementById("main-page").innerHTML = html;
    
    return new Promise((resolve) => {
        const checkButton = () => {
            const button = document.getElementById('startButton');
            if (button) {
                attachStartButtonListener();
                resolve();
            } else {
                setTimeout(checkButton, 10);
            }
        };
        checkButton();
    });
};

const loadPongModule = async () => {
    try {
        pongModule = await import('../js/main.js');
        return true;
    } catch (error) {
        console.error('Error loading pong module:', error);
        return false;
    }
};

const handleLocation = async () => {
    const path = window.location.pathname;
    console.log(path);
    
    if ((currentPongScript || pongModule) && path !== '/pong') {
        await cleanupPongScript();
    }
    
    const route = routes[path] || routes[404];
    const html = await fetch(route).then((data) => data.text());
    
    if (path === '/pong') {
        await insertHTMLAndWaitForButton(html);
        
        const script = document.createElement('script');
        script.src = '../js/main.js';
        script.type = 'module';
        currentPongScript = script;
        document.getElementById("main-page").appendChild(script);
        
        await loadPongModule();
    } else {
        document.getElementById("main-page").innerHTML = html;
    }
    
    document.body.setAttribute('data-show-navbar', path === '/');
};

window.onpopstate = handleLocation;
window.route = route;
handleLocation();