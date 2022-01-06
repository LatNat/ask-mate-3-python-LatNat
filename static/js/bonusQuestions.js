// you receive an array of objects which you must sort in the by the key "sortField" in the "sortDirection"
function getSortedItems(items, sortField, sortDirection) {
    let sorting;

    if (sortDirection === "asc") {
        sorting = 1;
    } else {
        sorting = -1;
    }

    return items.sort(function(a, b){
        if(+a[sortField]){
            return +a[sortField]*sorting - +b[sortField]*sorting;
        }
        if(a[sortField] > b[sortField]){
            return 1*sorting;
        }
        else if(a[sortField] < b[sortField]){
            return -1*sorting;
        }
        return 0;
    });
}

// you receive an array of objects which you must filter by all it's keys to have a value matching "filterValue"
function getFilteredItems(items, filterValue) {
    let columnName = "Title";

    if(filterValue.includes(":")){
        if(Object.keys(items[0]).includes(filterValue.split(":")[0])){
            columnName = filterValue.split(":")[0];
        }
        filterValue = filterValue.split(":")[1];
    }

    let filteredItems;
    if(columnName[0] === "!"){
        filteredItems = items.filter(question => !question[columnName.slice(1)].includes(filterValue));
    }
    else if(filterValue[0] === "!"){
        filteredItems = items.filter(question => !question[columnName].includes(filterValue.slice(1)));
    }
    else {
        filteredItems = items.filter(question => question[columnName].includes(filterValue));
    }

    return filteredItems;
}

function toggleTheme() {
    if(document.body.style.color !== "rgb(255, 255, 255)"){
        document.body.style.background = "#000000"
        document.body.style.color = "#FFFFFF"
    }
    else{
        console.log("hello")
        document.body.style.background = "#FFFFFF"
        document.body.style.color = "#000000"
    }
}

function increaseFont() {
    let tdElements = document.getElementsByTagName("td");
    for(let i=0;i<tdElements.length;i++){
        if(parseInt(tdElements[i].style.fontSize)){
            tdElements[i].style.fontSize = parseInt(tdElements[i].style.fontSize)+1 + "px";
        }
        else {
            tdElements[i].style.fontSize = "17px";
        }
        console.log(tdElements[i].style.fontSize)
    }
}

function decreaseFont() {
    let tdElements = document.getElementsByTagName("td");
    for(let i=0;i<tdElements.length;i++){
        if(parseInt(tdElements[i].style.fontSize)){
            tdElements[i].style.fontSize = parseInt(tdElements[i].style.fontSize)-1 + "px";
        }
        else {
            tdElements[i].style.fontSize = "15px";
        }
    }
}