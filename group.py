# Point Grouping example program
import sys
import os
import csv
import codecs
import csv, codecs, cStringIO
import copy
from optparse import make_option, OptionParser

from LatLng import LatLng
from LatLngGroup import LatLngGroup

class UTF8Recoder:
	"""
	Iterator that reads an encoded stream and reencodes the input to UTF-8
	"""
	def __init__(self, f, encoding):
		self.reader = codecs.getreader(encoding)(f)

	def __iter__(self):
		return self

	def next(self):
		return self.reader.next().encode("utf-8")

class UnicodeReader:
	"""
	A CSV reader which will iterate over lines in the CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		f = UTF8Recoder(f, encoding)
		self.reader = csv.reader(f, dialect=dialect, **kwds)

	def next(self):
		row = self.reader.next()
		return [unicode(s, "utf-8") for s in row]

	def __iter__(self):
		return self



def LatLngCompare(x,y):
	if x.lat > y.lat:
		return 1
	elif x.lat < y.lat:
		return -1
	else:
		if x.lng > y.lng : 
			return 1
		elif x.lng < y.lng:
			return -1
		return 0	

class Grouper:
	"""
		A simple points grouping algorithm (preprocessing)
	"""
	
	def __init__(self,radius=0.25,threshold=1.5):
		self.groups = []
		
		self.tgdi = radius * 2
		self.threshold = threshold
		
	def append(self,latlng):
		"""
			Append a point to groups
		"""
		target = None
		min = sys.maxint
		for g in self.groups:
			c = g.get_centroid()
			dist = c.distance(latlng)
			if dist < self.threshold:
				ng = copy.copy(g)
				ng.append(latlng)
				
				diff = ng.get_gdi() - g.get_gdi()
				if diff < min:
					min = diff
					target = g
		
		if target:
			g.append(latlng)
		else:
			self.groups.append(LatLngGroup([latlng]))
	
if __name__ ==  "__main__":
	args = sys.argv	
	
	input = args[1]
	
	reader = UnicodeReader(open(input))	
	
	pts = []
	
	for row in reader:
		try:
			pt = LatLng(float(row[0]),float(row[1]))
			pts.append(pt)
		except AssertionError:
			print row
		#except IndexError:
		#	print row
		
	pts.sort(LatLngCompare)
	
	grouper = Grouper()
	for (i,pt) in enumerate(pts):
#		print "Process " +str(i) +  ":" + str(pt)		
		grouper.append(pt)
		
#	print "group = " + str(len(grouper.groups))
		
	KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
%s
</Document>
</kml>	
"""

	PLACEMARKER="""
  <Placemark>
    <name>%d</name>
    <description>%s</description>
    <Point>
      <coordinates>%f,%f,0</coordinates>
    </Point>
  </Placemark>
"""
	placemark = []
	
	for (i,g) in enumerate(grouper.groups):
		c = g.get_centroid()
		desc = []
		for p in g.pts:
			desc.append(str(p))
		placemark.append(PLACEMARKER % (i, 
			",".join(desc) , c.lng ,c.lat )) 

	print KML % ( "\n".join(placemark))

