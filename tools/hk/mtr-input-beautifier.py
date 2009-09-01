#!/usr/bin/python

import sys
import codecs

input = sys.argv[1]

file = codecs.open(input ,"rt","utf-8")

result = []
name = []
fares = []

for line in file:
    items = line.split(" ")
    for token in items:
        try:
            value = float(token)
            if len(name) > 0 :
                key = " ".join(name)
                fares = []
                result.append( ( key , fares) )
                name = []
            fares.append(value)
        except ValueError:
            name.append(token)
        
for entry in result:
    
    print "\"" + entry[0].rstrip("\n").strip(" ") +"\"" , " ".join([ str(e) for e in entry[1] ])
