// Double click handler
const lastClickTimes = new Map();
const DOUBLE_CLICK_DELAY = 300;

// Keep track of the current pong script
let currentPongScript = null;

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
        // Forced path without click
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

const cleanupPongScript = () => {
    if (currentPongScript) {
        // If the script defined a cleanup function, call it
        if (window.cleanupPong && typeof window.cleanupPong === 'function') {
            window.cleanupPong();
            window.cleanupPong = null;
        }
        
        // Remove the script element
        currentPongScript.remove();
        currentPongScript = null;
    }
};

const insertHTMLAndWaitForButton = async (html) => {
    // Insert the HTML
    document.getElementById("main-page").innerHTML = html;
    
    // Wait for the button to be available in DOM
    return new Promise((resolve) => {
        const checkButton = () => {
            if (document.getElementById('startButton')) {
                resolve();
            } else {
                // Check again in a few milliseconds
                setTimeout(checkButton, 10);
            }
        };
        checkButton();
    });
};

const handleLocation = async () => {
    const path = window.location.pathname;
    console.log(path);
    
    // Clean up pong script if we're navigating away from pong
    if (currentPongScript && path !== '/pong') {
        cleanupPongScript();
    }
    
    const route = routes[path] || routes[404];
    const html = await fetch(route).then((data) => data.text());
    
    if (path === '/pong') {
        // Insert HTML and wait for button to be available
        await insertHTMLAndWaitForButton(html);
        
        // Now load the script
        const script = document.createElement('script');
        script.src = '../js/main.js';
        script.type = 'module';
        currentPongScript = script;
        document.getElementById("main-page").appendChild(script);
    } else {
        // For other routes, just insert the HTML normally
        document.getElementById("main-page").innerHTML = html;
    }
    
    document.body.setAttribute('data-show-navbar', path === '/');
};

window.onpopstate = handleLocation;
window.route = route;
handleLocation();