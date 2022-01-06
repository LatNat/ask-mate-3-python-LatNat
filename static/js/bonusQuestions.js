// you receive an array of objects which you must sort in the by the key "sortField" in the "sortDirection"
function getSortedItems(items, sortField, sortDirection) {
    console.log(items)
    console.log(sortField)
    console.log(sortDirection)

    // === SAMPLE CODE ===
    // if you have not changed the original html uncomment the code below to have an idea of the
    // effect this function has on the table
    //
    if (sortDirection === "asc") {
        const firstItem = items.shift()
        if (firstItem) {
            items.push(firstItem)
        }
    } else {
        const lastItem = items.pop()
        if (lastItem) {
            items.push(lastItem)
        }
    }

    return items
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
    console.log("toggle theme")
}

function increaseFont() {
    console.log("increaseFont")
}

function decreaseFont() {
    console.log("decreaseFont")
}