
import os


__all__ = ['node_list', 'submission_script']


def node_list(host_name):
    """
    Attempt to find a node list for PBS clusters.

    Parameters
    ----------
    host_name

    Returns
    -------

    """
    pbs_nodes = os.environ.get('PBS_NODEFILE', None)

    if pbs_nodes is None:
        return

    pbs_list = []
    with open(pbs_nodes, 'r') as file:
        lines = file.readlines()

        for line in lines:
            line = line.split(' ')

            if line[0] != host_name:
                pbs_list.append(line[0])

    return pbs_list


def submission_script(name, num_nodes, num_workers, num_threads, node_memory):
    """
    Generate a submission script for PBS clusters.

    Parameters
    ----------
    name
    num_nodes
    num_workers
    num_threads
    node_memory

    Returns
    -------
    str

    """

    return f"""#!/bin/bash -l

name={name}
num_nodes={num_nodes}
num_workers_per_node={num_workers}
num_threads_per_worker={num_threads}

#PBS -N {name}
#PBS -l walltime=48:00:00
#PBS -l select={num_nodes+1}:ncpus={num_threads*num_workers}:mpiprocs={num_workers}:ompthreads={num_threads}:mem={node_memory}GB
#PBS -l place=scatter:excl
#PBS -o out.log
#PBS -e err.log
#PBS -q <queue_name>

# load any modules before activating the conda env
# for example:
# module load anaconda3/personal

# activate conda environment
conda activate stride

# set number of threads per process
# use $(ppn) to use one worker per node and as many threads pr worker as cores in the node
export OMP_NUM_THREADS=$num_threads_per_worker

# set any environment variables
# for example:
# export DEVITO_COMPILER=icc

# run our job
ls -l
date
mrun -n $num_nodes -nw $num_workers_per_node -nth $num_threads_per_worker python forward.py &> $name-output.log
date

stat=$?
echo "Exit status: $stat" >> "$name-output.log"
"""
