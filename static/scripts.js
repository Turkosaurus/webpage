const beerDensity = 8.345 // Density of beer in pounds/gallon

const kegData = {
    "1/2 BBL": {
        "capacityGal":15.5,
        "weightEmpty":31
    },
    "1/3 BBL": {
        "capacityGal":13.2,
        "weightEmpty":27
    },
    "1/4 BBL": {
        "capacityGal":7.9,
        "weightEmpty":18
    },
    "1/6 BBL": {
        "capacityGal":5.2,
        "weightEmpty":14.5
    }
}

document.addEventListener('DOMContentLoaded', loadListeners, false);
// document.addEventListener('DOMContentLoaded', loadData, false);

function loadListeners() {
    console.log("Hello!");

    const weightBegin = document.getElementById("weightBegin");
    const weightEnd = document.getElementById('weightEnd');
    const kegSize = document.getElementById('kegSize');
    
    kegSize.addEventListener('change', (event) => {
        let size = event.target.value;
        let min = kegData[size].weightEmpty;
        let shell = kegData[size].weightEmpty
        let max = (kegData[size].capacityGal * beerDensity) + shell;
        max = Number.parseFloat(max).toFixed(2);
        console.log(max);
        
        weightBegin.min = min;
        weightBegin.max = max;
        weightBegin.value = max;

        weightEnd.min = min;
        weightEnd.max = max;
        
        // weightEnd.value = "";
        console.log(event.target.value)
    });

    const percentUsed = document.getElementById('percentUsed');
    weightEnd.addEventListener('change', (event) => {
        // if zero, insert placeholder
        let size = kegSize.value
        let shell = kegData[size].weightEmpty
        result = (weightEnd.value - shell) /  (weightBegin.max - shell)
        result = Number.parseFloat(result * 100).toFixed(2);
        // console.log(result)
        // percentUsed.value = "foo"
        percentUsed.value = `${result}%`
    });
}

function updatePercent() {

}


function updateKegMinMax() {
    console.log("HOLY HELL WE MADE IT");
    alert("we made it");
}



// event listener for keg size, set min
    // starting weight is maximum possible (or TODO the saved, cached last value for that beer)
    // populate minimum and maximum starting weight and ending weights

function nextKeg() {
    // add a row to the results
    // clear the form

}


// PSEUDOCODE

// Match kegType to kegWeights data to find base weight

// get keg size

function difference (kegType, weightGross) {

    // match kegType to kegData
    let capacityGal = kegData[kegType]['capacityGal'];
    let weightEmpty = kegData[kegType]['weightEmpty'];

    // Calculate usage
    let weightMax = capacityGal * beerDensity; // Weight of beer within a full keg
    let weightLiquid = weightGross - weightEmpty; // Subtract shell weight

    // Beer remaining
    let percent = weightLiquid / weightMax;
    let gallons = weightLiquid / 8.345;
    
    let results = {
        'percent':percent,
        'galons':gallons
    };

    return results;
}
