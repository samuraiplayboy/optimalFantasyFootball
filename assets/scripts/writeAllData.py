from scrapers.scrapeFantasyProsRankings import getFpRankingsData
from scrapers.scrapeFantasyProsProjections import getFpProjectionsData
from scrapers.scrapeEspnProjections import getEspnProjectionsData
from scrapers.scrapeRotoGrinderProjections import getRotoProjections
from collections import defaultdict
from operator import itemgetter
import os
from time import time
import json


###############################################################################
###                        Main Function (Call Me!)                         ###
###############################################################################


def main():
    data = runPipeline()

    positions = {
        "QB": {"Players": [], "AvgDkPoints": [], "AvgFdPoints": []},
        "RB": {"Players": [], "AvgDkPoints": [], "AvgFdPoints": []},
        "WR": {"Players": [], "AvgDkPoints": [], "AvgFdPoints": []},
        "TE": {"Players": [], "AvgDkPoints": [], "AvgFdPoints": []},
        "DST": {"Players": [], "AvgDkPoints": [], "AvgFdPoints": []},
        "K": {"Players": [], "AvgDkPoints": [], "AvgFdPoints": []},
    }

    reqKey = "Position"
    refinedData = [d for d in data if reqKey in d.keys()]

    for player in refinedData:
        if player["Position"] in positions:
            positions[player["Position"]]["Players"].append(player)

        allDkPoints, allFdPoints = [], []
        try:
            allDkPoints.append(player["rotoDkPoints"])
            allFdPoints.append(player["rotoFdPoints"])
        except:
            print "No Rotogrinder Points for", player["Name"]

        try:
            player["fpDkPoints"] = calcDkPoints(player, "fpProjections")
            allDkPoints.append(player["fpDkPoints"])

            player["fpFdPoints"] = calcFdPoints(player, "fpProjections")
            allFdPoints.append(player["fpFdPoints"])
        except:
            print "No FantasyPros Stat Projections for", player["Name"]

        try:
            player["espnDkPoints"] = calcDkPoints(player, "espnProjections")
            allDkPoints.append(player["espnDkPoints"])

            player["espnFdPoints"] = calcFdPoints(player, "espnProjections")
            allFdPoints.append(player["espnFdPoints"])
        except:
            print "No ESPN Projections for", player["Name"]

        try:
            player["AvgDkPoints"] = sum(allDkPoints) / len(allDkPoints)
            player["AvgFdPoints"] = sum(allFdPoints) / len(allFdPoints)
        except:
            print player["Name"], "has no points!"
            player["AvgDkPoints"], player["AvgFdPoints"] = 0, 0

        try:
            player["DkPointsPerDollar"] = player["AvgDkPoints"] / player["dkSalary"]
            player["FdPointsPerDollar"] = player["AvgFdPoints"] / player["fdSalary"]
        except:
            player["DkPointsPerDollar"], player["FdPointsPerDollar"] = 0, 0
        positions[player["Position"]]["AvgDkPoints"].append(player["DkPointsPerDollar"])
        positions[player["Position"]]["AvgFdPoints"].append(player["FdPointsPerDollar"])

    for player in refinedData:
        calcExpectation(player, positions)

    writeData(refinedData, "data/fantasyData.json")
    writeFinalFiles(refinedData)

    return refinedData


###############################################################################
###                            Data ETL Functions                           ###
###############################################################################

# Pipeline
def runPipeline():
    rawDataFile = "data/rawData.json"
    allData = []
    if os.path.isfile(rawDataFile):
        fileAge = time() - os.path.getctime(rawDataFile)
    else:
        fileAge = 4000

    # if its been scraped in the last hour, just read the file.
    if fileAge < 60 * 60:
        with open(rawDataFile) as f:
            allData = json.load(f)
    else:
        allData = joinData(scrapeData())
        writeData(allData, rawDataFile)

    return allData

# Extract
def scrapeData():
    roto = getRotoProjections()
    espn = getEspnProjectionsData()
    ranks = getFpRankingsData()
    fp = getFpProjectionsData()

    data = [ranks, roto, espn, fp]

    return data

# Transform
def joinData(listOfPlayerLists):
    d = defaultdict(dict)
    for dataset in listOfPlayerLists:
        for player in dataset:
            player["Name"] = player["Name"].lower()
            d[player["Name"]].update(player)

    return d.values()


def reducePlayer(player, site = "Dk"):
    site = site.lower()
    sPlayer = {"Name": player["Name"],
               "Position": player["Position"]}
    if site == "dk":
        sPlayer["Points"] = player["AvgDkPoints"]
        sPlayer["Salary"] = player["dkSalary"]
        sPlayer["ExpPoints"] = player["expDkPoints"]
    elif site == "fd":
        sPlayer["Points"] = player["AvgFdPoints"]
        sPlayer["Salary"] = player["fdSalary"]
        sPlayer["ExpPoints"] = player["expFdPoints"]
    else:
        sPlayer = sPlayer(player)
    sPlayer["PerDiff"] = abs(sPlayer["Points"] - sPlayer["ExpPoints"]) / sPlayer["Points"]

    return sPlayer


def calcExpectation(player, positions):
    dk = positions[player["Position"]]["AvgDkPoints"]
    fd = positions[player["Position"]]["AvgFdPoints"]
    avgDkPosPpd = sum(dk) / len(dk)
    avgFdPosPpd = sum(fd) / len(fd)
    player["expDkPoints"] = player["dkSalary"] * (avgDkPosPpd)
    player["expFdPoints"] = player["fdSalary"] * (avgFdPosPpd)

# Load
def writeData(data, fileName):
    with open(fileName, "w") as fantasyFile:
        json.dump(data, fantasyFile, indent = 4)
        print "JSON file completed: ", fileName
        print len(data), "Total Players"


def writeFinalFiles(data):
    sites = ["Fd", "Dk"]
    for site in sites:
        avgKey = "Avg" + site + "Points"
        expKey = "exp" + site + "Points"
        fileName = "data/best" + site + "Players.json"
        bestplayers = []
        for d in data:
            salary = site.lower() + "Salary"
            if d[expKey] <= d[avgKey] and d[salary] > 0:
                bestplayers.append(reducePlayer(d, site))
        writeData(bestplayers, fileName)


###############################################################################
###                        Fantasy Scoring Functions                        ###
###############################################################################


def calcDkPoints(player, projectionKey):
    points, projections = 0, player[projectionKey]
    # Passing points
    try:
        points += projections["PassTds"] * 4.0
        points += projections["PassYards"] * .04
        if projections["PassYards"] >= 300:
            points += 3.0
        points += projections["PassInts"] * -1.0
    except:
        pass
    # Rushing Points
    try:
        points += projections["RushYards"] * 0.1
        points += projections["RushTds"] * 6.0
        if projections["RushYards"] >= 100:
            points += 3.0
    except:
        pass
    # Receiving Points
    try:
        points += projections["RecYards"] * 0.1
        points += projections["Recs"] * 1.0
        points += projections["RecTds"] * 6.0
        if projections["RecYards"] >= 100:
            points += 3.0
    except:
        pass
    # Miscellanious
    try:
        points += projections["Fumbles"] * -1.0
    except:
        pass

    return points


def calcFdPoints(player, projectionKey):
    points, projections = 0, player[projectionKey]
    # Passing points
    try:
        points += projections["PassTds"] * 4.0
        points += projections["PassYards"] * .04
        points += projections["PassInts"] * -1.0
    except:
        pass
    # Rushing Points
    try:
        points += projections["RushYards"] * 0.1
        points += projections["RushTds"] * 6.0
    except:
        pass
    # Receiving Points
    try:
        points += projections["RecYards"] * 0.1
        points += projections["Recs"] * 0.5
        points += projections["RecTds"] * 6.0
    except:
        pass
    # Miscellanious
    try:
        points += projections["Fumbles"] * -2.0
    except:
        pass

    return points


###############################################################################
###                             Utility Functions                           ###
###############################################################################





main()