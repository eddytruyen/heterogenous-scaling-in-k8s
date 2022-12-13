import os
from datetime import datetime

import pandas as pd
from pyspark.sql import SparkSession

from WorkloadSuite import WorkloadSuite

DATA_DIR = '../data/'


def get_names_of_workload_files():
    files = [file for file in os.listdir(DATA_DIR) if file.startswith("workloads-csv")]
    return files


def get_workload_suite_info(file_name):
    info = []
    with open(DATA_DIR + file_name, 'r') as file:
        lines = file.readlines()
        print(file)
        for i in range(len(lines)):
            trimmed_line = lines[i].strip()
            if trimmed_line.startswith("input"):
                print(trimmed_line)
                ws = WorkloadSuite()
                ws.get_info(trimmed_line, lines[i + 1].strip())
                if ws.bench_results is not None:
                    info.append(ws.bench_results)
    return info


if __name__ == '__main__':
    workload_files = get_names_of_workload_files()
    dataset_info = []
    spark = SparkSession.builder.appName("PySpark Read").getOrCreate()
    for file in workload_files:
        dataset_info.extend(get_workload_suite_info(file))
    spark.stop()
    if len(dataset_info) > 0:
        dataset = pd.concat(dataset_info)
        print(dataset.shape)
        dataset.to_csv(DATA_DIR + "dataset" + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".csv", index=False)
    else:
        print("no data")
