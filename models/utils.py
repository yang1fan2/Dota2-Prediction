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
    if len(feature)==0:
        return train_x, test_x
    train = []
    test =[]
    for k,v in feature.items():
        print 'use feature : ',k
        train.append(train_x[:,v[0]:v[1]])
        test.append(test_x[:,v[0]:v[1]])

    return np.concatenate(train,axis = 1),np.concatenate(test,axis = 1)    

def load_data(dir_name):
    (train_x, train_y) = load_dict("%s_train.pk"%dir_name)
    (test_x, test_y) = load_dict("%s_test.pk"%dir_name)
    train_x = normalize(train_x)
    test_x = normalize(test_x)
    return train_x, train_y, test_x, test_y