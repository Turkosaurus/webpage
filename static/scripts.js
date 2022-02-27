const beerDensity = 8.345 // Density of beer in pounds/gallon

const kegData = {
    "1/2 BBL": {
        "capacityGal":15.5,
        "weightEmpty":31,
        "nickname":"Half Barrel"
    },
    "1/3 BBL": {
        "capacityGal":13.2,
        "weightEmpty":27,
        "nickname":"Third Barrel"
    },
    "1/4 BBL": {
        "capacityGal":7.9,
        "weightEmpty":18,
        "nickname":"Quarter Barrel"
    },
    "1/6 BBL": {
        "capacityGal":5.2,
        "weightEmpty":14.5,
        "nickname":"Sixth Barrel"
    }
}

document.addEventListener('DOMContentLoaded', loadListeners, false);

let kegs = 0;

function loadListeners() {
    
    // Grab DOM Objects
    const kegName = document.getElementById("kegName");
    const weightBegin = document.getElementById("weightBegin");
    const weightEnd = document.getElementById('weightEnd');
    const kegSize = document.getElementById('kegSize');
    const kegSizeSmall = document.querySelector('small#kegSize')

    kegName.placeholder = `Keg Tap #${kegs + 1}`

    console.log(kegSizeSmall)

    // Load Keg Data into option list
    let kegDataEnum = 0;

    for(const keg in kegData) {
        // console.log(kegSize);
        const option = document.createElement('option');
        option.value = keg;
        option.text = `${keg} "${kegData[keg].nickname}" (${kegData[keg].capacityGal} gal)`;
        option.small = `${kegData[keg].nickname}`; // AKA or nicknames
        kegSize.add(option);
        
        console.log(option);

        console.log(`${keg}: ${kegData[keg].capacityGal}`);
        kegDataEnum += 1
    }
    console.log(`Loaded ${kegDataEnum} keg size options`);

    
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
        console.log("weight begin small")
        console.log(weightBegin)


        kegSizeSmall.innerHTML = `Min: ${min} pounds | Max: ${max} pounds`

        console.log(weightBeginSmall)


        for(let i = 0; i < weightBegin.labels.length; i++) {
            console.log(weightBegin.labels[i].textContent);
        }

        console.log(`label:${weightBegin.textContent}`);

        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/labels#browser_compatibility
        // https://stackoverflow.com/questions/285522/find-html-label-associated-with-a-given-input
        // document.querySelector("label[for=" + vHtmlInputElement.id + "]");

        weightEnd.min = min;
        weightEnd.max = max;
        
        // weightEnd.value = "";
        console.log(event.target.value)
    });

    const percentUsed = document.getElementById('percentUsed');
    const percentUsedSmall = document.querySelector("small#percentUsed")
    weightEnd.addEventListener('change', (event) => {
        // if zero, insert placeholder
        let size = kegSize.value
        let shell = kegData[size].weightEmpty
        result = (weightEnd.value - shell) /  (weightBegin.max - shell)
        
        result = Number.parseFloat(result * 100).toFixed(1);
        // console.log(result)
        // percentUsed.value = "foo"
        percentUsed.value = `${result}%`
        
        let gals = Number.parseFloat(result * (kegData[size].capacityGal / 100)).toFixed(2)
        percentUsedSmall.innerHTML = `Volume: ${gals} gallons | ${gals * 8} pints`
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
