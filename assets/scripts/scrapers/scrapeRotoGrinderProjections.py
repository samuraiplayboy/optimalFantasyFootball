import requests
from lxml import html
from collections import defaultdict
from time import sleep
from random import randint


def getRotoProjections():
    players = []
    baseUrl = "https://rotogrinders.com/projected-stats/nfl"
    urls = [baseUrl + "?site=%s" % s for s in ["draftkings", "fanduel"]]
    for url in urls:
        sleep(randint(1,5))
        if url[-1] == "s":
            keys = ("dkSalary", "rotoDkPoints")
        elif url[-1] == "l":
            keys = ("fdSalary", "rotoFdPoints")
        else:
            keys = ("Salary", "Points")

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
            allData   = tree.xpath('//*[@id="proj-stats"]//tr[2]/td[2]//text()')
            names     = getNames(tree)
            positions = getPos(tree)
            salaries  = getSalary(tree)
            points    = getPoints(tree)
        except:
            continue

        for i in xrange(len(names)):
            player = {
                "Name": names[i],
                "Position": positions[i],
                keys[0]: salaries[i],
                keys[1]: points[i]
            }
            print "Scraped RotoGrinder for:", player["Name"]
            players.append(player)

    return joinData(players)


def getNames(tree):
    names = tree.xpath('//*[@id="proj-stats"]//tr/td[1]//a/text()')

    return names


def getPos(tree):
    rawPositions = tree.xpath('//*[@id="proj-stats"]//tr/td[2]/text()')

    positions = []
    for p in rawPositions[1:]:
        pos = p.replace('\n', "").strip()
        if pos == "D":
            pos = "DST"
        positions.append(pos)

    return positions


def getSalary(tree):
    rawSalaries = tree.xpath('//*[@id="proj-stats"]//tr/td[4]/text()')

    salaries = []
    for sal in rawSalaries[1:]:
        sal = sal.rstrip('\n').replace('K','').replace('$','').strip()
        if sal == 'N/A':
            salaries.append(0)
        else:
            salaries.append(float(sal) * 1000)

    return salaries


def getPoints(tree):
    points = tree.xpath('//*[@id="proj-stats"]//tr/td[5]/text()')

    return [float(p) for p in points[1:]]


def joinData(data):
    d = defaultdict(dict)
    for e in data:
        d[e['Name']].update(e)

    return d.values()
