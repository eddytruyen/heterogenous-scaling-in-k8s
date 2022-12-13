import pickle

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

MODEL_DIR = "../model/"


def __perform_grid_search(model, hyperparams, X_train, y_train):
    grid = GridSearchCV(model, hyperparams, cv=5, scoring="neg_root_mean_squared_error", n_jobs=-1)
    grid.fit(X_train, y_train)
    return grid


def __save_model(model):
    model_file_name = model.estimator.__class__.__name__ + ".pickle"
    pickle.dump(model, open(MODEL_DIR + model_file_name, "wb"))


def train_perf_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
    print("Training...")
    neigh = KNeighborsRegressor()
    neigh_hyperparams = {"n_neighbors": range(25, 100), "algorithm": ["auto", "brute"],
                         "leaf_size": [5, 10, 15], "weights": ["uniform", "distance"],
                         "metric": ["euclidean", "minkowski"]}
    neigh_grid = __perform_grid_search(neigh, neigh_hyperparams, X_train, y_train)

    tree = DecisionTreeRegressor()
    tree_hyperparams = {"criterion": ["squared_error", "friedman_mse", "poisson"],
                        "max_depth": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15]}
    tree_grid = __perform_grid_search(tree, tree_hyperparams, X_train, y_train)

    forest = RandomForestRegressor()
    forest_hyperparams = {"criterion": ["squared_error"],
                          "max_depth": [4, 5, 6],
                          "n_estimators": [200, 250, 300, 350, 400, 500]
                          }
    forest_grid = __perform_grid_search(forest, forest_hyperparams, X_train, y_train)

    models = [neigh_grid, tree_grid, forest_grid]
    [__save_model(model) for model in models]
    return models


def get_metrics(model, data, actual):
    predicted = model.predict(data)
    actual_cpu = actual.iloc[:, 0]
    actual_mem = actual.iloc[:, 1]
    predicted_cpu = predicted[:, 0]
    predicted_mem = predicted[:, 1]
    return {"model": model.estimator.__class__.__name__,
            "score": model.score(data, actual),
            "mse_cpu": mean_squared_error(actual_cpu, predicted_cpu),
            "mse_mem": mean_squared_error(actual_mem, predicted_mem),
            "mae_cpu": mean_absolute_error(actual_cpu, predicted_cpu),
            "mae_mem": mean_absolute_error(actual_mem, predicted_mem),
            "r2_cpu": r2_score(actual_cpu, predicted_cpu),
            "r2_mem": r2_score(actual_mem, predicted_mem),
            "adjusted_r2_cpu": (1 - ((1 - r2_score(actual_cpu, predicted_cpu)) * (
                    (data.shape[0] - 1) / (data.shape[0] - 1 - data.shape[1])))),
            "adjusted_r2_mem": (1 - ((1 - r2_score(actual_mem, predicted_mem)) * (
                    (data.shape[0] - 1) / (data.shape[0] - 1 - data.shape[1]))))}


def predict_perf_model(data, model_type=3):
    model_file_name = ""
    if model_type == 1:
        model_file_name = "KNeighborsRegressor.pickle"
    elif model_type == 2:
        model_file_name = "DecisionTreeRegressor.pickle"
    elif model_type == 3:
        model_file_name = "RandomForestRegressor.pickle"
    pickled_model = pickle.load(open(MODEL_DIR + model_file_name, "rb"))
    prediction = np.floor(pickled_model.predict(data))
    mean_prediction = np.mean(prediction, axis=1)
    prediction = np.floor(mean_prediction)
    # total_cpu = int(prediction[0][0])
    # total_mem = int(prediction[0][1])
    return prediction
