#!/bin/bash

# to generate API key: 
# st2 apikey create -k -m '{"used_by": "snmp"}'

export ST2_API_KEY=$SNMP_ST2_API_KEY
v=`st2 key get $1 -j | jq ".value|tonumber" 2>/dev/null`

if (( $? != 0 )); then
  echo "-1"
else
  echo "$v"
fi
