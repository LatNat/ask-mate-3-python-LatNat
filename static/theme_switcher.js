function initTheme() {
  const body = document.body;
  const theme = getActualTheme();
  body.className = theme;
}

function initMenu() {
    const menuToggle = document.querySelector("div#menuToggle input[type=checkbox]");
    const status = getMenuStatus();
    menuToggle.checked = status !== 'off';
    }

function getActualTheme() {
  return window.sessionStorage.getItem('theme') || 'bg-light light-colors';
}

function getMenuStatus() {
    return window.sessionStorage.getItem('menu') || 'off';
}

function setTheme(theme) {
  const body = document.body;
  body.className = theme;
  window.sessionStorage.setItem('theme', theme);
}

function setMenuStatus(status) {
    const menuToggle = document.querySelector("div#menuToggle input[type=checkbox]");
    menuToggle.checked = status !== 'off';
    window.sessionStorage.setItem('menu', status)
}

function menuButton() {
    const menuStatus = new Map();
    menuStatus.set('off', 'on');
    menuStatus.set('on', 'off');
    const currentStatus = getMenuStatus();
    setMenuStatus(menuStatus.get(currentStatus));
}

function initListeners() {
    let button = document.querySelector("div.theme-button a span");
    button.addEventListener('click', (event) => {
        const nextTheme = new Map();
        nextTheme.set('bg-light light-colors', 'bg-light dark-colors');
        nextTheme.set('bg-light dark-colors', 'bg-light light-colors');
        const actualTheme = getActualTheme();
        switchButtonText();
        setTheme(nextTheme.get(actualTheme));
    });
}

function switchButtonText() {
    let button = document.querySelector("div.theme-button a span");
    let oldText = button.textContent;
    if (oldText === 'light theme') {
        button.textContent = 'dark theme';
    } else {
        button.textContent = 'light theme';
    }

}
function init() {
  initTheme();
  initMenu();
  initListeners();
}

window.addEventListener('DOMContentLoaded', init);