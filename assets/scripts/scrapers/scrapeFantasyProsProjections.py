import requests
from lxml import html
from time import sleep
from random import randint


def getFpProjectionsData():
    baseUrl = "http://www.fantasypros.com/nfl/projections/"
    posUrls = ["qb", "rb", "wr", "te", "k"]
    allPlayers = []
    for pos in posUrls:
        url = baseUrl + pos + ".php"
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
            if pos == "qb":
                players = getQbs(tree)
            elif pos == "rb":
                players = getRbs(tree)
            elif pos == "wr":
                players = getWrs(tree)
            elif pos == "te":
                players = getTes(tree)
            elif pos == "k":
                players = getKs(tree)
            else:
                print "unrecognized position URL:", pos
        except:
            continue

        for player in players:
            allPlayers.append(player)
            print "Scraped FantasyPros Projections for:", player["Name"]

    return allPlayers


def getQbs(tree):
    
    names     = tree.xpath('//*[@id="data"]//tr/td[1]/a/text()')
    passAtts  = tree.xpath('//*[@id="data"]//tr/td[2]/text()')
    passComp  = tree.xpath('//*[@id="data"]//tr/td[3]/text()')
    passYards = tree.xpath('//*[@id="data"]//tr/td[4]/text()')
    passTds   = tree.xpath('//*[@id="data"]//tr/td[5]/text()')
    passInts  = tree.xpath('//*[@id="data"]//tr/td[6]/text()')
    rushAtts  = tree.xpath('//*[@id="data"]//tr/td[7]/text()')
    rushYards = tree.xpath('//*[@id="data"]//tr/td[8]/text()')
    rushTds   = tree.xpath('//*[@id="data"]//tr/td[9]/text()')
    fumbles   = tree.xpath('//*[@id="data"]//tr/td[10]/text()')

    qbs = []
    for i in xrange(len(names)):
        qb = {"fpProjections":{}}
        qb["Name"] = names[i]
        qb["fpProjections"]["PassAtts"]  = float(passAtts[i])
        qb["fpProjections"]["PassComp"]  = float(passComp[i])
        qb["fpProjections"]["PassYards"] = float(passYards[i])
        qb["fpProjections"]["PassTds"]   = float(passTds[i])
        qb["fpProjections"]["PassInts"]  = float(passInts[i])
        qb["fpProjections"]["RushAtts"]  = float(rushAtts[i])
        qb["fpProjections"]["RushYards"] = float(rushYards[i])
        qb["fpProjections"]["RushTds"]   = float(rushTds[i])
        qb["fpProjections"]["Fumbles"]   = float(fumbles[i])
        qbs.append(qb)

    return qbs


def getRbs(tree):
    names     = tree.xpath('//*[@id="data"]//tr/td[1]/a/text()')
    rushAtts  = tree.xpath('//*[@id="data"]//tr/td[2]/text()')
    rushYards = tree.xpath('//*[@id="data"]//tr/td[3]/text()')
    rushTds   = tree.xpath('//*[@id="data"]//tr/td[4]/text()')
    recs      = tree.xpath('//*[@id="data"]//tr/td[5]/text()')
    recYards  = tree.xpath('//*[@id="data"]//tr/td[6]/text()')
    recTds    = tree.xpath('//*[@id="data"]//tr/td[7]/text()')
    fumbles   = tree.xpath('//*[@id="data"]//tr/td[8]/text()')

    rbs = []
    for i in xrange(len(names)):
        rb = {"fpProjections": {}}
        rb["Name"] = names[i]
        rb["fpProjections"]["RushAtts"]  = float(rushAtts[i])
        rb["fpProjections"]["RushYards"] = float(rushYards[i])
        rb["fpProjections"]["RushTds"]   = float(rushTds[i])
        rb["fpProjections"]["Recs"]      = float(recs[i])
        rb["fpProjections"]["RecYards"]  = float(recYards[i])
        rb["fpProjections"]["RecTds"]    = float(recTds[i])
        rb["fpProjections"]["Fumbles"]   = float(fumbles[i])
        rbs.append(rb)

    return rbs

def getWrs(tree):
    names     = tree.xpath('//*[@id="data"]//tr/td[1]/a/text()')    
    rushAtts  = tree.xpath('//*[@id="data"]//tr/td[2]/text()')
    rushYards = tree.xpath('//*[@id="data"]//tr/td[3]/text()')
    rushTds   = tree.xpath('//*[@id="data"]//tr/td[4]/text()')
    recs      = tree.xpath('//*[@id="data"]//tr/td[5]/text()')
    recYards  = tree.xpath('//*[@id="data"]//tr/td[6]/text()')
    recTds    = tree.xpath('//*[@id="data"]//tr/td[7]/text()')
    fumbles   = tree.xpath('//*[@id="data"]//tr/td[8]/text()')

    wrs = []
    for i in xrange(len(names)):
        wr = {"fpProjections": {}}
        wr["Name"] = names[i]
        wr["fpProjections"]["RushAtts"]  = float(rushAtts[i])
        wr["fpProjections"]["RushYards"] = float(rushYards[i])
        wr["fpProjections"]["RushTds"]   = float(rushTds[i])
        wr["fpProjections"]["Recs"]      = float(recs[i])
        wr["fpProjections"]["RecYards"]  = float(recYards[i])
        wr["fpProjections"]["RecTds"]    = float(recTds[i])
        wr["fpProjections"]["Fumbles"]   = float(fumbles[i])
        wrs.append(wr)

    return wrs


def getTes(tree):
    names    = tree.xpath('//*[@id="data"]//tr/td[1]/a/text()')
    recs     = tree.xpath('//*[@id="data"]//tr/td[2]/text()')
    recYards = tree.xpath('//*[@id="data"]//tr/td[3]/text()')
    recTds   = tree.xpath('//*[@id="data"]//tr/td[4]/text()')
    fumbles  = tree.xpath('//*[@id="data"]//tr/td[5]/text()')

    tes = []
    for i in xrange(len(names)):
        te = {"fpProjections": {}}
        te["Name"] = names[i]
        te["fpProjections"]["Recs"]     = float(recs[i])
        te["fpProjections"]["RecYards"] = float(recYards[i])
        te["fpProjections"]["RecTds"]   = float(recTds[i])
        te["fpProjections"]["Fumbles"]  = float(fumbles[i])
        tes.append(te)

    return tes


def getKs(tree):
    names = tree.xpath('//*[@id="data"]//tr/td[1]/a/text()')
    fg    = tree.xpath('//*[@id="data"]//tr/td[2]/text()')
    fga   = tree.xpath('//*[@id="data"]//tr/td[3]/text()')
    xpt   = tree.xpath('//*[@id="data"]//tr/td[4]/text()')

    ks = []
    for i in xrange(len(names)):
        k = {"fpProjections": {}}
        k["Name"] = names[i]
        k["fpProjections"]["FG"]  = float(fg[i])
        k["fpProjections"]["FGA"] = float(fga[i])
        k["fpProjections"]["XPT"] = float(xpt[i])
        ks.append(k)

    return ks
