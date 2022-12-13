import os

import pandas as pd
from pyspark.sql import SparkSession

DATA_DIR = "./data/"
MOUNT_DATA_DIR = "/mnt/nfs-disk-2/spark-bench-test/"


class WorkloadSuite:
    def __init__(self):
        self.nr_conds_in_query = None
        self.nr_cols_selected_in_query = None
        self.nr_cols_in_data = None
        self.nr_rows_in_data = None
        self.tenant_id = None
        self.tenant_group = None
        self.file_name = None
        self.report_name = None
        self.bench_results = None

    def __str__(self):
        return f"{self.report_name}, {self.bench_results}, {self.tenant_group}, {self.tenant_id}, " \
               f"{self.nr_cols_selected_in_query}, {self.nr_conds_in_query}, " \
               f"{self.nr_cols_in_data}, {self.nr_rows_in_data}, {self.file_name}"

    def __get_tenant_info(self, input_line):
        start = input_line.rfind("/")
        end = input_line.rfind(".")
        end_file = input_line.rfind('"')
        tenant_info = input_line[start:end].split("-")[-2:]
        self.tenant_group, self.tenant_id = tenant_info[0][1:], tenant_info[1]
        self.file_name = input_line[start + 1:end_file]
        self.report_name = "report-g" + self.tenant_group + "-t" + self.tenant_id + ".csv"

    def __get_bench_results(self):
        if not os.path.exists(DATA_DIR + self.report_name):
            return None
        renamed_cols = ["w1_num", "w1_cpu", "w1_mem", "w2_num", "w2_cpu", "w2_mem", "w3_num", "w3_cpu",
                        "w3_mem", "w4_num", "w4_cpu", "w4_mem", "time"]
        df = pd.read_csv(DATA_DIR + self.report_name, sep="\t")
        df = df[df.Successfull].iloc[:, 1:-1]
        df.drop(["SLAName", "Successfull", "Timestamp"], axis=1, inplace=True)
        df.columns = renamed_cols
        self.bench_results = df

    def __get_query_info(self, query_line):
        start_of_select_substring = query_line.find("select")
        select_str = query_line[start_of_select_substring:]
        length_of_select = len("select ")
        start_of_from_substring = select_str.find(" from")
        self.nr_cols_selected_in_query = len(select_str[length_of_select:start_of_from_substring].split(","))
        length_of_where = len("where ")
        start_of_where_substring = select_str.find(" where ")
        self.nr_conds_in_query = len(select_str[start_of_where_substring + length_of_where:].split("and"))

    def __get_data_info(self):
        spark = SparkSession.builder.appName("PySpark Read").getOrCreate()
        df = spark.read.option("header", "true").csv(MOUNT_DATA_DIR + self.file_name)
        self.nr_rows_in_data = df.count()
        self.nr_cols_in_data = len(df.columns)

    def get_train_info(self, input_line, query_line):
        self.__get_tenant_info(input_line)
        self.__get_bench_results()
        if self.bench_results is not None:
            self.__get_query_info(query_line)
            self.__get_data_info()
            self.bench_results["nr_query_cols"] = self.nr_cols_selected_in_query
            self.bench_results["nr_query_conds"] = self.nr_conds_in_query
            self.bench_results["nr_data_cols"] = self.nr_cols_in_data
            self.bench_results["nr_data_rows"] = self.nr_rows_in_data
            self.bench_results["nr_users"] = self.tenant_id

    def get_predict_info(self, input_line, query_line):
        self.__get_tenant_info(input_line)
        self.__get_query_info(query_line)
        self.__get_data_info()
        self.bench_results = {}
        self.bench_results["nr_query_cols"] = self.nr_cols_selected_in_query
        self.bench_results["nr_query_conds"] = self.nr_conds_in_query
        self.bench_results["nr_data_cols"] = self.nr_cols_in_data
        self.bench_results["nr_data_rows"] = self.nr_rows_in_data


