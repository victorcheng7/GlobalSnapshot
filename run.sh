#!/bin/bash
function runTests {
    for f in $1/*.in; do
	filename=$(basename "$f")
	filename="${filename%.*}"
	./asg2 $filename $1/setup $f > $1/$filename.out &
    done
}

function checkOutputs {
    for f in $1/*.exp; do
	filename=$(basename "$f")
	filename="${filename%.*}"
	./testOutput $f $1/$filename.out > temp
	if grep FAILED temp; then
	    cat $1/$filename.out
	fi
    done
}

function runAllTests {
    let num_test_cases=1
    for d in ./tests/*; do
	if [[ ! -d $d ]]; then
	    continue
	fi
	echo TESTCASE $num_test_cases:
	runTests $d
	while ps | grep -q asg2; do
	    sleep 1
	done
	checkOutputs $d
	num_test_cases=$[num_test_cases+1]
    done
    rm temp
}

runAllTests
