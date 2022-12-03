import os
from datetime import datetime

import pandas as pd
from pyspark.sql import SparkSession

import PerfModel
from WorkloadSuite import WorkloadSuite

DATA_DIR = "./data/"


def get_names_of_workload_files():
    files = [file for file in os.listdir(DATA_DIR) if file.startswith("workloads-csv")]
    return files


def get_workload_suite_info(file_name):
    info = []
    with open(DATA_DIR + file_name, "r") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            trimmed_line = lines[i].strip()
            if trimmed_line.startswith("input"):
                ws = WorkloadSuite()
                ws.get_train_info(trimmed_line, lines[i + 1].strip())
                if ws.bench_results is not None:
                    info.append(ws.bench_results)
    return info


def transform_data(data):
    data["tot_cpu"] = data.w1_num * data.w1_cpu + data.w2_num * data.w2_cpu + data.w3_num * data.w3_cpu + data.w4_num * data.w4_cpu
    data["tot_mem"] = data.w1_num * data.w1_mem + data.w2_num * data.w2_mem + data.w3_num * data.w3_mem + data.w4_num * data.w4_mem
    # standardisation = preprocessing.StandardScaler()
    X_cols = ["time", "nr_query_cols", "nr_query_conds", "nr_data_rows", "nr_data_cols", "nr_users"]
    y_cols = ["tot_cpu", "tot_mem"]
    X = data[X_cols]
    y = data[y_cols]
    # X = pd.DataFrame(X, columns=X_cols)
    return pd.concat([X, y], axis=1), X, y


if __name__ == "__main__":
    workload_files = get_names_of_workload_files()
    dataset_info = []
    spark = SparkSession.builder.appName("PySpark Read").getOrCreate()
    for file in workload_files:
        dataset_info.extend(get_workload_suite_info(file))
    spark.stop()
    print("len\t", len(dataset_info))
    if len(dataset_info) > 0:
        #print(dataset_info)
        print(type(dataset_info))
        dataset, X, y = transform_data(pd.concat(dataset_info))
        cur_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        dataset.to_csv(DATA_DIR + "dataset_" + cur_time + ".csv", index=False)
        models = PerfModel.train_perf_model(X, y)
        metrics = pd.DataFrame([PerfModel.get_metrics(model, X, y) for model in models])
        metrics.to_csv(DATA_DIR + "metrics_" + cur_time + ".csv", index=False)
