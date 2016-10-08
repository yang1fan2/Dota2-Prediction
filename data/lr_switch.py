'''
Please refer How Does He Saw Me? A Recommendation Engine for Picking Heroes in Dota 2
'''
from keras.models import Sequential,Model
from keras.layers import Dense, Activation, Embedding,Merge,merge
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
    feature = np.zeros((n,max_hero*4))
    cnt = 0
    for players in x:
#        feature[cnt,0]=1 # bias
        for i in range(5):
            assert players[i]<max_hero
            assert players[5+i]<max_hero
            feature[cnt,players[i]] = 1
            feature[cnt,3*max_hero + players[i]] = 1
            feature[cnt,max_hero+players[5+i]] = 1
            feature[cnt,2*max_hero+players[5+i]] = 1
        cnt += 1
    y = [int(e) for e in y]
    y = np.array(y)
    fin.close()
    return (feature,y)

if __name__ == '__main__':
    (train_x, train_y) = load_pk("10k/train.pk")
    (valid_x, valid_y) = load_pk("10k/valid.pk")
    (test_x, test_y) = load_pk("10k/test.pk")
    x = Input(batch_shape=(batch_size, 4*max_hero))
    radiant = Lambda(lambda x:x[:,0:2*max_hero],output_shape=lambda x:(x[0],x[1]/2))(x)
    dire = Lambda(lambda x:x[:,2*max_hero:],output_shape=lambda x:(x[0],x[1]/2))(x)
    dense_layer = Dense(1, input_dim = 2*max_hero,activation='sigmoid',W_regularizer=l2(l2_lambda))
    predict_r = dense_layer(radiant)
    predict_d = dense_layer(dire)
    predict = merge([predict_r,predict_d],mode = lambda x:(x[0]+(1-x[1]))/2,output_shape=lambda x:x[0])
    model = Model(input=x, output=predict)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(train_x, train_y, batch_size=batch_size, nb_epoch=nb_epoch,
          validation_data=(valid_x, valid_y))
    score, acc = model.evaluate(test_x, test_y, batch_size=batch_size)
    print '\nscore ', score
    print 'acc ',acc


