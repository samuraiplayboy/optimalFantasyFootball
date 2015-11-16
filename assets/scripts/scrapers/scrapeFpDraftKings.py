import requests
from lxml import html
from time import sleep
from random import randint


def getFpDkData():
    sleep(randint(2, 5))
    url = "http://www.fantasypros.com/nfl/draftkings-lineup-optimizer.php"
    try:
        response = requests.get(url)
        tree = html.fromstring(response.text)
    except:
        try:
            response = requests.get(url)
            tree = html.fromstring(response.text)
        except:
            print "Couldn't scrape:", url
            return []

    names         = getDkName(tree)
    points        = getPlayerPoints(tree)
    salaries      = getPlayerSalaries(tree)
    positions     = getPlayerPosition(tree)
    opponents     = getPlayerOpponent(tree)

    players = []
    for i in xrange(min(len(names), len(points), len(salaries))):
        player = {}
        player["Name"]         = names[i]
        player["Position"]     = positions[i][0]
        player["PositionRank"] = positions[i][-1]
        player["dkPoints"]     = points[i]
        player["dkSalary"]     = salaries[i]
        # player["Opponent"]     = opponents[i]
        if player["Position"] != "NR":
        	players.append(player)
        	print "Scraped Fantasy Pros for DK Points/Salary for:", player["Name"]

    return players


def getPlayerPosition(tree):
    allPositions = tree.xpath('//*[@id="player-pool"]//tr/td[2]/text()')

    return [[p, 0] if p == "NR" else p.split(" #") for p in allPositions]


def getPlayerOpponent(tree):
    allOpponents = tree.xpath('//*[@id="player-pool"]//tr/td[3]/span/text()')

    return allOpponents


def getPlayerSalaries(tree):
    rawSalaries = tree.xpath('//*[@id="player-pool"]//tr/td[6]/text()')

    return [int(s[1:].replace(",", "")) for s in rawSalaries]


def getPlayerPoints(tree):
    rawPoints = tree.xpath('//*[@id="player-pool"]//tr/td[5]/text()')

    return [float(p) for p in rawPoints]


def getDkName(tree):
    rawNames = tree.xpath('//*[@id="player-pool"]//tr/td[1]/text()')

    return [n.split(",")[0] for n in rawNames]

