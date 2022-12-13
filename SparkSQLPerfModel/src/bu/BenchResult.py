import pandas as pd
import os


def get_bench_result(file_path):
    if not os.path.exists(file_path):
        return None
    renamed_cols = ['config_#', 'w1_num', 'w1_cpu', 'w1_mem', 'w2_num', 'w2_cpu', 'w2_mem', 'w3_num', 'w3_cpu',
                    'w3_mem', 'w4_num', 'w4_cpu', 'w4_mem', 'sla', 'time', 'success', '']
    df = pd.read_csv(file_path, sep='\t', names=renamed_cols, header=None, skiprows=1).iloc[:, 1:-1]
    df = df[df.success]
    df.drop(['sla', 'success'], axis=1, inplace=True)
    return df
