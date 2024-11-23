// Double click handler
const lastClickTimes = new Map();
const DOUBLE_CLICK_DELAY = 300;

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

const handleLocation = async () => {
    const path = window.location.pathname;
    console.log(path);
    const route = routes[path] || routes[404];
    const html = await fetch(route).then((data) => data.text());
    document.getElementById("main-page").innerHTML = html;
    document.body.setAttribute('data-show-navbar', path === '/');

    if (path === '/pong') {
        const script = document.createElement('script');
        script.src = '../js/main.js';
        script.type = 'module';
        document.getElementById("main-page").appendChild(script);
    }
};

window.onpopstate = handleLocation;
window.route = route;
handleLocation();