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
# hero_size = 10
# dim = 128
# max_hero = 130
nb_epoch = 20

l2_lambda = 0.00001

def load_pk(filename):
    fin = open(filename,"rb")
    (x, y) = cPickle.load(fin)
    X = np.array(x)
    Y = np.array([int(e) for e in y])
    fin.close()
    return (X, Y)

if __name__ == '__main__':
    directory = "../feature"
    # (X, Y) = load_pk("%s/player_rank_individual.pk"%directory)
    (X, Y) = load_pk("%s/player_rank_avg.pk"%directory)

    # Split data into train, validation, test sets
    N, dim = X.shape
    train_x = X[:int(N*.9),:]
    train_y = Y[:int(N*.9)]
    valid_x = X[int(N*.9):int(N*.95),:]
    valid_y = Y[int(N*.9):int(N*.95)]
    test_x = X[int(N*.95):,:]
    test_y = Y[int(N*.95):]

    x = Input(batch_shape=(batch_size, dim)) # input data
    predict = Dense(1, input_dim = dim, activation='sigmoid', W_regularizer=l2(l2_lambda))(x)
    model = Model(input=x, output=predict)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(train_x, train_y, batch_size=batch_size, nb_epoch=nb_epoch,
          validation_data=(valid_x, valid_y))
    loss, acc = model.evaluate(test_x, test_y, batch_size=batch_size)
    print '\nloss:', loss
    print 'Test accuracy:', acc


