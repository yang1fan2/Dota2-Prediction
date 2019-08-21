from keras.models import Sequential,Model
from keras.layers import Dense, Activation, Embedding
from keras.layers import Input, Dense, Lambda
import numpy as np
from keras.regularizers import l2, l1
from six.moves import cPickle
from sklearn.preprocessing import Imputer
from utils import *

batch_size = 32
hero_size = 10
dim = 128
max_hero = 130
nb_epoch = 20

l2_lambda = 0.00001
l1_lambda = 0.00001
# [1] binary hero id: 113 * 2 = 226 dim 0
# [2] hero attributes: 10 * 26 = 260 dim 226
# [3] hero_winrate: 5 * 5 = 25 dim 486
# [4] player_mmrpec: 10 * 2 = 20 dim 511
# [5] hero_player: 10 * 8 = 80 dim 531
    
feature = {'hero_id':[0,226]}#, 'winrate':[486,486+25]},'mmr':[511,511+20]




if __name__ == '__main__':
    directory = "../match_data/new_match"
    (train_x, train_y) = load_dict("%s_train.pk"%directory)
    (test_x, test_y) = load_dict("%s_test.pk"%directory)
    train_x = normalize(train_x)
    test_x = normalize(test_x)
    #train_x, test_x = choose_feature(train_x, test_x, feature)
    feature_dim = train_x.shape[1]
    print 'feature_dim = ',feature_dim
    print 'test examples = ',test_x.shape[0]
    x = Input(batch_shape=(batch_size, feature_dim)) # input data
    predict = Dense(1, input_dim = feature_dim,activation='sigmoid',W_regularizer=l2(l2_lambda))(x)    
    model = Model(input=x, output=predict)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(train_x, train_y, batch_size=batch_size, nb_epoch=nb_epoch,
          validation_split=0.1)
    score, acc = model.evaluate(test_x, test_y, batch_size=batch_size)
    print '\nscore ', score
    print 'acc ',acc
