'''
UCSD: DOTA 2 Win Prediction
the version with only offset
'''
from sklearn.cross_validation import StratifiedKFold
from keras.models import Sequential,Model
from keras.layers import Dense, Activation, Embedding
from keras.layers import Input, Dense, Lambda, GlobalAveragePooling1D
import numpy as np
from keras.regularizers import l2, activity_l2,l1, activity_l1
from six.moves import cPickle

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

def load_dict(filename):
    fin = open(filename, 'rb')
    return cPickle.load(fin)    


def choose_feature(train_x, test_x, feature):
    train = []
    test =[]
    for k,v in feature.items():
        print 'use feature : ',k
        if k!='mmr':
            train.append(train_x[:,v[0]:v[1]])
            test.append(test_x[:,v[0]:v[1]])
        else:
            for i in range(0,20,2):
                train.append(train_x[:,511+i+1:511+i+2])
                test.append(test_x[:,511+i+1:511+i+2])

    return np.concatenate(train,axis = 1),np.concatenate(test,axis = 1)

if __name__ == '__main__':
    directory = "../match_data/small_match"
    (train_x, train_y) = load_dict("%s_train.pk"%directory)
    (test_x, test_y) = load_dict("%s_test.pk"%directory)
    train_x, test_x = choose_feature(train_x, test_x, feature)
    feature_dim = train_x.shape[1]
    print 'feature_dim = ',feature_dim
    print 'test examples = ',test_x.shape[0]
    x = Input(batch_shape=(batch_size, feature_dim)) # input data
    layer_1 = Dense(128, input_dim = feature_dim,activation='relu',W_regularizer=l1(l1_lambda))(x)    
    predict = Dense(1, input_dim = 128,activation='sigmoid',W_regularizer=l1(l1_lambda))(layer_1)    
    model = Model(input=x, output=predict)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(train_x, train_y, batch_size=batch_size, nb_epoch=nb_epoch,
          validation_split=0.1)
    score, acc = model.evaluate(test_x, test_y, batch_size=batch_size)
    print '\nscore ', score
    print 'acc ',acc
