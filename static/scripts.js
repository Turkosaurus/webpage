function difference (weightStart, weightEnd, kegType) {



    // Match kegType to kegWeights data to find base weight
    // pounds
    const kegWeights = {
        "1/2 BBL":69
    }

    let weightDelta = weightStart - weightEnd

    let results = {
        'weightUsed':weightDelta,
        'percentUsed':'foo',
        'ounces used':'3.14'
    }

    return results
}