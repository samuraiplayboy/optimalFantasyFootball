function readDataFile() {
	// parse json file from writeAllData.py into dictionaries
	var jsonData = JSON.parse()

    with open("assets/scripts/data/fantasyData.json", "r") as fantasyFile:
        var raw = json.load(fantasyFile)
        var data = [{unicodeToString(k): v for k, v in d.iteritems()} for d in raw]

    return data
}
