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


// PSEUDOCODE

// Match kegType to kegWeights data to find base weight

// get keg size
    // populate minimum and maximum starting weight and ending weight

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
