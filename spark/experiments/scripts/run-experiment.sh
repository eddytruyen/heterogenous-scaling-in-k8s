slo=35
group=g5
runs=1
home=/home/ubuntu/heterogenous-scaling-in-k8s/spark/experiments/scripts
current_dir=`pwd`
workload_profile=$home/udits/stable.yaml
output_dir=$home/udits/output
if [ ! -d $output_dir ]
then
       mkdir $output_dir
fi
for run in `seq $runs`
do
	echo Running run $run for group $group, slo $slo
	cd $home/../../../apps/matrix-generator/
	rm -r Results/exp3/silver*
	rm  Results/matrix.yaml
	rm Results/result-matrix.yaml
	python server.py conf/matrix-spark.yaml > log 2> err &
	sleep 3
	cd $home
	python generator.py start -f $workload_profile
	cp csv_output_file.csv $output_dir/csv_output_file_${group}_${slo}_${run}.csv
	cp ../../../apps/matrix-generator/Results/matrix.yaml $output_dir/matrix_${group}_${slo}_${run}.yaml
	kill %
done
cd $current_dir
