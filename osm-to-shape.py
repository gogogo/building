# -*- coding: utf-8 -*-
"""
	Convert OSM XML to Shape data import format
"""

import sys
from xml.dom.minidom import parse

def searchWayByName(dom,name):
	ret = None
	for node in dom.getElementsByTagName('way'):
		for tag in node.getElementsByTagName('tag'):
				if tag.getAttribute('k') == u"name" and tag.getAttribute('v') == name:
					ret = node
					break
		if ret != None:
			break

	return ret	

def searchWayByID(dom,id):
	ret = None
	for node in dom.getElementsByTagName('way'):
		if node.getAttribute("id") == id:
			ret = node
			break

	return ret

def extractPointsFromWay(dom,way):
	ret = []
	for nd in way.getElementsByTagName('nd'):
		id = nd.getAttribute('ref')
		for node in dom.getElementsByTagName('node'):
			if node.getAttribute('id') == id:
				lat = float(node.getAttribute('lat') )
				lon = float(node.getAttribute('lon'))

				ret.append( (lat,lon  ) )
	return ret
	
if len(sys.argv) != 4:
	print "%s osm.xml wayname shapeid" % sys.argv[0]
	sys.exit(0)

dom = parse(sys.argv[1])
wayname=sys.argv[2].decode('UTF-8')
id = sys.argv[3]

way = searchWayByID(dom,wayname)
if not way:
	print "\"%s\" not found" % wayname
	sys.exit(0)
	
points = extractPointsFromWay(dom,way)

point_list = []
for pt in points:
	point_list.append("%f,%f" % pt)

print "%s,%s,%s,\"%s\"" % (id,"",1, ",".join(point_list) )
