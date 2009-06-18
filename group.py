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
from kml import Kml
from kml import Placemarker
import xml.dom.minidom

from Grouper import Grouper,GroupSwapOptimizer

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
	
if __name__ ==  "__main__":
	debug = open("debug.log","wt")
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
		grouper.append(pt)
	
	optimizer = GroupSwapOptimizer(grouper)
	optimizer.process()
		

	#Output generation
	
	dom = Kml()

	group_style = 	xml.dom.minidom.parseString("""
   <Style id="group">
      <IconStyle>
         <color>ff00ff00</color>
         <scale>1.1</scale>
         <Icon>
            <href>http://maps.google.com/mapfiles/kml/pal3/icon21.png</href>
         </Icon>
      </IconStyle>
	  <PolyStyle>
         <color>4cff5500</color>
      </PolyStyle>
	  <LineStyle>
        <color>ffffffff</color>
     </LineStyle>
      
   </Style>"""
	)
	
	line_style = xml.dom.minidom.parseString("""
   <Style id="line">
	 <LineStyle>
        <color>7f00ffff</color>
        <width>4</width>
      </LineStyle>         
   </Style>
	""")
	
	sys.stderr.write("No. of swap = %d\n" % optimizer.swap_count)
	
	dom.documentNode.appendChild(group_style.documentElement)
	dom.documentNode.appendChild(line_style.documentElement)

	for (i,g) in enumerate(grouper.groups):
		debug.write("group %d\n" % i)
		debug.write(g.toString(6) + "\n")
		c = g.get_centroid()
		desc = "Number: %d \n Radius : %f\n" % (len(g.pts),g.get_radius() )

		placemark = Placemarker(name = str(i) , desc=desc, point = c ,styleUrl="group" )
				
		dom.documentNode.appendChild(placemark.documentElement)
		
		polygon = Placemarker(name=str(i) , group = g ,styleUrl="group")
		dom.documentNode.appendChild(polygon.documentElement)			

	for p in pts:
		placemark = Placemarker(name="STOP" , point = p)
		dom.documentNode.appendChild(placemark.documentElement)

	print dom.toxml()
	debug.close()
