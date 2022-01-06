function switchTheme() {
    let linkedFiles = document.getElementsByTagName("link");
    let head = document.querySelector("head");
    let button = document.querySelector("div.theme-button a span");
    let oldScheme = button.textContent;
    console.log(oldScheme);
    let newScheme;
    if (oldScheme.includes('light')) { newScheme = 'light'} else { newScheme = 'dark'}
    let newTheme = '<link rel="stylesheet" type="text/css" href="/static/' + newScheme + '_theme_colors.css">'
    console.log(head);
    for (let link of linkedFiles) {
        console.log(link);
        if (link.href.includes("light")) {
            link.remove();
            head.insertAdjacentHTML("afterbegin", newTheme);
            button.textContent = "light theme";
        } else if (link.href.includes("dark")) {
            link.remove();
            head.insertAdjacentHTML("afterbegin", newTheme);
            button.textContent = "dark theme";
        }
    }
}