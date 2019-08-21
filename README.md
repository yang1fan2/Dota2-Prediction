# Dota2-Prediction



## Dota dataset: MongoDB dump (2.35 GB, 1M matches, 20K players and 111 heros)
link: https://drive.google.com/open?id=0BwzxsWu2LtGyS0NiMktmNGxHem8
There are four collections in mongoDB (db name is 701)
- benchmark: https://www.opendota.com/benchmarks
- hero: http://api.herostats.io/ (hero id bug is fixed)
- matches: https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails (1M matches)
- player: 200k players' profile (MMR rating, winning and losing games, played heroes and etc.). Each player has at least 100 matches in the above 1M matches. (https://www.opendota.com/players/89593976)
- distribution https://www.opendota.com/distributions
