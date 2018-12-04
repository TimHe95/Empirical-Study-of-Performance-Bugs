#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#print(__doc__)
import time
import numpy as np
import getopt, sys

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # necessary 

from sklearn.decomposition import PCA
from sklearn import svm


def load_data(data_dir, Test_Set_Percentage):
    X = np.loadtxt(data_dir+'/res_train.txt')
    
    np.random.shuffle(X)
    
    Test_Set_Size = round(Test_Set_Percentage * X.shape[0])
    
    # Generate train data
    X_train = X[:-Test_Set_Size]
    
    # Generate some regular novel observations
    X_test = X[-Test_Set_Size:]
    
    # Generate some abnormal novel observations
    X_outliers = np.random.uniform(low=9, high=11, size=(1, X.shape[1]))
    
    X_outliers[-1] = np.loadtxt(data_dir+'/res_test.txt')
    if len(X_outliers.shape) == 1: # if there is only one outlier sample.
        X_outliers = X_outliers.reshape(1, -1)
    
    return (X_train, X_test, X_outliers)


def PCA_n(X_train, X_test, X_outliers, n):
    
    pca = PCA(n_components=n)
    
    all_data4reduced = np.vstack((X_train, X_test, X_outliers))
    
    reduced = pca.fit_transform(all_data4reduced)
    
    X_train_reduced = reduced[0 : X_train.shape[0]]
    X_test_reduced = reduced[X_train.shape[0] : X_train.shape[0] + X_test.shape[0]]
    X_outliers_reduced = reduced[-X_outliers.shape[0]:]
    
    return (X_train_reduced, X_test_reduced, X_outliers_reduced)


def visualize(X_train_embedding, X_test_embedding, X_outliers_embedding):

    fig = plt.figure()
    
    ax = fig.gca(projection='3d')
    s = 30
    ax.scatter(X_train_embedding[:, 0], X_train_embedding[:, 1], X_train_embedding[:, 2],
               c='white', s=s, edgecolors='k')
    ax.scatter(X_test_embedding[:, 0], X_test_embedding[:, 1], X_test_embedding[:, 2],
               c='blueviolet', s=2*s, edgecolors='k')
    ax.scatter(X_outliers_embedding[:, 0], X_outliers_embedding[:, 1], X_outliers_embedding[:, 2],
               c='gold', s=s*2, edgecolors='k')
    plt.show()


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:k:g:d:c:s:m:b:p:", 
                                   ["nu","kernel","gamma","degree","coef0","shrinking","max-iter","base-dir","test-set-percentage"])
    except getopt.GetoptError as err:
        print ([str(err),'\nCommand option error.'])  # will print something like "option -a not recognized"
        sys.exit(2)
        
    m_nu=0.01 #(default=0.5)
        
    # 'linear', 'poly', 'rbf', 'sigmoid', 'precomputed' or a callable. 
    m_kernel='poly' #(default='rbf')
    
    # Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’. 
    m_gamma='auto' #(default='auto')

    # Degree of the polynomial kernel function (‘poly’). Ignored by all other kernels.        
    m_degree=3 #(default=3)
    
    # Independent term in kernel function. It is only significant in ‘poly’ and ‘sigmoid’
    m_coef0=0.0 #(default=0.0)
    
    # Whether to use the shrinking heuristic.
    m_shrinking=True
    
    # Hard limit on iterations within solver, or -1 for no limit.
    m_max_iter=-1 #(default=-1)
    
    data_dir='/Users/hhc/Desktop/auto-test/hehaochen-bugreproduce/S4_GenData4ML'
    
    Test_Set_Percentage = 0.1
    
    n = 3 # PCA dimension 3 is for 3D drawing
    
    for o, a in opts:
        if o in ("-n", "--nu"):
            m_nu = float(a)
        elif o in ("-k", "--kernel"):
            m_kernel = a
        elif o in ("-g", "--gamma"):
            m_gamma = a # maybe float?
        elif o in ("-d", "--degree"):
            m_degree = int(a)
        elif o in ("-c", "--coef0"):
            m_coef0 = float(a)
        elif o in ("-s", "--shrinking"):
            m_shrinking = bool(a)
        elif o in ("-m", "--max-iter"):
            m_max_iter = int(a)
        elif o in ("-b", "--base-dir"):
            data_dir = a.strip('/')
        elif o in ("-p", "--test-set-percentage"):
            Test_Set_Percentage = float(a)
        else:
            print("unhandled option")
            sys.exit(1)
    
    # load data
    X_train, X_test, X_outliers = load_data(data_dir, Test_Set_Percentage)

    # pca
    X_train_reduced, X_test_reduced, X_outliers_reduced = PCA_n(X_train, X_test, X_outliers, n)

    # train model
    start = time.time()
    clf = svm.OneClassSVM(nu=m_nu, kernel=m_kernel, gamma=m_gamma, degree=m_degree, 
                          coef0=m_coef0, shrinking=m_shrinking, max_iter=m_max_iter)
    clf.fit(X_train_reduced)
    end = time.time()
    print('model training done. Use %.3f sec'%(end-start))
    
    # test model
    y_pred_train = clf.predict(X_train_reduced)
    y_pred_test = clf.predict(X_test_reduced)
    y_pred_outliers = clf.predict(X_outliers_reduced)
    
    # show error rate
    n_error_train = y_pred_train[y_pred_train == -1].size
    n_error_test = y_pred_test[y_pred_test == -1].size
    n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
    print("error train: %d/%d ; errors novel regular: %d/%d ; "
          "errors novel abnormal: %d/%d"
          % (n_error_train, X_train_reduced.shape[0], 
             n_error_test, X_test_reduced.shape[0], 
             n_error_outliers, X_outliers_reduced.shape[0]))
    
    visualize(X_train_reduced, X_test_reduced, X_outliers_reduced)

if __name__ == "__main__":
    
    main()




