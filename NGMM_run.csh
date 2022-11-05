#!/bin/tcsh

# Set up conda and gurobi environment
conda activate /usr/local/usrapps/infews/group_env
module load gurobi
source /usr/local/apps/gurobi/gurobi810/linux64/bin/gurobi.sh

# Submit LSF job for the directory $dirName
bsub -n 8 -R "span[hosts=1]" -R "rusage[mem=20GB]" -W 5000 -x -o out.%J -e err.%J "python NGMM_wrapper.py"

conda deactivate
