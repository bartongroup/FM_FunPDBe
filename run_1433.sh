#!/bin/bash
#$ -t 1-18
#$ -tc 50
#$ -v PATH
#$ -cwd

# List of files to operate on...
# ls ./data/input/*.fasta > available_fasta.txt
SEEDFILE=available_fasta.txt
SEED=$(awk "NR==$SGE_TASK_ID" $SEEDFILE)

# Process
python run_predictors.py 1433pred $SEED