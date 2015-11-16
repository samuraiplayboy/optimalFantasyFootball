import requests
from lxml import html
from time import sleep
from random import randint


def getEspnProjectionsData():
    players = []
    base = "http://games.espn.go.com/ffl/tools/projections?"
    urls = [base + "&startIndex=0%s" % str(s) for s in xrange(0, 401, 40)]

    for url in urls:
        sleep(randint(1, 5))
        try:
            response = requests.get(url, timeout = 10)
            tree = html.fromstring(response.text)
        except:
            try:
                response = requests.get(url, timeout = 10)
                tree = html.fromstring(response.text)
            except:
                print "Couldn't scrape:", url

        try:
            names = getEspnName(tree)
            # points = getEspnPoints(tree)
            stats = [getEspnPassStats(tree),
                     getEspnRushStats(tree), 
                     getEspnRecStats(tree)]
        except:
            continue
        
        for i in xrange(len(names)):
            player = {"espnProjections": {}}
            player["Name"] = names[i]
            for stat in stats:
                for name, val in stat.iteritems():
                    player["espnProjections"][name] = val[i]

            players.append(player)
            print "Scraped ESPN Projections for:", player["Name"]

    return players


def getEspnName(tree):
    rawNames = tree.xpath('//*[@id="playertable_0"]//tr/td[1]/a/text()')[1:]

    return rawNames


def getEspnPoints(tree):
    rawPoints = tree.xpath('//*[@id="playertable_0"]//tr/td[14]/text()')

    return [float(p) for p in rawPoints]


def getEspnPassStats(tree):
    passStats = {}

    cOverA = tree.xpath('//*[@id="playertable_0"]//tr/td[4]/text()')[1:]
    cpa = [(s[0], s[-1]) for s in (c.split("/") for c in cOverA)]
    passStats["PassComp"] = [float(c[0]) for c in cpa]
    passStats["PassAtts"] = [float(a[-1]) for a in cpa]

    rawYards = tree.xpath('//*[@id="playertable_0"]//tr/td[5]/text()')
    passStats["PassYards"] = [0 if y == "--" else float(y) for y in  rawYards]

    rawPassTds = tree.xpath('//*[@id="playertable_0"]//tr/td[6]/text()')
    passStats["PassTds"] = [0 if y == "--" else float(y) for y in  rawPassTds]

    rawPassInts = tree.xpath('//*[@id="playertable_0"]//tr/td[7]/text()')
    passStats["PassInts"] = [0 if y == "--" else float(y) for y in  rawPassInts]

    return passStats


def getEspnRushStats(tree):
    rushStats = {}

    rawRushAtts = tree.xpath('//*[@id="playertable_0"]//tr/td[8]/text()')
    rushStats["RushAtts"] = [0 if y == "--" else float(y) for y in  rawRushAtts]

    rawRushYards = tree.xpath('//*[@id="playertable_0"]//tr/td[9]/text()')
    rushStats["RushYards"] = [0 if y == "--" else float(y) for y in  rawRushYards]

    rawRushTds = tree.xpath('//*[@id="playertable_0"]//tr/td[10]/text()')
    rushStats["RushTds"] = [0 if y == "--" else float(y) for y in  rawRushTds]

    return rushStats


def getEspnRecStats(tree):
    recStats = {}

    rawRecs = tree.xpath('//*[@id="playertable_0"]//tr/td[11]/text()')
    recStats["Recs"] = [0 if y == "--" else float(y) for y in  rawRecs]

    rawRecYards = tree.xpath('//*[@id="playertable_0"]//tr/td[12]/text()')
    recStats["RecYards"] = [0 if y == "--" else float(y) for y in rawRecYards]

    rawRecTds = tree.xpath('//*[@id="playertable_0"]//tr/td[13]/text()')
    recStats["RecTds"] = [0 if y == "--" else float(y) for y in rawRecTds]

    return recStats

