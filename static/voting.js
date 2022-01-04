function change_scrollbar() {
    var documentScroll = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    new_location = window.sessionStorage.getItem("location");
    if(new_location){
        console.log(new_location);
        window.scrollTo(0, parseInt(new_location));
        sessionStorage.removeItem("location");
    }
}

function store_scrollbar() {
    var documentScroll = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    new_location = documentScroll;
    window.sessionStorage.setItem("location", new_location);
}

window.onload = (event) => {
    change_scrollbar();
}
