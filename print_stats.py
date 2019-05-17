#!/usr/bin/env python
# encoding: utf-8

import sys
import copy



total_statuses = {
}

for filename in sys.argv[1:]:
    ips = []
    statuses = {
       "available": 0,
       "closed": 0,
       "other": 0
    }
    versions = {}
    print(filename)
    with open(filename, 'r') as f:
        for row in f.readlines():
             ip, version = row.strip().split(",", 1)
             if ip in ips:
                 #print("Skipping duplicate ip %s"% ip)
                 continue
             ips.append(ip)
             if version.startswith("v1") or version.startswith("microsoft"):
                 statuses['available'] += 1
             elif version.startswith("timeout") or version.startswith("connection refused"):
                 statuses['closed'] += 1
             else:
                 statuses['other'] += 1
             version_start = '.'.join(version.split(".",2)[:1])
             if version_start not in versions:
                  versions[version_start] = 0
             versions[version_start] += 1
    
    print(versions)
    
    total_statuses[filename] = copy.deepcopy(statuses)


for filename in sorted(total_statuses.keys()):
    print(filename)
    print(total_statuses[filename])
