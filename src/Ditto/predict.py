#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
import yaml
import warnings
warnings.simplefilter("ignore")
from joblib import dump, load

import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    "-i",
    type=str,
    required=True,
    help="Input data file with path")
parser.add_argument(
    "--output",
    "-o",
    type=str,
    required=True,
    help="Output data file with path")
parser.add_argument(
    "--output500",
    "-o5",
    type=str,
    required=True,
    help="Output data file with path for Top 500 variants")
args = parser.parse_args()

#os.chdir('/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/')

print("Loading data....")

#with open('SL212589_genes.yaml') as fh:
#        config_dict = yaml.safe_load(fh)

X = pd.read_csv(args.input)
X_test = X
print('Data Loaded!')
#overall.loc[:, overall.columns.str.startswith('CLN')]
var = X_test[config_dict['ML_VAR']]
X_test = X_test.drop(config_dict['ML_VAR'], axis=1)
#feature_names = X_test.columns.tolist()
X_test = X_test.values

with open("/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/models/F_3_0_1_nssnv/StackingClassifier_F_3_0_1_nssnv.joblib", 'rb') as f:
    clf = load(f)

print('Ditto Loaded!\nRunning predictions.....')


#SL135596	MSTO1 	MYOPATHY, MITOCHONDRIAL, AND ATAXIA		MSTO1(NM_018116.3,c.676C>T,p.Gln226Ter,Likely Pathogenic);	MSTO1(NM_018116.3,c.971C>T,p.Thr324Ile,VUS)

y_score = model.predict(X_test)
del X_test
print('Predictions finished!Sorting ....')
pred = pd.DataFrame(y_score, columns = ['pred_Benign', 'pred_Pathogenic'])

overall = pd.concat([var, pred], axis=1)

overall = overall.merge(X,on='ID')
#overall['hazel'] = X['Gene.refGene'].map(config_dict)
del X, pred, y_score
overall.drop_duplicates(inplace=True)
overall = overall.reset_index(drop=True)
overall = overall.sort_values('pred_Pathogenic', ascending=False)
overall.head(500).to_csv(args.output500, index=False)
overall = overall.sort_values([ 'CHROM', 'POS'])
#columns = overall.columns
print('writing to database...')
#overall.head(500).to_csv('predicted_results_500_SL212589.tsv', sep='\t', index=False)
overall.to_csv(args.output, index=False)
#overall.loc[:, overall.columns.str.startswith('CLNS')]

#df1 = overall.iloc[:, :90]
#df2 = overall.iloc[:, 90:]
#df2 = pd.concat([df1['ID'], df2], axis=1)
#del overall
#store = pd.HDFStore("predicted_results_SL212589.h5")
#store.append("SL212589", overall, min_itemsize={"values": 100}, data_columns=columns)
#overall.to_hdf("predicted_results_SL212589.h5", "SL212589", format="table", mode="w")
#pd.read_hdf("store_tl.h5", "table", where=["index>2"])
#from sqlalchemy import event
#engine1 = create_engine('sqlite:///SL212589_1.db', echo=True, pool_pre_ping=True)
#engine = create_engine('sqlite:///SL212589.db', echo=True, pool_pre_ping=True)
#sqlite_connection = engine.connect()
#sqlite_connection1 = engine1.connect()
#sqlite_table = 'SL212589'
#overall.to_sql(sqlite_table, sqlite_connection, index=False, if_exists="append", chunksize=10000, method='multi') #chunksize=10000,
#
#df1.to_sql(sqlite_table, sqlite_connection, if_exists='fail')
#df2.to_sql(sqlite_table, sqlite_connection1, if_exists='fail')
#sqlite_connection.close()
print('Database storage complete!')
