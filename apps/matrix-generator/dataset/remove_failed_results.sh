sed 's/{"namespaces":[{"name":"silver","chart":{"Name":"spark","DirPath":"/home/ubuntu/go/src/k8-resource-optimizer/examples/charts/bitnami-heterogeneous/spark"},"config":{"Settings":[{"
Parameter":{"Name":"worker1.replicaCount","Resource":"","Searchspace":{"Min":0,"Max":0,"Granularity":1},"Prefix":"","Suffix":""},"Value":{"Value":0,"Type":"int"}},{"Parameter":{"Name":"work
er2.replicaCount","Resource":"","Searchspace":{"Min":1,"Max":1,"Granularity":1},"Prefix":"","Suffix":""},"Value":{"Value":1,"Type":"int"}},{"Parameter":{"Name":"worker3.replicaCount","Resou
rce":"","Searchspace":{"Min":0,"Max":0,"Granularity":1},"Prefix":"","Suffix":""},"Value":{"Value":0,"Type":"int"}},{"Parameter":{"Name":"worker4.replicaCount","Resource":"","Searchspace":{"
Min":2,"Max":2,"Granularity":1},"Prefix":"","Suffix":""},"Value":{"Value":.*,"Type":"int"}},{"Parameter":{"Name":"worker1.resources.requests.cpu","Resource":"CPU","Searchspace":{"Min":.*,"Max":.*,"Granularity":1},"Prefix":"","Suffix":""},"Value":{"Value":.*,"Type":"int"}},{"Parameter":{"Name":"worker1.resources.requests.memory","Resource":"Mem","Searchspace":{"Min":.*,"Max":.*,"Granularity":1},"Prefix":"","Suffix":"Gi"},"Value":{"Value":.*,"Type":"int"}},{"Parameter":{"Name":"worker2.resources.requests.cpu","Resource":"CPU","Searchspace":{"Min":.*,"Max":.*,"Granularity":1},"Prefix":"","Suffix":""},"Value":{"Value":.*,"Type":"int"}},{"Parameter":{"Name":"worker2.resources.requests.memory","Resource":"Mem","Searchspace":{"Min":.*,"Max":.*,"Granularity":.*},"Prefix":"","Suffix":"Gi"},"Value":{"Value":.*,"Type":"int"}},{"Parameter":{"Name":"worker3.resources.requests.cpu","Resource":"CPU","Searchspace":{"Min":.*,"Max":.*,"Granularity":1},"Prefix":"","Suffix":""},"Value":{"Value":.*,"Type":"int"}},{"Parameter":{"Name":"worker3.resources.requests.memory","Resource":"Mem","Searchspace":{"Min":.*,"Max":.*,"Granularity":1},"Prefix":"","Suffix":"Gi"},"Value":{"Value":.*,"Type":"int"}},{"Parameter":{"Name":"worker4.resources.requests.cpu","Resource":"CPU","Searchspace":{"Min":.*,"Max":.*,"Granularity":1},"Prefix":"","Suffix":""},"Value":{"Value":.*,"Type":"int"}},{"Parameter":{"Name":"worker4.resources.requests.memory","Resource":"Mem","Searchspace":{"Min":.*,"Max":.*,"Granularity":1},"Prefix":"","Suffix":"Gi"},"Value":{"Value":.*,"Type":"int"}}]},"nboftenants":.*}],"experiment":{"Iteration":.*,"Sample":.*,"SparkBenchconfig":{"Name":"","SLOs":[{"Name":"silver","Workload":"sql","NrOfTenants":.*,"ScriptPath":"/tmp/sparkbenchwrap/silver/run-bench.sh","ConfPath":"/tmp/sparkbenchwrap/silver/output.conf","TenantGroup":"2","BenchPath":"/mnt/nfs-disk-2/spark-bench/","ReleaseName":"silver-spark"}],"Users":.*},"OutputDir":".*","Type":"SparkBenchBatchExperiment","Failed":true}},"result":{"Results":[{"name":"silver","Duration":.*,"Successfull":false}],"Type":"SparkBenchBatchExperimentResult","Failed":true}}
