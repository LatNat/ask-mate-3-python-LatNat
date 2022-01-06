function hide_relevant_buttons(user_id){
    var buttons = document.getElementsByClassName("buttons");
    for(let i=0;i<buttons.length;i++){
        if(buttons[i].getAttribute("data-user-id") === String(user_id)){
            buttons[i].style.visibility='visible';
        }
    }
}
