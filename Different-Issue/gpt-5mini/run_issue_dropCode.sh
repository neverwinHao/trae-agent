#!/bin/bash
# Run trae-agent two-phase with dropCode issue style
cd /home/v-haoliu3/SWT_Models/trae-agent
bash Different-Issue/gpt-5mini/run_issue.sh dropCode ${1:-4}
