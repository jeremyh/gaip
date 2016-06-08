#!/bin/bash
#
# Start a NBAR run by submitting the run_NBAR.pbs script to the PBS queue
# This script initialises all the appropriate logging and job parameters
#
# Edit this file to get your run parameters (Inputs, outputs and resources)
#
# usage: ./submit_NBAR.sh 
#
#================================================================================
umask 007

# INPUTS (change any of these)
# ======

L1T_PATH=/short/v10/jps547/staging

# OUTPUTS (change any of these)
# =======

OUTPUT_ROOT=/g/data/v10/testing_ground/nbar-metadata
OUTPUT_PATH=$OUTPUT_ROOT/output
LOG_PATH=$OUTPUT_ROOT/logs
CFG_FILE=nbar.cfg

# RESOURCES
# =========

PROJECT='v10'           # <---- Change this as required
QUEUE='normal'          # <---- Change this as required
WALLCLOCK='01:30:00'    # <---- Change this depending on workload (see SOP)
NODES=1                 # <---- Change this depending on workload (see SOP)

let MEM_GB=32*$NODES    # don't touch
let NCPUS=16*$NODES     # don't touch
let JOBFS_MB=100*$NODES # don't touch

# JOB SPECS
# =========

MAIL_LIST="your.name@ga.gov.au"

# Create ouput directory

rm -r ${OUTPUT_ROOT}
mkdir -p ${OUTPUT_PATH}/nbar
mkdir -p ${OUTPUT_PATH}/nbart
mkdir -p ${LOG_PATH}


#================================================================================
HOSTNAME=`hostname`
PID=$$
LSPEC="walltime=${WALLCLOCK},ncpus=${NCPUS},mem=${MEM_GB}GB,jobfs=${JOBFS_MB}MB"
echo $LSPEC

# Submit the job

qsub -v L1T_PATH=$L1T_PATH,OUTPUT_PATH=$OUTPUT_PATH,LOG_PATH=$LOG_PATH,CFG_FILE=$CFG_FILE \
 -M $MAIL_LIST \
 -e $LOG_PATH/run_NBAR_${HOSTNAME}_${PID}.stderr \
 -o $LOG_PATH/run_NBAR_${HOSTNAME}_${PID}.stdout \
 -l $LSPEC \
 -q $QUEUE \
 -P $PROJECT \
 run_NBAR.pbs
