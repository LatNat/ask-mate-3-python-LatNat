function popUp(){
setTimeout(function(){
       window.alert("Username or Email already in use, please try another!");
   }, 100);
}
window.addEventListener("load", (event) => {
    popUp();
});
