#!/bin/bash
# Run trae-agent two-phase with initTest issue style
cd /home/v-haoliu3/SWT_Models/trae-agent
bash Different-Issue/gpt-5mini/run_issue.sh initTest ${1:-4}
