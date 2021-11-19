#!/bin/bash

function restart() {
	sudo rm -r Results/exp3/silver
	echo "import pdb;" >> src/generator.py
	git stash
}
	

if [ $1 == "0003" ]
then
	count=`ls -l test0003*.sh | wc -l`
	echo "Running $count test scripts"
	count=`expr $count - 1`
	for i in `seq 0 $count` 
	do
		restart
		bash -x ./test0003-$i.sh
	done
elif [ $1 == "0100" ] 
then
	for i in `seq 9`
	do
		restart
		bash -x ./test$i.sh
	done
elif [ $1 == "0100-v2" ]
then
	for i in `seq 13 15`
	do
		restart
                bash -x ./test$i.sh
		sleep 5
        done
fi




