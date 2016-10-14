from keras.models import Sequential,Model
from keras.layers import Dense, Activation, Embedding,merge,Flatten
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
    x = np.array(x)
    y = np.array(y)
    fin.close()
    return (x,y)

if __name__ == '__main__':
    directory = "mongodb"
    (train_x, train_y) = load_pk("%s/train.pk"%directory)
    (valid_x, valid_y) = load_pk("%s/valid.pk"%directory)
    (test_x, test_y) = load_pk("%s/test.pk"%directory)
    x = Input(batch_shape=(batch_size, hero_size))
    hero_embed = Embedding(max_hero, dim,input_length=hero_size)(x)#(batch,10, dim)
    player_radiant = Lambda(lambda x:x[:,0:5,:],output_shape=lambda x:(x[0],hero_size/2,x[2]))(hero_embed)
    player_dire = Lambda(lambda x:x[:,5:,:],output_shape=lambda x:(x[0],hero_size/2,x[2]))(hero_embed)
    team_radiant =  GlobalAveragePooling1D()(player_radiant)
    team_dire =  GlobalAveragePooling1D()(player_dire)
    team_dense = Dense(1, W_regularizer=l2(l2_lambda))
    a_radient =  team_dense(team_radiant)
    a_dire =  team_dense(team_dire)
    team_difference = merge([a_radient,a_dire],mode=lambda x: x[0] - x[1],output_shape=lambda x:x[0])
    predict = Activation('sigmoid')(team_difference)
    model = Model(input=x, output=predict)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(train_x, train_y, batch_size=batch_size, nb_epoch=nb_epoch,
          validation_data=(valid_x, valid_y))
    score, acc = model.evaluate(test_x, test_y, batch_size=batch_size)
    print '\nscore ', score
    print 'acc ',acc


