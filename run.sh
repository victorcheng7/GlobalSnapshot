#!/bin/bash
function runTests {
	let port_num=5001
	for f in $1/*.in; do
		filename=$(basename "$f")
		filename="${filename%.*}"
		./asg1 $port_num $f > $1/$filename.out &
		port_num=$[port_num+1]
	done
}

function checkOutputs {
	for f in $1/*.exp; do
		filename=$(basename "$f")
		filename="${filename%.*}"
		./testOutput $f $1/$filename.out
	done
}

function runAllTests {
	let num_test_cases=1
	for d in ./tests/*; do
		echo TESTCASE $num_test_cases:
		runTests $d
		while ps | grep -q asg1; do
			sleep 1
		done
		checkOutputs $d
		num_test_cases=$[num_test_cases+1]
	done
}

runAllTests
