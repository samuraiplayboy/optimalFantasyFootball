function getTopLineup(fileLoc, benched) {
    "use strict";
    function parseSiteKey(fileLoc) {
        if (fileLoc === "assets/data/bestDkPlayers.json") {
            return 'dk';
        } else {
            if (fileLoc === "assets/data/bestFdPlayers.json") {
                return 'fd';
            } else {
                throw "Can't compare file for key";
            }
        }
    }
    function readPlayerFile(fileLoc, callback) {
        var data = jQuery.parseJSON(
            jQuery.ajax({
                url: fileLoc,
                async: false,
                dataType: 'json'
            }).responseText
        );
        return data;
    }
    function getFlex(site) {
        var flex;
        if (site === "dk") {
            flex = ["RB", "WR", "TE"];
        } else {
            if (site === "fd") {
                flex = [null];
            } else {
                throw "Can't read site param";
            }
        }
        return flex;
    }
    function getPositions(site) {
        var positions;
        if (site === "dk") {
            positions = {"QB": 1, "RB": 2, "WR": 3, "TE": 1, "DST": 1};
        } else {
            if (site === "fd") {
                positions = {"QB": 1, "RB": 2, "WR": 3, "TE": 1, "K": 1, "DST": 1};
            } else {
                throw "Can't read the key from showLineup";
            }
        }
        return positions;
    }
    function getBudget(lineup) {
        var currentBudget = 0;
        lineup.forEach(function (player) {
            currentBudget = currentBudget + player.Salary;
        });
        return currentBudget;
    }
    function getPoints(lineup) {
        var currentPoints = 0;
        lineup.forEach(function (player) {
            currentPoints = currentPoints + player.Points;
        });
        return currentPoints;
    }
    function updateLineup(oldLineup, newLineup) {
        if (newLineup === undefined) {
            throw "Comparing a lineup with an UNDEFINED lineup.";
        }
        var oP = getPoints(oldLineup);
        var nP = getPoints(newLineup);
        if (nP > oP) {
            return newLineup;
        } else {
            if (oP > nP) {
                return oldLineup;
            } else {
                var oB = getBudget(oldLineup);
                var nB = getBudget(newLineup);
                if (nB < oB) {
                    return newLineup;
                } else {
                    return oldLineup;
                }
            }
        }
    }
    function getTopFlexLineup(players, site, benched) {

        function getLineup(players, site, flexPos, benched) {

            function addFlextoPositions(site, flexPos) {
                var positions = getPositions(site);
                if (positions === null) {
                    throw "Null positions from getPositions(site)  Can't read site?";
                }
                if (positions.hasOwnProperty(flexPos) > -1 && flexPos !== null) {
                    positions[flexPos] += 1;
                }
                return positions;
            }
            function isValidLineup(lineup, site) {
                function underBudget(lineup, site) {
                    var totalBudget;
                    if (site === 'dk') {
                        totalBudget = 50000;
                    } else {
                        if (site === 'fd') {
                            totalBudget = 60000;
                        } else {
                            throw "Error validating lineup site key.";
                        }
                    }
                    return totalBudget >= getBudget(lineup);
                }
                function rightPlayers(lineup, site) {
                    //see if the a's and b's lineup position values match.
                    function comparePositions(a, b) {
                        var valid = true;
                        var ks = Object.keys(a);
                        ks.forEach(function (pos) {
                            if (a[pos] !== b[pos]) {
                                valid = false;
                            }
                        });
                        return valid;
                    }
                    //get lineup position values for our lineup.
                    var pos, lineupPos = {};
                    lineup.forEach(function (player) {
                        pos = player.Position;
                        if (lineupPos.hasOwnProperty(pos)) {
                            lineupPos[pos] += 1;
                        } else {
                            lineupPos[pos] = 1;
                        }
                    });
                    var flex = getFlex(site);
                    var valid, positions = getPositions(site);
                    flex.forEach(function (f) {
                        positions = addFlextoPositions(site, f);
                        valid = comparePositions(positions, lineupPos);
                        if (valid) {
                            return valid;
                        }
                    });
                    return valid;
                }
                return underBudget(lineup, site);// && rightPlayers(lineup, site);
            }
            function getTopNPlayers(players, pos, benched, n) {
                var topPlayers = [];
                players.forEach(function (player) {
                    if (player.Position === pos && benched.indexOf(player) < 0) {
                        topPlayers.push(player);
                    }
                });
                var top = topPlayers.sort(function (a, b) {
                    if (a.Points > b.Points) {
                        return -1;
                    } else {
                        if (a.Points < b.Points) {
                            return 1;
                        } else {
                            return 0;
                        }
                    }
                });
                return top.slice(0, n);
            }
            function getFirstLineup(players, site, flexPos, benched) {
                var positions = addFlextoPositions(site, flexPos);
                var lineup = [];
                Object.keys(positions).forEach(function (pos) {
                    getTopNPlayers(players, pos, benched, positions[pos])
                        .forEach(function (player) {
                            lineup.push(player);
                        });
                });
                return lineup;
            }
            function iterLineup(lineup, players, site, benched) {

                function getWorstPlayer(lineup, fixed) {
                    var worst, ppd, minPointsPerDollar;
                    lineup.forEach(function (player) {
                        if (fixed.indexOf(player) > -1) {
                            return;
                        }
                        ppd = player.Points / player.Salary;
                        if (minPointsPerDollar === undefined) {
                            minPointsPerDollar = ppd;
                            worst = player;
                        } else {
                            if (minPointsPerDollar > ppd) {
                                minPointsPerDollar = ppd;
                                worst = player;
                            }
                        }
                    });
                    if (worst === undefined || worst === null) {
                        throw "getWorstPlayerError: returning empty value.";
                    }
                    return worst;
                }
                var worst, worstIndex, newPlayer, seen = benched;
                lineup.forEach(function (player) {
                    if (benched.indexOf(player) < 0) {
                        seen.push(player);
                    }
                });
                var fixed = [];
                while (!isValidLineup(lineup, site)) {
                    worst = getWorstPlayer(lineup, fixed);
                    worstIndex = lineup.indexOf(worst);
                    if (worstIndex > -1) {
                        newPlayer = getTopNPlayers(players, worst.Position, seen, 1)[0];
                        if (newPlayer === undefined || newPlayer === null) {
                            fixed.push(worst);
                            continue;
                        }
                        if (seen.indexOf(worst) < 0) {
                            seen.push(worst);
                        }
                        lineup.splice(worstIndex, 1);
                        lineup.push(newPlayer);
                        seen.push(newPlayer);
                    } else {
                        return lineup;
                    }
                }
                return lineup;
            }
            var lineup = getFirstLineup(players, site, flexPos, benched);
            lineup = iterLineup(lineup, players, site, benched);
            return lineup;
        }
        var lineup, finalLineup = [];
        getFlex(site).forEach(function (flex) {
            lineup = getLineup(players, site, flex, benched);
            finalLineup = updateLineup(finalLineup, lineup);
        });
        return finalLineup;
    }
    var seen = benched;
    var site = parseSiteKey(fileLoc);
    var players = readPlayerFile(fileLoc);
    var lineup = getTopFlexLineup(players, site, seen);
    var finalLineup = lineup;
    var i, j, size = finalLineup.length;
    for (i = 0; i < size; i += 1) {
        seen = [];
        for (j = 0; j < size; j += 1) {
            seen.push(finalLineup[(i + j) % size]);
            lineup = getTopFlexLineup(players, site, seen);
            finalLineup = updateLineup(finalLineup, lineup);
        }
    }
    return finalLineup;
}

function getLineupTable(lineup) {
    "use strict";
    function roundToTwo(num) {
        return (Math.round(player.Points * 100) / 100);
    }
    var table = [];
    table.push("<table><thead><tr><th>Position</th><th>Name</th>");
    table.push("<th>Salary</th><th>Points</th></tr></thead><tbody>");
    var totP = 0;
    var totS = 0;
    lineup.forEach(function (player) {
        table.push("<tr><td>");
        table.push(player.Position);
        table.push("</td><td>");
        table.push(player.Name);
        table.push("</td><td>");
        table.push((player.Salary).toString());
        table.push("</td><td>");
        table.push((Math.round(player.Points * 100) / 100).toString());
        table.push("</td></tr>");
        totP = totP + player.Points;
        totS = totS + player.Salary;
    });
    table.push("<tr><td><b>Total:</b></td><td><b>");
    table.push("$" + totS.toString());
    table.push("</b></td><td><b>");
    table.push((Math.round(player.Points * 100) / 100).toString() + " Points");
    table.push("</b></td></tr>");
    table.push("</tbody></table>");
    return table.join("");
}

function reoptimize() {
    "use strict";
    // first get selected players in current lineup.
    function getBenched() {
        // get selected players on page, and return in list
        return [];
    }
    var newLineup = getTopLineup(fileLoc, getBenched());
}

function reset() {
    "use strict";
    document.getElementById('lineup').style.display = "none";
    document.getElementById('splash-buttons').style.display = "block";
}

function showLineup(fileLoc) {
    "use strict";
    document.getElementById('lineupTable').innerHTML = getLineupTable(getTopLineup(fileLoc, []));
    document.getElementById('splash-buttons').style.display = "none";
    document.getElementById('lineup').style.display = "block";
}

function showDkLineup() {
    "use strict";
    showLineup("assets/data/bestDkPlayers.json");
}

function showFdLineup() {
    "use strict";
    showLineup("assets/data/bestFdPlayers.json");
}