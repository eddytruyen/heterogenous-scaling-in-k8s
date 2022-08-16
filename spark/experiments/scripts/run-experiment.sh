slo=50
group=g6
runs=1
home=/home/udits/githubrepos/heterogenous-scaling-in-k8s/spark/experiments/scripts
current_dir=`pwd`
workload_profile=$home/udits/on_off.yaml
output_dir=$home/udits/output
if [ ! -d $output_dir ]
then
       mkdir $output_dir
fi
cd $home/../../../apps/matrix-generator/
sed -i "s/completionTime: .*/completionTime: $slo/g" conf/matrix-spark.yaml
for run in `seq 1 $runs`
do
	echo Running run $run for group $group, slo $slo
	cd $home/../../../apps/matrix-generator/
	rm -r Results/exp3/silver*
	rm  Results/matrix.yaml
	rm Results/result-matrix.yaml
	ratio=`jq -n 1/$run`
	sed -i "s/searchWindow: .*/searchWindow: $run/g" conf/matrix-spark.yaml
	sed -i "s/sampling_ratio: .*/sampling_ratio: $ratio/g" conf/matrix-spark.yaml
	python server.py conf/matrix-spark.yaml &
	sleep 3
	cd $home
	python generator.py start -f $workload_profile
	cp csv_output_file.csv $output_dir/u_pf_csv_output_file_${group}_${slo}_${run}.csv
	cp ../../../apps/matrix-generator/Results/matrix.yaml $output_dir/pf_matrix_${group}_${slo}_${run}.yaml
	kill %
done
cd $current_dir
