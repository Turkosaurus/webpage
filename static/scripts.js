const beerDensity = 8.345; // Density of beer in pounds/gallon
const galPerLiter = 3.78541;
// let unit = "imperial";
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

// Active keg's form data, globally available for processing and validation
const tapData = {
    "kegNumber":1,
    "name":'',
    "size":'',
    "weightBegin":'',
    "weightEnd":'',
    "usedPercent":'',
    "usedVolume":''
}

// Setep result arrays for download or csv export
const inventoryResults = []
let headerRow = []
for(i in tapData) {
    headerRow.push(i);
}
inventoryResults.push(headerRow);

document.addEventListener('DOMContentLoaded', initializePage, false);

function initializePage() {
    
    // Grab DOM Objects
    const kegName = document.getElementById("kegName");
    const kegSize = document.getElementById('kegSize');
    const weightBegin = document.getElementById("weightBegin");
    const weightEnd = document.getElementById('weightEnd');
    const nextKeg = document.getElementById('nextKeg');
    const print = document.getElementById('print');
    const download = document.getElementById('download');
    const reset = document.getElementById('reset');

    // Load Keg Data into option list
    let kegDataEnum = 0;
    for(const keg in kegData) {
        // console.log(kegSize);
        const option = document.createElement('option');
        option.value = keg;
        option.text = `${keg} "${kegData[keg].nickname}" (${kegData[keg].capacityGal} gal)`;
        option.small = `${kegData[keg].nickname}`; // AKA or nicknames
        kegSize.add(option);        
        // console.log(option);
        // console.log(`${keg}: ${kegData[keg].capacityGal}`);
        kegDataEnum += 1
    }
    resetKegForm(kegName, weightBegin, weightEnd);
    console.log(`Loaded ${kegDataEnum} keg size options`);

    // Allow eventlisteners to be passed objects
    // https://ultimatecourses.com/blog/avoiding-anonymous-javascript-functions

    kegName.addEventListener('change', function () {
        tapData.name = kegName.value;
    }, false);

    kegSize.addEventListener('change', function () {
        updateKegSize(kegSize, weightBegin, weightEnd);
    }, false);

    weightBegin.addEventListener('change', function () {
        calculatePercent(kegSize, weightBegin, weightEnd);
    }, false);

    weightEnd.addEventListener('change', function () {
        calculatePercent(kegSize, weightBegin, weightEnd);
    }, false);

    nextKeg.addEventListener('click', function() {
        nextKegUpdate(kegName, kegSize, weightBegin, weightEnd);
    }, false);

    print.addEventListener('click', function() {
        printResults();
    })

    download.addEventListener('click', function() {
        downloadResults();
    })

    reset.addEventListener('click', function() {
        resetKegForm(kegName, weightBegin, weightEnd);
    })
}

function resetKegForm(kegName, weightBegin, weightEnd) {

    const usedPercent = document.getElementById('usedPercent');
    const usedVolume = document.getElementById('usedVolume');

    const weightBeginLabel = document.querySelector("small#weightBegin");
    weightBeginLabel.innerHTML = `(max: - lbs.)`
 
    const weightEndLabel = document.querySelector("small#weightEnd");
    weightEndLabel.innerHTML = `(min: - lbs.)`

    kegName.value = '';
    kegName.placeholder = tapData.name = `Keg Tap ${tapData.kegNumber}`;

    document.getElementById("kegSize").selectedIndex = "0";
    weightBegin.value = '';
    weightEnd.value = '';
    tapData.size = '';
    tapData.weightBegin = '';
    tapData.weightEnd = '';
    tapData.usedPercent = '';
    tapData.usedVolume = '';
    usedPercent.value = "";
    usedVolume.value = "";
}

function updateKegSize(kegSize, weightBegin, weightEnd) {
    let size = tapData.size = kegSize.value; //test
    let min = kegData[size].weightEmpty;
    let max = (kegData[size].capacityGal * beerDensity) + min;    
    max = Number.parseFloat(max).toFixed(0);
    
    // kegSizeSmall.innerHTML = `Min-Max: ${min}-${max} pounds`
    weightBegin.min = min;
    weightBegin.max = max;

    const weightBeginLabel = document.querySelector("small#weightBegin");
    weightBeginLabel.innerHTML = `(max: ${max} lbs.)`
 
    const weightEndLabel = document.querySelector("small#weightEnd");
    weightEndLabel.innerHTML = `(min: ${min} lbs.)`

    weightBegin.value = max;
    // weightEnd.value = min; // TODO remove after testing

    weightEnd.min = min;
    weightEnd.max = max;
    
    calculatePercent(kegSize, weightBegin, weightEnd);
}

function calculatePercent(kegSize, weightBegin, weightEnd) {

    // console.log("calculatePercent()");
    const usedPercent = document.getElementById('usedPercent');
    const usedVolume = document.getElementById('usedVolume');
     
    if (weightEnd.value > 0 && kegSize.value != '') {

        let size = kegSize.value;
        let min = kegData[size].weightEmpty;
        let max = (kegData[size].capacityGal * beerDensity) + min;
        
        startPercent = (weightBegin.value - min) / (max - min)
        endPercent = (weightEnd.value - min) / (max - min)

        resultPercent = startPercent - endPercent
        resultPercent = Number.parseFloat(resultPercent).toFixed(3);

        resultVolume = resultPercent * kegData[size].capacityGal
        resultVolume = Number.parseFloat(resultVolume).toFixed(1)    

        resultPercent = Number.parseFloat(resultPercent * 100).toFixed(1);
        usedPercent.value = `${resultPercent} %`;
        usedVolume.value = `${resultVolume} gal.`;

        tapData.weightBegin = weightBegin.value;
        tapData.weightEnd = weightEnd.value;
        tapData.usedPercent = resultPercent;
        tapData.usedVolume = resultVolume;
    } else {
        tapData.weightBegin = ''
        tapData.weightEnd = ''
        tapData.usedPercent = ''
        tapData.usedVolume = ''
        usedPercent.value = "-";
        usedVolume.value = "-";
    }
}

function nextKegUpdate(kegName, kegSize, weightBegin, weightEnd) {

    if(tapData.size === '') {
        alert("Size required.");
        return
    }

    if(parseInt(tapData.weightBegin) <= kegData[tapData.size].weightEmpty) {
        alert(`Beginning weight must be at least ${kegData[tapData.size].weightEmpty} lbs.`);
        return
    }

    // TODO add more validation and errors here
    if(tapData.weightEnd === '') {
        alert("Ending weight required.");
        return
    }

    const inventory = document.getElementById("inventory");
    let row = inventory.insertRow(inventory.rows.length);
    let i = 0;
    let newRow = []
    for(tap in tapData) {
        let cell = row.insertCell(i);
        cell.innerHTML = tapData[tap];
        newRow.push(tapData[tap])
        i++;
    }
    inventoryResults.push(newRow)
    console.log(inventoryResults)

    tapData.kegNumber += 1;
    // document.getElementById("kegForm").reset();
    resetKegForm(kegName, weightBegin, weightEnd);
    kegSize.value = '';
    weightBegin.value = '';
    weightEnd.value = '';
    calculatePercent(kegSize, weightBegin, weightEnd);

    // add a row to the results
    // clear the form
    console.log(tapData);
}

function printResults() {
    document.getElementById("time").innerHTML = `Printed on ${Date()}`
    print();
}

function downloadResults() {
    // https://stackoverflow.com/questions/14964035/how-to-export-javascript-array-info-to-csv-on-client-side
    let csvContent = "data:text/csv;charset=utf-8,";

    inventoryResults.forEach(function(rowArray) {
        let row = rowArray.join(",");
        csvContent += row + "\r\n";
    });

    var encodedUri = encodeURI(csvContent);
    window.open(encodedUri);
    console.log(inventoryResults)
}