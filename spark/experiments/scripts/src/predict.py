import sys
import subprocess

import pandas as pd
import yaml

import PerfModel
from WorkloadSuite import WorkloadSuite

DATA_DIR = "../data/"


def get_workload_suite_info(file_name):
    info = []
    with open(file_name, "r") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            trimmed_line = lines[i].strip()
            if trimmed_line.startswith("input"):
                ws = WorkloadSuite()
                ws.get_predict_info(trimmed_line, lines[i + 1].strip())
                if ws.bench_results is not None:
                    ws.bench_results["time"] = completion_time
                    ws.bench_results["nr_users"] = nr_users
                    info.append(ws.bench_results)
    return info


if __name__ == "__main__":
    # python predict.py completionTime, args for rescale.sh
    print("Prediction phase...")
    print(sys.argv)
    if len(sys.argv) != 8:
        print("PROBLEM!")
    else:
        nr_users = sys.argv[2]
        with open("/home/udits/githubrepos/heterogenous-scaling-in-k8s/apps/matrix-generator/conf/matrix-spark.yaml", "r") as stream:
            parsed_yaml = yaml.safe_load(stream)
            completion_time = parsed_yaml["slas"][0]["slos"]["completionTime"]
        print("SLO\t", completion_time)
        output_conf_file = "/home/udits/githubrepos/heterogenous-scaling-in-k8s/spark/experiments/scripts/sql/output.conf"
        dataset_info = pd.DataFrame(get_workload_suite_info(output_conf_file))
        X_cols = ["time", "nr_query_cols", "nr_query_conds", "nr_data_rows", "nr_data_cols", "nr_users"]
        data = dataset_info[X_cols]
        print("Data\n", data)
        # time, nr_query_cols, nr_query_conds, nr_data_rows, nr_data_cols, nr_users = sys.argv[1:]
        # numeric_data = [float(val) for val in sys.argv[1:]]
        # data = np.array(numeric_data).reshape(1, -1)
        prediction = PerfModel.predict_perf_model(data)
        print("Prediction of the above data\n", prediction)
        command = ["/home/udits/githubrepos/heterogenous-scaling-in-k8s/spark/experiments/scripts/rescale.sh", sys.argv[1], sys.argv[2], str(completion_time), sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], str(0), str(int(prediction[0])), str(int(prediction[1]))]
        #command = command + [str(int(prediction[1]))]
        print("Command\n", command)
        subprocess.run(" ".join(command), shell=True)

        # print(*[PerfModel.predict_perf_model(data, i) for i in range(1, 4)])
