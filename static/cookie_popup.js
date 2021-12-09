var modal = document.getElementById("myModal");
var btn = document.getElementById("myBtn");
var span = document.getElementsByClassName("close")[0];

btn.onclick = function () {
  sessionStorage.setItem("popup", "False");
  modal.style.display = "none";
}

span.onclick = function() {
  modal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target === modal) {
    modal.style.display = "none";
  }
}

window.onload = (event) => {
  var popup = sessionStorage.getItem("popup");
  if(popup != "False") {
    modal.style.display = "block";
  }
};
