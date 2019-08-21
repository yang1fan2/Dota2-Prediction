'''
UCSD: DOTA 2 Win Prediction
the version with only offset
'''

from keras.models import Sequential,Model
from keras.layers import Dense, Activation, Embedding
from keras.layers import Input, Dense, Lambda, GlobalAveragePooling1D
import numpy as np
from keras.regularizers import l2, activity_l2
from six.moves import cPickle

batch_size = 32
hero_size = 10
dim = 128
max_hero = 130
nb_epoch = 20

l2_lambda = 0.00001

def load_pk(filename):
    fin = open(filename,"rb")
    (x, y) = cPickle.load(fin)
    n = len(x)
    feature = np.zeros((n,max_hero*2+1))
    cnt = 0
    for players in x:
        feature[cnt,0]=1 # bias
        for i in range(5):
            assert players[i]<max_hero
            assert players[5+i]<max_hero
            feature[cnt,1+players[i]] = 1 #radiant feature
            feature[cnt,max_hero+1+players[5+i]] = 1 # dire feature
        cnt += 1
    y = [int(e) for e in y]
    y = np.array(y)
    fin.close()
    return (feature,y)

if __name__ == '__main__':
    directory = "100k_very_high"
    (train_x, train_y) = load_pk("%s/train.pk"%directory)
    (valid_x, valid_y) = load_pk("%s/valid.pk"%directory)
    (test_x, test_y) = load_pk("%s/test.pk"%directory)
    x = Input(batch_shape=(batch_size, 2*max_hero + 1)) # input data
    predict = Dense(1, input_dim = 2*max_hero+1,activation='sigmoid',W_regularizer=l2(l2_lambda))(x)    
    model = Model(input=x, output=predict)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(train_x, train_y, batch_size=batch_size, nb_epoch=nb_epoch,
          validation_data=(valid_x, valid_y))
    score, acc = model.evaluate(test_x, test_y, batch_size=batch_size)
    print '\nscore ', score
    print 'acc ',acc


