from sklearn.preprocessing import Imputer
from sklearn import preprocessing
from six.moves import cPickle
import numpy as np


def normalize(X):
    #replace NaN with mean value
    imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(X)
    X = imp.transform(X)

    
    scaler = preprocessing.StandardScaler()

    #preprocessing.MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled

def load_dict(filename):
    fin = open(filename, 'rb')
    return cPickle.load(fin)  

def choose_feature(train_x, test_x, feature):
    # 0.00070101986416 S_R - S_D
    # 0.533479546336 C_R
    
    if len(feature)==0:
        return train_x, test_x
    train = []
    test =[]
    for k,v in feature.items():
        print 'use feature : ',k
        train.append(train_x[:,v[0]:v[1]])
        test.append(test_x[:,v[0]:v[1]])

    # train_S = np.ones((train_x.shape[0],1),dtype='float32') * 0.00070101986416
    # test_S = np.ones((test_x.shape[0],1),dtype='float32') * 0.00070101986416
    # train_D = np.ones((train_x.shape[0],1),dtype='float32') * 0.533479546336
    # test_D = np.ones((test_x.shape[0],1),dtype='float32') * 0.533479546336
    # train += [train_S, train_D]
    # test += [test_S, test_D]

    return np.concatenate(train,axis = 1),np.concatenate(test,axis = 1)    

def load_data(dir_name):
    (train_x, train_y) = load_dict("%s_train.pk"%dir_name)
    (test_x, test_y) = load_dict("%s_test.pk"%dir_name)
    train_x = normalize(train_x)
    test_x = normalize(test_x)
    return train_x, train_y, test_x, test_y