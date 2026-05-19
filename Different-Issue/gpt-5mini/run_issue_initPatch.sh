#!/bin/bash
# Run trae-agent two-phase with initPatch issue style
cd /home/v-haoliu3/SWT_Models/trae-agent
bash Different-Issue/gpt-5mini/run_issue.sh initPatch ${1:-4}
