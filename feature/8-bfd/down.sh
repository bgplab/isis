#!/bin/bash
netlab config -q ifdown -l br
echo
echo -n "Interface shut down @ "
date +%H:%M:%S.%N
