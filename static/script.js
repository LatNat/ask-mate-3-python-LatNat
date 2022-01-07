window.onload = (event) => {
    var modal = document.getElementById("myModal");
    var popup = sessionStorage.getItem("popup");
      if(popup !== "False") {
        modal.style.display = "block";
      }
    function search() {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const searched = urlParams.get('search')
        if (searched !== "") {
            let text = document.getElementById("text").innerHTML;
            let re = new RegExp(searched, "ig"); // search for all instances
            let newText = text.replace(re, `<span class="highlight"><b>${searched.toUpperCase()}</b></span>`);
            document.getElementById("text").innerHTML = newText;
        }


    }

    function main() {
        if (document.getElementById("search-bool")) {
            search()
        }
    }

    main()
}

function capitalize(str) {
  const lower = str.toLowerCase();
  return str.charAt(0).toUpperCase() + lower.slice(1);
}

