#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 01:11:09 2020

@author: tarunmamidi
"""
import time
import os
import numpy as np

np.random.seed(5)
import optuna
from optuna.integration import TFKerasPruningCallback
from optuna.integration.tensorboard import TensorBoardCallback
from optuna.samplers import TPESampler
import tensorflow as tf
import tensorflow.keras as keras
import argparse

# import ray
# Start Ray.
# ray.init(ignore_reinit_error=True)
try:
    tf.get_logger().setLevel("INFO")
except Exception as exc:
    print(exc)
import warnings

warnings.simplefilter("ignore")
# import ray
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize

# from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score,
    roc_auc_score,
    accuracy_score,
    confusion_matrix,
    recall_score,
)
import pandas as pd
import yaml
import matplotlib.pyplot as plt
import shap

# from joblib import dump, load


# EPOCHS = 150
class Objective(object):
    def __init__(self, train_x, val_x, test_x, train_y, val_y, test_y):

        self.train_x = train_x
        self.test_x = test_x
        self.train_y = train_y
        self.test_y = test_y
        self.val_x = val_x
        self.val_y = val_y
        # self.var = var
        # self.x = x
        # self.n_columns = 112
        # self.CLASS = 2

    def __call__(self, config):
        # Clear clutter from previous TensorFlow graphs.
        tf.keras.backend.clear_session()

        # Metrics to be monitored by Optuna.
        if tf.__version__ >= "2":
            monitor = "val_accuracy"
        else:
            monitor = "val_acc"
        n_layers = config.suggest_int("n_layers", 1, 30)
        model = Sequential()
        model.add(
            Dense(
                self.train_x.shape[1],
                input_shape=(self.train_x.shape[1],),
                activation=config.suggest_categorical(
                    "activation",
                    [
                        "tanh",
                        "softmax",
                        "elu",
                        "softplus",
                        "softsign",
                        "relu",
                        "sigmoid",
                        "hard_sigmoid",
                        "linear",
                    ],
                ),
            )
        )
        for i in range(n_layers):
            num_hidden = config.suggest_int("n_units_l{}".format(i), 1, 200)
            model.add(
                Dense(
                    num_hidden,
                    name="dense_l{}".format(i),
                    kernel_initializer=config.suggest_categorical(
                        "kernel_initializer_l{}".format(i),
                        [
                            "uniform",
                            "lecun_uniform",
                            "normal",
                            "zero",
                            "glorot_normal",
                            "glorot_uniform",
                            "he_normal",
                            "he_uniform",
                        ],
                    ),
                    activation=config.suggest_categorical(
                        "activation_l{}".format(i),
                        [
                            "tanh",
                            "softmax",
                            "elu",
                            "softplus",
                            "softsign",
                            "relu",
                            "sigmoid",
                            "hard_sigmoid",
                            "linear",
                        ],
                    ),
                )
            )
            model.add(
                Dropout(
                    config.suggest_float("dropout_l{}".format(i), 0.0, 0.9),
                    name="dropout_l{}".format(i),
                )
            )
        model.add(
            Dense(
                units=self.train_y.shape[1],
                name="dense_last",
                kernel_initializer=config.suggest_categorical(
                    "kernel_initializer",
                    [
                        "uniform",
                        "lecun_uniform",
                        "normal",
                        "zero",
                        "glorot_normal",
                        "glorot_uniform",
                        "he_normal",
                        "he_uniform",
                    ],
                ),
                activation="sigmoid",
            )
        )
        model.compile(
            loss="binary_crossentropy",
            optimizer=config.suggest_categorical(
                "optimizer",
                ["SGD", "RMSprop", "Adagrad", "Adadelta", "Adam", "Adamax", "Nadam"],
            ),
            metrics=["accuracy"],
        )
        # model.summary()
        # Create callbacks for early stopping and pruning.
        callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=10),
            TFKerasPruningCallback(config, monitor),
        ]

        # Train the model
        model.fit(
            self.train_x,
            self.train_y,
            validation_data=(self.val_x, self.val_y),
            verbose=0,
            shuffle=True,
            callbacks=callbacks,
            batch_size=config.suggest_int("batch_size", 100, 1000),
            epochs=150,
        )

        # Evaluate the model accuracy on the validation set.
        score = model.evaluate(self.val_x, self.val_y, verbose=0)
        return score[1]

    def tuned_run(self, config):
        # Clear clutter from previous TensorFlow graphs.
        print("running tuned params\n")
        tf.keras.backend.clear_session()
        model = Sequential()
        model.add(
            Dense(
                self.train_x.shape[1],
                input_shape=(self.train_x.shape[1],),
                activation=config["activation"],
            )
        )
        for i in range(config["n_layers"]):
            model.add(
                Dense(
                    config["n_units_l{}".format(i)],
                    name="dense_l{}".format(i),
                    kernel_initializer=config["kernel_initializer_l{}".format(i)],
                    activation=config["activation_l{}".format(i)],
                )
            )
            model.add(Dropout(config["dropout_l{}".format(i)]))
        model.add(
            Dense(
                units=self.train_y.shape[1],
                name="dense_last",
                kernel_initializer=config["kernel_initializer"],
                activation="sigmoid",
            )
        )
        model.compile(
            loss="binary_crossentropy",
            optimizer=config["optimizer"],
            metrics=["accuracy"],
        )
        # model.summary()
        # Train the model
        model.fit(
            self.train_x,
            self.train_y,
            verbose=2,
            batch_size=config["batch_size"],
            epochs=500,
        )
        # Evaluate the model accuracy on the validation set.
        # score = model.evaluate(test_x, test_y, verbose=0)
        return model

    def show_result(self, study, var, output, feature_names):
        pruned_trials = [
            t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED
        ]
        complete_trials = [
            t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE
        ]
        print("Study statistics: ")
        print("  Number of finished trials: ", len(study.trials))
        print("  Number of pruned trials: ", len(pruned_trials))
        print("  Number of complete trials: ", len(complete_trials))
        print("Best trial:")
        trial = study.best_trial
        print("  Value: ", trial.value)
        print("  Params: ")
        for key, value in trial.params.items():
            print("    {}: {}".format(key, value))
        print(
            f"NeuralNetwork_{var}:  {trial.params}",
            file=open(f"../tuning/tuned_parameters.csv", "a"),
        )

        model = self.tuned_run(trial.params)
        print("ran tuned model\n")
        results = model.evaluate(self.test_x, self.test_y)
        y_score = model.predict(self.test_x)
        prc = precision_score(self.test_y, y_score.round(), average="weighted")
        recall = recall_score(self.test_y, y_score.round(), average="weighted")
        roc_auc = roc_auc_score(self.test_y, y_score.round())
        accuracy = accuracy_score(self.test_y, y_score.round())
        # prc_micro = average_precision_score(self.test_y, y_score, average='micro')
        matrix = confusion_matrix(
            np.argmax(self.test_y.values, axis=1), np.argmax(y_score, axis=1)
        )
        print(
            f"Model\tTest_loss\tTest_accuracy\tPrecision\tRecall\troc_auc\tAccuracy\tConfusion_matrix[low_impact, high_impact]",
            file=open(output, "a"),
        )  # \tConfusion_matrix[low_impact, high_impact]
        print(
            f"Neural_Network\t{results[0]}\t{results[1]}\t{prc}\t{recall}\t{roc_auc}\t{accuracy}\n{matrix}",
            file=open(output, "a"),
        )  # results:\nstorage ="sqlite:///../tuning/{var}/Neural_network_{var}.db"
        # Calling `save('my_model')` creates a SavedModel folder `my_model`.
        model.save(f"../tuning/{var}/Neural_network/Neural_network_{var}")
        model.save_weights(f"../tuning/{var}/Neural_network/weights.h5")

        # explain all the predictions in the test set
        background = shap.kmeans(self.train_x, 10)
        explainer = shap.KernelExplainer(model.predict, background)
        background = self.test_x[
            np.random.choice(self.test_x.shape[0], 10000, replace=False)
        ]
        shap_values = explainer.shap_values(background)
        plt.figure()
        shap.summary_plot(shap_values, background, feature_names, show=False)
        # shap.plots.beeswarm(shap_vals, feature_names)
        # shap.plots.waterfall(shap_values[1], max_display=10)
        plt.savefig(
            f"../tuning/{var}/Neural_network_{var}_features.pdf",
            format="pdf",
            dpi=1000,
            bbox_inches="tight",
        )
        del background, shap_values, model, study
        return None


def data_parsing(var, config_dict, output):
    os.chdir(
        "/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/train_test"
    )
    # Load data
    # print(f'\nUsing merged_data-train_{var}..', file=open(output, 'a'))
    X_train = pd.read_csv(f"train_{var}/merged_data-train_{var}.csv")
    # var = X_train[config_dict['ML_VAR']]
    X_train = X_train.drop(config_dict["ML_VAR"], axis=1)
    X_train.replace([np.inf, -np.inf], np.nan, inplace=True)
    X_train.fillna(0, inplace=True)
    feature_names = X_train.columns.tolist()
    X_train = X_train.values
    Y_train = pd.read_csv(f"train_{var}/merged_data-y-train_{var}.csv")
    Y_train = pd.get_dummies(Y_train)
    # Y_train = label_binarize(Y_train.values, classes=['low_impact', 'high_impact']).ravel()
    X_train, X_val, Y_train, Y_val = train_test_split(
        X_train, Y_train, test_size=0.20, random_state=42
    )

    X_test = pd.read_csv(f"test_{var}/merged_data-test_{var}.csv")
    # var = X_test[config_dict['ML_VAR']]
    X_test = X_test.drop(config_dict["ML_VAR"], axis=1)
    # feature_names = X_test.columns.tolist()
    X_test = X_test.values
    Y_test = pd.read_csv(f"test_{var}/merged_data-y-test_{var}.csv")
    Y_test = pd.get_dummies(Y_test)
    # Y_test = label_binarize(Y_test.values, classes=['low_impact', 'high_impact']).ravel()
    print(f"Shape: {Y_train.shape}")
    print("Data Loaded!")
    # scaler = StandardScaler().fit(X_train)
    # X_train = scaler.transform(X_train)
    # X_test = scaler.transform(X_test)
    # explain all the predictions in the test set
    return X_train, X_val, X_test, Y_train, Y_val, Y_test, feature_names


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--var-tag",
        "-v",
        type=str,
        default="nssnv",
        help="Var tag used while filtering or untuned models. (Default: nssnv)",
    )

    args = parser.parse_args()

    var = args.var_tag

    os.chdir(
        "/data/project/worthey_lab/projects/experimental_pipelines/tarun/ditto/data/processed/train_test"
    )
    with open("../../../configs/columns_config.yaml") as fh:
        config_dict = yaml.safe_load(fh)

    start = time.perf_counter()
    if not os.path.exists("../tuning/" + var):
        os.makedirs("../tuning/" + var)
    output = "../tuning/" + var + "/ML_results_" + var + ".csv"
    # print('Working with '+var+' dataset...', file=open(output, "w"))
    print("Working with " + var + " dataset...")
    # X_train, X_test, Y_train, Y_test, feature_names = ray.get(data_parsing.remote(var,config_dict,output))
    X_train, X_val, X_test, Y_train, Y_val, Y_test, feature_names = data_parsing(
        var, config_dict, output
    )
    # print('Model\tCross_validate(avg_train_score)\tCross_validate(avg_test_score)\tPrecision(test_data)\tRecall\troc_auc\tAccuracy\tTime(min)\tConfusion_matrix[low_impact, high_impact]', file=open(output, "a"))    #\tConfusion_matrix[low_impact, high_impact]
    # list1 = ray.get(classifier.remote(classifiers,var, X_train, X_test, Y_train, Y_test,background,feature_names))
    # print(f'{list1[0]}\t{list1[1]}\t{list1[2]}\t{list1[3]}\t{list1[4]}\t{list1[5]}\t{list1[6]}\t{list1[7]}\n{list1[8]}', file=open(output, "a"))
    # print(f'training and testing done!')

    print("Starting Objective...")
    objective = Objective(X_train, X_val, X_test, Y_train, Y_val, Y_test)
    tensorboard_callback = TensorBoardCallback(
        f"../tuning/{var}/Neural_network_{var}_logs/", metric_name="accuracy"
    )
    study = optuna.create_study(
        sampler=TPESampler(**TPESampler.hyperopt_parameters()),
        study_name=f"Neural_network_{var}",
        storage=f"sqlite:///../tuning/{var}/Neural_network_{var}.db",  # study_name= "Ditto3",
        direction="maximize",
        pruner=optuna.pruners.MedianPruner(n_startup_trials=100),
        load_if_exists=True,  # , pruner=optuna.pruners.MedianPruner(n_startup_trials=150)
    )
    # study = optuna.load_study(study_name= "Ditto_all", sampler=TPESampler(**TPESampler.hyperopt_parameters()),storage ="sqlite:///Ditto_all.db") # study_name= "Ditto3",
    study.optimize(
        objective,
        n_trials=1000,
        callbacks=[tensorboard_callback],
        n_jobs=-1,
        gc_after_trial=True,
    )  # , n_jobs = -1 timeout=600,
    finish = (time.perf_counter() - start) / 120
    # ttime = (finish- start)/120
    print(f"Total time in hrs: {finish}")
    objective.show_result(study, var, output, feature_names)
    del X_train, X_test, Y_train, Y_test, feature_names