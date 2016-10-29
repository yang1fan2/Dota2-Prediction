# Dota2-Prediction

## Project deadlines:
- 10/05/2016, **Proposal:** A short description of the project, including: a title, Andrew ids of the members, and a short description of your proposed project (about a page).
- 11/07/2016, **Midway Report:** More detailed introduction, review of related works, details of the proposed method, and preliminary results if available, in 4-5 pages.
- 12/02/2016, **Poster session:** Present your work to the peers, instructors, and other community members who will stop by.
- 12/09/2016, **Final report:** _A full academic paper_, including: problem definition and motivation, background and related work, details of the proposed method, details of experiments and results, conclusion and future work. 8 pages *excluding* references and appendix.



## Dota dataset: MongoDB dump (2.35 GB, 1M matches, 20K players and 111 heros)
link: https://drive.google.com/open?id=0BwzxsWu2LtGyS0NiMktmNGxHem8
There are four collections in mongoDB (db name is 701)
- benchmark: https://www.opendota.com/benchmarks
- hero: http://api.herostats.io/ (hero id bug is fixed)
- matches: https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails (1M matches)
- player: 200k players' profile (MMR rating, winning and losing games, played heroes and etc.). Each player has at least 100 matches in the above 1M matches. (https://www.opendota.com/players/89593976)
- distribution https://www.opendota.com/distributions
