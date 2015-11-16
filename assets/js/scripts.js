// generate many Draft Kings lineups, pick best
function getTopLineup(fileLoc, site) {
    "use strict";
    function readPlayerFile(fileLocation) {

        function getFileFromServer(url, doneCallback) {

            function handleStateChange() {
                if (xhr.readyState === 4) {
                    doneCallback(xhr.status === 200
                        ? xhr.responseText
                        : null);
                }
            }
            var xhr;
            xhr = new XMLHttpRequest();
            xhr.onreadystatechange = handleStateChange();
            xhr.open("GET", url, true);
            xhr.send();
        }
        var players = getFileFromServer(fileLocation, function (data) {
            if (data === null) {
                data = [];
                throw "Can't read the file for some reason";
            }
            return data;
        });
        return players;
    }
    function getFlex(site) {
        if (site === "dk") {
            return ["RB", "WR", "TE"];
        } else {
            if (site === "fd") {
                return [null];
            }
        }
        return [null];
    }
    function getPositions(site) {
        if (site === "dk") {
            return {"QB": 1, "RB": 2, "WR": 3, "TE": 1, "DST": 1};
        } else {
            if (site === "fd") {
                return {"QB": 1, "RB": 2, "WR": 3, "TE": 1, "K": 1, "DST": 1};
            } else {
                throw "Can't read the key";//why??
                return null;
            }
        }
    }
    function getBudget(lineup) {
        var i, currentBudget = 0;
        for (i = 0; i < lineup.length; i += 1) {
            currentBudget = currentBudget + lineup[i].Salary;
        }
        return currentBudget;
    }
    function getPoints(lineup) {
        var i, currentPoints = 0;
        for (i = 0; i < lineup.length; i += 1) {
            currentPoints = currentPoints + lineup[i].Points;
        }
        return currentPoints;
    }
    function updateLineup(oldLineup, newLineup) {
        if (getPoints(newLineup) >= getPoints(oldLineup)) {
            if (getPoints(newLineup) === getPoints(oldLineup)) {
                if (getBudget(newLineup) > getBudget(oldLineup)) {
                    return oldLineup
                }
            }
            return newLineup;
        }
        return oldLineup;
    }
    function getTopFlexLineup(players, site, benched) {

        function getLineup(players, site, flexPos, benched) {

            function addFlextoPositions(site, flexPos) {
                var positions = getPositions(site);
                if (positions === null) {
                    throw "Null positions from getPositions(site);  Can't read site?";
                }
                if (positions.indexOf(flexPos) > -1) {
                    positions[flexPos] += 1;
                }
                return positions;
            }
            function isValidLineup(lineup, site) {
                function underBudget(lineup, site) {
                    function getSiteBudget(site) {
                        if (site === "dk") {
                            return 50000;
                        } else {
                            if (site === "fd") {
                                return 60000;
                            }
                        }
                        return 0;
                    }
                    return getSiteBudget(site) < getBudget(lineup);
                }
                function rightPlayers(lineup, site) {
                    function countPos(lineup) {
                        var i, pos, lineupPos = {};
                        for (i = 0; i < lineup.length; i += 1) {
                            pos = lineup[i].Position;
                            if (lineupPos.keys.indexOf(pos) > -1) {
                                lineupPos[pos] += 1;
                            } else {
                                lineupPos[pos] = 1;
                            }
                        }
                        return lineupPos;
                    }
                    function comparePositions(a, b) {
                        var valid = true;
                        var i, ks = a.keys;
                        for (i = 0; i < ks.length; i += 1) {
                            if (a[ks] !== b[ks]) {
                                valid = false;
                            }
                        }
                        return valid;
                    }
                    var lineupPos = countPos(lineup);
                    var flex = getFlex(site);
                    var positions = getPositions(site);
                    var i, valid = false;
                    for (i = 0; i < flex.length; i += 1) {
                        positions = addFlextoPositions(flex[i], positions);
                        valid = comparePositions(positions, lineupPos);
                        if (valid) {
                            return valid;
                        }
                    }
                    return valid;
                }
                return underBudget(lineup, site);// && rightPlayers(lineup, site);
            }
            function getTopNPlayers(players, pos, benched, n) {
                function comparePlayers(a, b) {
                    if (a.Points < b.Points) {
                        return -1;
                    } else {
                        if (a.Points > b.Points) {
                            return 1;
                        }
                    }
                    return 0;
                }
                // players.sort(comparePlayers);
                var i, player, topPlayers = [];
                for (i = 0; i < n; i += 1) {
                    player = players[i];
                    if (player.Postition === pos) {
                        if (benched.indexOf(player) === -1) {
                            topPlayers.push(player);
                        }
                    }
                }
                return topPlayers.slice(0, n);
            }
            function getFirstLineup(players, site, flexPos, benched) {
                var positions = addFlextoPositions(flexPos, getPositions(site));
                // var ks = positions.keys;
                var i, key, topPlayers, lineup = [];
                for (key in positions) {
                    topPlayers = getTopNPlayers(players, key, benched, positions[key]);
                    for (i = 0; i < topPlayers.length; i += 1) {
                        lineup.push(topPlayers[i]);
                    }
                }
                // for (i = 0; i < ks.length; i += 1) {
                //     topPlayers = getTopNPlayers(players, ks[i], benched, positions[ks[i]]);
                //     for (j = 0; j < topPlayers.length; j += 1) {
                //         lineup.push(topPlayers[j]);
                //     }
                // }
                return lineup;
            }
            function iterLineup(lineup, players) {
                function getWorstPlayer(lineup) {
                    var i, minPointsPerDollar, worst, player, ppd;
                    for (i = 0; i < lineup.length; i += 1) {
                        player = lineup[i];
                        ppd = player.Points / player.Salary;
                        if (minPointsPerDollar === null) {
                            minPointsPerDollar = ppd;
                            worst = player;
                        } else if (minPointsPerDollar > ppd) {
                            minPointsPerDollar = ppd;
                            worst = player;
                        }
                    }
                    return worst;
                }
                var worst, worstIndex;
                while (!isValidLineup(lineup)) {
                    worst = getWorstPlayer(lineup);
                    worstIndex = lineup.indexOf(worst);
                    benched.push(worst);
                    if (worstIndex > -1) {
                        lineup.splice(worstIndex, 1);
                    }
                    lineup.push(getTopNPlayers(players, worst.Position, benched, 1)[0]);
                }
                return lineup;
            }
            var lineup = getFirstLineup(players, site, flexPos, benched);
            lineup = iterLineup(lineup, players);
            return lineup;
        }
        var flex = getFlex(site);
        var i, lineup, finalLineup = [];
        for (i = 0; i < flex.length; i += 1) {
            lineup = getLineup(players, site, flex[i], benched);
            finalLineup = updateLineup(finalLineup, lineup);
        }
        return finalLineup;
    }
    var finalLineup = [];
    var benched = [];
    var site = parseSiteKey(fileLoc);
    var players = readPlayerFile(fileLoc);
    var lineup = getTopFlexLineup(players, site, benched);
    var i, j, size = finalLineup.length;
    for (i = 0; i < size; i += 1) {
        benched = [];
        for (j = 0; j < size; j += 1) {
            benched.push(finalLineup[(i + j) % size]);
            lineup = getTopFlexLineup(players, site, benched);
            finalLineup = updateLineup(finalLineup, lineup);
        }
    }
    return finalLineup;
}
function writeLineupTable(lineup) {
    "use strict";
    var table = [];
    table.push("<table><thead><tr><th>Position</th><th>Name</th>");
    table += "<th>Salary</th><th>Points</th></tr></thead><tbody>";
    var i, player;
    for (i = 0; i < lineup.length; i += 1) {
        player = lineup[i];
        table.push("<tr><td>");
        table.push(player.Position);
        table.push("</td><td>");
        table.push(player.Name);
        table.push("</td><td>");
        table.push((player.Salary).toString());
        table.push("</td><td>");
        table.push((player.Points).toString());
        table.push("</td></tr>");
    }
    table.push("</tbody></table>");
    return table.join("");
}
function parseSiteKey(fileLocation) {
    if (fileLocation === 'assets/scripts/data/bestDkPlayers.json'){
        return "dk";
    } else {
        if (fileLocation === 'assets/scripts/data/bestFdPlayers.json') {
            return "fd";
        }
        else {
            throw "Can't compare file for key"
            return null;
        }
    }
}
//onClick for user selecting Draft Kings
function showDkLineup() {
    "use strict";
    document.getElementById('splash-buttons').style.display = "none";
    var fileLoc = 'assets/scripts/data/bestDkPlayers.json';
    var key = parseSiteKey(fileLoc);
    var best = getTopLineup(fileLoc, key);
    var table = writeLineupTable(best);
    var console;
    console.log(table);

    document.getElementById('lineup').style.display = "block";
}

//onClick for user selecting Fan Duel
function showFdLineup() {
    "use strict";
    document.getElementById('splash-buttons').style.display = "none";
    var fileLoc = 'assets/scripts/data/bestFdPlayers.json';
    var best = getTopLineup(fileLoc, parseSiteKey(fileLoc));
    var table = writeLineupTable(best);
    var console;
    console.log(table);

    document.getElementById('lineup').style.display = "block";
}