import numpy as np
from six.moves import cPickle
from sklearn.preprocessing import Imputer
from utils import *
from keras.models import Sequential,Model
from keras.layers import Dense, Activation, Embedding
from keras.layers import Input, Dense, Lambda, GlobalAveragePooling1D
from keras.regularizers import l2, activity_l2,l1, activity_l1

class Param:
    batch_size = 32
    dim = 64
    nb_epoch = 32  # smaller data size takes more epochs to converge

    nn_lambda = 0.001
    lr_lambda = 0.000001
    # [1] binary hero id: 113 * 2 = 226 dim 0   'hero_id':[0,226]
    # [2] hero attributes: 10 * 26 = 260 dim 226  'hero_attr':[226,226+260]
    # [3] hero_winrate: 5 * 5 = 25 dim 486  'winrate':[486,486+25]
    # [4] player_mmrpec: 10 * 2 = 20 dim 511 'mmr':[511,511+20]
    # [5] hero_player_attr: 10 * 8 = 70 dim 531 'h_p_attr':[531,531+70]
    # [6] hero_player_winrate: 10 dim 601 'h_p_winrate':[601,601+10]
    feature = {'hero_id':[0,226], 'hero_attr':[226,226+260], 'winrate':[486,486+25], \
    'mmr':[511,511+20], 'h_p_attr':[531,531+70], 'h_p_winrate':[601,601+10]}
param = Param()
feature_dim = 611

def logistic_regression():
    x = Input(batch_shape=(param.batch_size, feature_dim)) # input data
    predict = Dense(1, input_dim = feature_dim,activation='sigmoid',W_regularizer=l2(param.lr_lambda))(x)    
    model = Model(input=x, output=predict)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def nn():
    x = Input(batch_shape=(param.batch_size, feature_dim)) # input data
    layer1 = Dense(param.dim, input_dim = feature_dim,activation='sigmoid',W_regularizer=l2(param.nn_lambda))(x)    
    predict = Dense(1, input_dim = param.dim,activation='sigmoid',W_regularizer=l2(param.nn_lambda))(layer1)    
    model = Model(input=x, output=predict)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

classifiers = {

    # 'nn': nn,
    'LR': logistic_regression,
    
}


if __name__ == '__main__':
    
    train_x_all, train_y_all, test_x, test_y = load_data("../match_data/new_match")
    # train_x_all, test_x = choose_feature(train_x_all, test_x_all, param.feature)

    # Random shuffle (in-place) before splitting the training set
    train_y_all = np.array([train_y_all]).transpose()
    train_all = np.hstack((train_x_all, train_y_all))
    np.random.shuffle(train_all)
    train_x_all = train_all[:,0:-1]
    train_y_all = train_all[:,-1]

    feature_dim = train_x_all.shape[1]
    print 'feature_dim = ',feature_dim
    print 'test examples = ',test_x.shape[0]

    # Run classifiers for each training data size
    train_size = np.exp2(range(7,17)).astype(int)

    for size in train_size:
        train_x = train_x_all[0:size,:]
        train_y = train_y_all[0:size]
        print 'train examples = ',train_x.shape[0]

        for index, (name, classifier) in enumerate(classifiers.items()):
            model = classifier()
            model.fit(train_x, train_y, batch_size=param.batch_size, nb_epoch=param.nb_epoch)
            score, acc = model.evaluate(test_x, test_y, batch_size=param.batch_size)
            print '\n ',name
            print ' test acc ',acc
