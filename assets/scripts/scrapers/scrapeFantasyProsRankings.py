import requests
from lxml import html
from time import sleep
from random import randint


def getFpRankingsData():
    players = []
    posUrls = ["qb", "ppr-rb", "ppr-wr", "ppr-te" "k", "dst"]
    for posUrl in posUrls:
        url = "http://www.fantasypros.com/nfl/rankings/%s.php" % posUrl
        sleep(randint(2, 5))
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
            position = getPosFromPosUrl(posUrl)
            ecr      = getFpPlayerEcr(tree)
            names    = getFpPlayerName(tree)
            meanrank = getFpPlayerAvgRank(tree)
            stdev    = getFpPlayerStdev(tree)
            # opps     = getFpPlayerOpp(tree)
        except:
            print "Error parsing:", url
            continue

        for i in xrange(len(names)):
            player = {}
            player['Name']      = names[i]
            player['Rank']      = ecr[i]
            player['MeanRank']  = meanrank[i]
            player['RankStdev'] = stdev[i]
            player['Position']  = position
            # player['Opponent']  = opps[i]

            players.append(player)
            print "Scraped FantasyPros Rankings for:", player["Name"]

    return players

def getPosFromPosUrl(posUrl):
    if "-" in posUrl:
        pos = (posUrl.split("-")[-1]).upper()
    else:
        pos = posUrl.upper()

    return pos


def getFpPlayerEcr(tree):
    allEcrs = tree.xpath('//*[@id="data"]//tr/td[1]/text()')

    return [float(e) for e in allEcrs]


def getFpPlayerName(tree):
    allNames = tree.xpath('//*[@id="data"]//tr/td[2]/a/text()')

    return allNames


def getFpPlayerOpp(tree):
    rawOpps = tree.xpath('//*[@id="data"]//tr/td[3]/text()')

    return [rawOpp.split(" ")[-1] for rawOpp in rawOpps]


def getFpPlayerBestRank(tree):
    allBests = tree.xpath('//*[@id="data"]//tr/td[4]/text()')

    return [float(b) for b in allBests]


def getFpPlayerWorstRank(tree):
    allWorstRanks = tree.xpath('//*[@id="data"]//tr/td[5]/text()')

    return [float(w) for w in allWorstRanks]


def getFpPlayerAvgRank(tree):
    allAvgs = tree.xpath('//*[@id="data"]//tr/td[6]/text()')

    return [float(a) for a in allAvgs]


def getFpPlayerStdev(tree):
    allStdevs = tree.xpath('//*[@id="data"]//tr/td[7]/text()')

    return [float(s) for s in allStdevs]
