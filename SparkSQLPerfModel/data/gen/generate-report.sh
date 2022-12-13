rm report-g*.csv; for g in 0; do for t in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do sed "s/nbOfTenants: .*/nbOfTenants: $t/g" spark-heterogeneous-csv-kmeans-data-g0.yaml | sed "s/tenantGroup: \".*\"/tenantGroup: \"$g\"/g" > tmp.yaml; ./k8-resource-optimizer -x -c tmp.yaml -e sparkbenchbatch -p exhaustive -r results-csv-kmeans-data-g0.json; cat report.csv >> report-g$g-t$t.csv; done; done
