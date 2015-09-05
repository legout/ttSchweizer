#!/bin/bash

numberOdTests=0

for t in test*
do
 cd $t
 ./doTest.sh
 numberOdTests=$[numberOdTests + 1]
done

echo "$numberOdTests Tests executed"
