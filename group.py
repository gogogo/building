# Point Grouping example program
import sys
import os
import csv
import codecs
import csv, codecs, cStringIO
import copy
from optparse import make_option, OptionParser

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "../gogogo-hk"))

from gogogo.geo.LatLng import LatLng
from gogogo.geo.LatLngGroup import LatLngGroup

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
	
	def __init__(self,radius=0.4,max_walking_distance=1.0):
		self.groups = []
		
		self.tgdi = radius
		self.threshold = max_walking_distance / 2
		
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
				ng = g.dup()
				ng.append(latlng)
				if ng.get_radius() < self.threshold and ng.get_gdi() < self.tgdi:
					diff = ng.get_gdi() - g.get_gdi()
					if diff < min:
						min = diff
						target = g
		
		if target:
			target.append(latlng)
			#print "DEBUG: " + str(g.get_radius())
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
   <Style id="group">
      <IconStyle>
         <color>ff00ff00</color>
         <scale>1.1</scale>
         <Icon>
            <href>http://maps.google.com/mapfiles/kml/pal3/icon21.png</href>
         </Icon>
      </IconStyle>
   </Style>
   <Style id="line">
	 <LineStyle>
        <color>7f00ffff</color>
        <width>4</width>
      </LineStyle>         
   </Style>
%s
</Document>
</kml>	
"""

	PLACEMARKER="""
  <Placemark>
    <name>%s</name>
    <description>%s</description>
    <Point>
      <coordinates>%f,%f,0</coordinates>
    </Point>
    <styleUrl>%s</styleUrl>
    %s
  </Placemark>
"""

	LINE_PLACEMARK="""
  <Placemark>
    <name>%s</name>
    <description>%s</description>
    <styleUrl>#line</styleUrl>
   <LineString>
        <extrude>0</extrude>
        <tessellate>0</tessellate>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>%s
        </coordinates>	
	</LineString>
  </Placemark>

"""

	placemark = []
	
	for (i,g) in enumerate(grouper.groups):
		c = g.get_centroid()
		desc = "Number: %d \n Radius : %f\n" % (len(g.pts),g.get_radius() )
		#for p in g.pts:
		#	desc.append(str(p))			
				
		placemark.append(PLACEMARKER % (str(i), 
			desc , c.lng ,c.lat ,"group", "" )) 
			
		line = []
		for (j,p) in  enumerate(g.pts):	
			coord = "%f,%f\n%f,%f\n" % (c.lng , c.lat , p.lng,p.lat)
			placemark.append(LINE_PLACEMARK % (str(i) + "-" + str(j), 
				"" , coord )) 
			

	for p in pts:
		placemark.append(PLACEMARKER % ("STOP", 
			"" , p.lng ,p.lat ,"","")) 

	print KML % ( "\n".join(placemark))

