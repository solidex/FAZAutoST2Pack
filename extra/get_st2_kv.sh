#!/bin/bash
export ST2_API_KEY=<API_KEY, DO: st2 apikey create -k -m '{"used_by": "snmp"}'>
v=`st2 key get $1 -j | jq ".value|tonumber" 2>/dev/null`

if (( $? != 0 )); then
  echo "-1"
else
  echo "$v"
fi
