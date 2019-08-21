# Real-time Dota2 Match Result Prediction
In this project, we try to predict the winning team of a Dota2 match. We consider prior (pre-match) features from individual players' match history, as well as real-time (during-match) features at each minute as the match progresses. We use logistic regression, the proposed Attribute Sequence Model, and their combinations as the prediction models. In a dataset of 78362 matches where 20631 matches contain replay data, our experiments show that adding more aspects of prior features improves accuracy from 58.69% to 71.49%, and introducing real-time features achieves up to 93.73% accuracy when predicting at the 40th minute.

## Training
```
pip install keras==1.0.0
cd match_data; unzip new_match.zip
cd ../models; python2 lr.py
# Please use Theano as the backend
```

## Dota dataset stored as MongoDB dump (2.35 GB, 1M matches, 20K players and 111 heros). Crawled via the APIs.
Availabe in Google [Drive](https://drive.google.com/open?id=0BwzxsWu2LtGyS0NiMktmNGxHem8).
There are four collections in mongoDB (db name is 701)
- benchmark: https://www.opendota.com/benchmarks
- hero: http://api.herostats.io/ (hero id bug is fixed)
- matches: https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails (1M matches)
- player: 200k players' profile (MMR rating, winning and losing games, played heroes and etc.). Each player has at least 100 matches in the above 1M matches. (https://www.opendota.com/players/89593976)
- distribution https://www.opendota.com/distributions


## Reference
Please find more information from this [paper](https://arxiv.org/abs/1701.03162)
```
@article{yang2016real,
  title={Real-time esports match result prediction},
  author={Yang, Yifan and Qin, Tian and Lei, Yu-Heng},
  journal={arXiv preprint arXiv:1701.03162},
  year={2016}
}
```
