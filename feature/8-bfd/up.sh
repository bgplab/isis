#!/bin/bash
netlab config -q ifup -l br
echo
echo -n "Link restored @ "
date +%H:%M:%S.%N
