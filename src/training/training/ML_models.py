#from numpy import mean
import numpy as np
import pandas as pd
import time
import ray
# Start Ray.
ray.init(ignore_reinit_error=True)
import warnings
warnings.simplefilter("ignore")
from joblib import dump, load
import shap
#from sklearn.preprocessing import StandardScaler
#from sklearn.feature_selection import RFE
#from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.preprocessing import label_binarize
from sklearn.metrics import precision_score, roc_auc_score, accuracy_score, confusion_matrix, recall_score
#from sklearn.multiclass import OneVsRestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from imblearn.ensemble import BalancedRandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import matplotlib.pyplot as plt
import yaml
import gc
import os
os.chdir('/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/')

TUNE_STATE_REFRESH_PERIOD = 10  # Refresh resources every 10 s

@ray.remote(num_returns=6)
def data_parsing(var,config_dict,output):
    os.chdir('/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/')
    #Load data
    print(f'\nUsing merged_data-train_{var}..', file=open(output, "a"))
    X_train = pd.read_csv(f'train_{var}/merged_data-train_{var}.csv')
    #var = X_train[config_dict['ML_VAR']]
    X_train = X_train.drop(config_dict['ML_VAR'], axis=1)
    feature_names = X_train.columns.tolist()
    X_train = X_train.values
    Y_train = pd.read_csv(f'train_{var}/merged_data-y-train_{var}.csv')
    Y_train = label_binarize(Y_train.values, classes=['low_impact', 'high_impact']).ravel() 

    X_test = pd.read_csv(f'test_{var}/merged_data-test_{var}.csv')
    #var = X_test[config_dict['ML_VAR']]
    X_test = X_test.drop(config_dict['ML_VAR'], axis=1)
    #feature_names = X_test.columns.tolist()
    X_test = X_test.values
    Y_test = pd.read_csv(f'test_{var}/merged_data-y-test_{var}.csv')
    print('Data Loaded!')
    #Y = pd.get_dummies(y)
    Y_test = label_binarize(Y_test.values, classes=['low_impact', 'high_impact']).ravel()  
    
    #scaler = StandardScaler().fit(X_train)
    #X_train = scaler.transform(X_train)
    #X_test = scaler.transform(X_test)
    # explain all the predictions in the test set
    background = shap.kmeans(X_train, 10)
    return X_train, X_test, Y_train, Y_test, background, feature_names


@ray.remote #(num_cpus=9)
def classifier(clf,var, X_train, X_test, Y_train, Y_test, background,feature_names, output):
   os.chdir('/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/')
   start = time.perf_counter()
   score = cross_validate(clf, X_train, Y_train, cv=10, return_train_score=True, return_estimator=True, n_jobs=-1, verbose=0, scoring=('roc_auc','neg_log_loss'))
   clf = score['estimator'][np.argmin(score['test_neg_log_loss'])]
   #y_score = cross_val_predict(clf, X_train, Y_train, cv=5, n_jobs=-1, verbose=0)
   #class_weights = class_weight.compute_class_weight('balanced', np.unique(Y_train), Y_train)
   #clf.fit(X_train, Y_train) #, class_weight=class_weights)
   clf_name = str(type(clf)).split("'")[1]  #.split(".")[3]
   with open(f"./models/{var}/{clf_name}_{var}.joblib", 'wb') as f:
    dump(clf, f, compress='lz4')
   #del clf
   #with open(f"./models/{var}/{clf_name}_{var}.joblib", 'rb') as f:
   # clf = load(f)
   y_score = clf.predict(X_test)
   prc = precision_score(Y_test,y_score, average="weighted")
   recall  = recall_score(Y_test,y_score, average="weighted")
   roc_auc = roc_auc_score(Y_test, y_score)
   #roc_auc = roc_auc_score(Y_test, np.argmax(y_score, axis=1))
   accuracy = accuracy_score(Y_test, y_score)
   #score = clf.score(X_train, Y_train)
   #matrix = confusion_matrix(np.argmax(Y_test, axis=1), np.argmax(y_score, axis=1))
   matrix = confusion_matrix(Y_test, y_score)

   # explain all the predictions in the test set
   #background = shap.kmeans(X_train, 6)
   explainer = shap.KernelExplainer(clf.predict, background)
   del clf, X_train
   background = X_test[np.random.choice(X_test.shape[0], 1000, replace=False)]
   shap_values = explainer.shap_values(background)
   plt.figure()
   shap.summary_plot(shap_values, background, feature_names, show=False)
   #shap.plots.waterfall(shap_values[0], max_display=15)
   plt.savefig(f"./models/{var}/{clf_name}_{var}_features.pdf", format='pdf', dpi=1000, bbox_inches='tight')
   finish = (time.perf_counter()-start)/60
   with open(output, 'a') as f:
        f.write(f"{clf_name}\t{np.mean(score['train_roc_auc'])}\t{np.mean(score['test_roc_auc'])}\t{np.mean(score['train_neg_log_loss'])}\t{np.mean(score['test_neg_log_loss'])}\t{prc}\t{recall}\t{roc_auc}\t{accuracy}\t{finish}\n{matrix}\n")
   return None

if __name__ == "__main__":
    #Classifiers I wish to use
    classifiers = [
        	DecisionTreeClassifier(class_weight='balanced'),
            RandomForestClassifier(class_weight='balanced', n_jobs=-1),
            BalancedRandomForestClassifier(),
            GaussianNB(),
            LinearDiscriminantAnalysis(),
            GradientBoostingClassifier()
        ]
    
    
    with open("../../configs/columns_config.yaml") as fh:
        config_dict = yaml.safe_load(fh)

    var = 'nssnv'
    if not os.path.exists('models/'+var):
        os.makedirs('./models/'+var)
    output = "models/"+var+"/ML_results_"+var+"_.csv"
    #print('Working with '+var+' dataset...', file=open(output, "a"))
    print('Working with '+var+' dataset...')
    X_train, X_test, Y_train, Y_test, background, feature_names = data_parsing.remote(var,config_dict,output)
    with open(output, 'a') as f:
        f.write('Model\tCross_validate(avg_train_roc_auc)\tCross_validate(avg_test_roc_auc)\tCross_validate(avg_train_neg_log_loss)\tCross_validate(avg_test_neg_log_loss)\tPrecision(test_data)\tRecall\troc_auc\tAccuracy\tTime(min)\tConfusion_matrix[low_impact, high_impact]\n')
    remote_ml = [classifier.remote(i, var, X_train, X_test, Y_train, Y_test,  background, feature_names, output) for i in classifiers]
    ray.get(remote_ml)
    gc.collect()

