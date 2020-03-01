#!/bin/bash

# Change the command line arguments as necessary to perform various experiments.
# See README.txt for an overview of the command line arguments as well as their
# default values.

echo Experiment Begin
counter=1
while  [ $counter -le 100 ]
do
    echo -e '\n*********************************************************'
    python2 intersection_simulation.py -l t -g 35 -r 13 -f 0.1 -a 6
    echo -e '\n*********************************************************'
    ((counter++))
done

echo Experiment Complete