import json
import unicodedata
from operator import itemgetter


###############################################################################
###                            Global Variables                             ###
###############################################################################


budget = 50000
flex = ["RB", "WR", "TE"]
benchedPlayers = []


###############################################################################
###                            ETL Functions                                ###
###############################################################################


def readDataFile(fileName):
    # parse json file from writeAllData.py into dictionaries
    with open(fileName, "r") as fantasyFile:
        raw = json.load(fantasyFile)
        data = [{unicodeToString(k): v for k, v in d.iteritems()} for d in raw]

    return data


def getTopNLineups(n = 1):
    global flex
    minRange, maxRange = 3, 10

    def topFlexLineup(data, m = 15):
        maxPoints, finalLineup = 0, []
        for pos in flex:
            lineup = getLineup(data, pos, m)
            points = getTotalPoints(lineup)
            if points > maxPoints:
                maxPoints, finalLineup = points, lineup
        return finalLineup

    def optimizeTop(lineup, topN, m):
        topN = sorted(topN, key = getTotalPoints)
        if lineup in topN:
            return topN
        elif len(topN) < m:
            topN.append(lineup)
        elif getTotalPoints(lineup) > getTotalPoints(topN[0]):
            topN.remove(topN[-1])
            topN.append(lineup)
        return sorted(topN, key = getTotalPoints)
    
    def iterPlayers(lineup, topN, m):
        global benchedPlayers
        size = len(lineup)
        for i in xrange(size):
            for j in xrange(size):
                benchedPlayers.append(lineup[(i + j) % size])
                for k in xrange(minRange, maxRange):
                    topN = optimizeTop(topFlexLineup(players, k), topN, m)
        return topN

    players = readDataFile("../data/bestDkPlayers.json")
    finalLineup = topFlexLineup(players)
    topN = [finalLineup]
    topN = iterPlayers(finalLineup, topN, n)

    for i in xrange(len(topN)):
        print writeLineup(topN[i])

    return topN


def getLineup(playerList, flexPos, m = 15):
    global benchedPlayers
    lineup, noGos = [], []

    def getWorstPlayer(lineup, safe = []):
        # find the least cost efficient player
        minDiff, minPlayer = -1, None
        for p in lineup:
            # TODO: define worst player in best way.
            pDiff = p["Points"] / p["Salary"]
            if (minDiff < 0 or pDiff < minDiff) and p not in safe:
                minDiff, minPlayer = pDiff, p
        return minPlayer

    def getTopNPlayers(playerList, pos, n):
        topPlayers = []
        for player in playerList:
            if player["Position"] == pos:
                topPlayers.append(player)
        return sorted(topPlayers, key=itemgetter("Points"), reverse=True)[:n]

    def getFirstLineup(flexPos):
        positions = { "QB": 1, "RB": 2, "WR": 3, "TE": 1, "DST": 1 }
        if flexPos in positions:
            positions[flexPos] += 1
        else:
            return [{"ERR": "invalid flex position"}]
        for pos, num in positions.iteritems():
            topPlayers = getTopNPlayers(playerList, pos, num)
            for p in topPlayers:
                lineup.append(p)
        return lineup

    def iterPlayers(lineup, flexPos, safeList, noGos, m = 15):
        worstPlayer = getWorstPlayer(lineup, safeList)
        noGos.append(worstPlayer)
        potential = []
        for np in getTopNPlayers(playerList, worstPlayer["Position"], m):
            if np not in lineup and np not in noGos:# and np not in benchedPlayers:
                potential.append(np)
        if len(potential) == 0:
            safeList.append(worstPlayer)
        else:
            lineup.remove(worstPlayer)
            lineup.append(sorted(potential, key = itemgetter("Points"))[-1])
        return [lineup, safeList, noGos]

    global budget
    lineup = getFirstLineup(flexPos)
    safeList = []
    while not isValidLineup(lineup, flexPos):
        iterStuff = iterPlayers(lineup, flexPos, safeList, noGos)
        lineup = iterStuff[0]
        safeList = iterStuff[1]
        noGos = iterStuff[2]

    return lineup


###############################################################################
###                            Utility Functions                            ###
###############################################################################


def isValidLineup(lineup, flexPos):
    global flex, budget

    def meetsBudget(lineup):
        valid = budget > getTotalSalary(lineup)
        return valid

    def rightPlayers(lineup, flexPos):
        def getPosCount(lineup):
            lineupPos = {}
            for player in lineup:
                pos = player["Position"]
                if pos in lineupPos:
                    lineupPos[pos] += 1
                else:
                    lineupPos[pos] = 1
            return lineupPos

        if flexPos not in flex:
            return False
        positions = { "QB": 1, "RB": 2, "WR": 3, "TE": 1, "DST": 1 }
        positions[flexPos] += 1
        lineupPos = getPosCount(lineup)
        for p, v in positions.iteritems():
            if p not in lineupPos or lineupPos[p] != v:
                return False
            # elif lineupPos[p] != v:
            #     return False
        return True

    return rightPlayers(lineup, flexPos) and meetsBudget(lineup)


def writeLineup(lineup):
    # write lineup in CSV format
    lines = "*" * 40 + "\nName,Position,Salary,ProjPoints\n"
    for player in lineup:
        lines += (player["Name"] + "," + 
                  player["Position"] + "," + 
                  "$" + str(player["Salary"]) + "," + 
                  str(player["Points"]) + "\n")
                  
    lines += ("\n" + "*" * 40 + "\n" + 
              "Budget Spent:  " + str(getTotalSalary(lineup)) + "\n" + 
                "Total Points:  " + str(getTotalPoints(lineup)) + "\n")

    return lines


def getTotalSalary(lineup):
    # returns totalbudget - sum(all player salaries in lineup)
    return sum([player["Salary"] for player in lineup])


def getTotalPoints(lineup):
    # finds the total projected points scored by a lineup
    return sum([player["Points"] for player in lineup])


def unicodeToString(text):
    try:
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore")
        return text
    except:
        return text

# print writeLineup(getLineup(readDataFile("../data/bestDkPlayers.json"), "RB", 5))
getTopNLineups(3)