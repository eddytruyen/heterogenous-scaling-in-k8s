sed -E "s/(\{\"Parameter\":\{\"Name\":\"worker4\.replicaCount\",\"Resource\":\"\",\"Searchspace\":\{\"Min\":.,\"Max\":.,\"Granularity\":.},\"Prefix\":\"\",\"Suffix\":\"\"},\"Value\":\{\"Value\":.,\"Type\":\"int\"}}),\{\"Parameter\":\{\"Name\":\"worker4\.replicaCount\",\"Resource\":\"\",\"Searchspace\":\{\"Min\":.,\"Max\":.,\"Granularity\":.},\"Prefix\":\"\",\"Suffix\":\"\"},\"Value\":\{\"Value\":.,\"Type\":\"int\"}}/\1/g" results3.json | sed -E "s/(\{\"Parameter\":\{\"Name\":\"worker3\.replicaCount\",\"Resource\":\"\",\"Searchspace\":\{\"Min\":.,\"Max\":.,\"Granularity\":.},\"Prefix\":\"\",\"Suffix\":\"\"},\"Value\":\{\"Value\":.,\"Type\":\"int\"}}),\{\"Parameter\":\{\"Name\":\"worker3\.replicaCount\",\"Resource\":\"\",\"Searchspace\":\{\"Min\":.,\"Max\":.,\"Granularity\":.},\"Prefix\":\"\",\"Suffix\":\"\"},\"Value\":\{\"Value\":.,\"Type\":\"int\"}}/\1/g" | sed -E "s/(\{\"Parameter\":\{\"Name\":\"worker2\.replicaCount\",\"Resource\":\"\",\"Searchspace\":\{\"Min\":.,\"Max\":.,\"Granularity\":.},\"Prefix\":\"\",\"Suffix\":\"\"},\"Value\":\{\"Value\":.,\"Type\":\"int\"}}),\{\"Parameter\":\{\"Name\":\"worker2\.replicaCount\",\"Resource\":\"\",\"Searchspace\":\{\"Min\":.,\"Max\":.,\"Granularity\":.},\"Prefix\":\"\",\"Suffix\":\"\"},\"Value\":\{\"Value\":.,\"Type\":\"int\"}}/\1/g" | sed -E "s/(\{\"Parameter\":\{\"Name\":\"worker1\.replicaCount\",\"Resource\":\"\",\"Searchspace\":\{\"Min\":.,\"Max\":.,\"Granularity\":.},\"Prefix\":\"\",\"Suffix\":\"\"},\"Value\":\{\"Value\":.,\"Type\":\"int\"}}),\{\"Parameter\":\{\"Name\":\"worker1\.replicaCount\",\"Resource\":\"\",\"Searchspace\":\{\"Min\":.,\"Max\":.,\"Granularity\":.},\"Prefix\":\"\",\"Suffix\":\"\"},\"Value\":\{\"Value\":.,\"Type\":\"int\"}}/\1/g" > l
