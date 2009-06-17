"""
KML Generation utility
"""

import xml.dom.minidom

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "../gogogo-hk"))

from gogogo.geo.LatLng import LatLng
from gogogo.geo.LatLngGroup import LatLngGroup
from gogogo.geo.ConvexHull import ConvexHull

XML = """
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
</Document>
</kml>	
"""

def appendTextNode(dom,name,text):
	node = dom.createElement(name)
	text = dom.createTextNode(text)
	dom.documentElement.appendChild(node)
	node.appendChild(text)

def Kml():
	"""
	Create KML Dom object
	"""
	dom = xml.dom.minidom.parseString(XML)
	dom.documentNode = dom.getElementsByTagName("Document")[0]
	return dom

def Placemarker(name=None , desc = None , styleUrl = None , point = None,
	group = None):
	"""
	Create Placemarker Dom object
	
	@param point: 
	@type point: gogogo.geo.LatLng

	@type group: gogogo.geo.LatLngGroup
	
	"""
	dom = xml.dom.minidom.parseString("<Placemark></Placemark>")
	
	if name:
		appendTextNode(dom,"name",name)

	if desc:
		appendTextNode(dom,"description",desc)

	if styleUrl:
		appendTextNode(dom,"styleUrl",styleUrl)

	if point:
		XML = "<Point><coordinates>%f,%f,0</coordinates></Point>" % (point.lng , point.lat)
		node = xml.dom.minidom.parseString(XML)
		dom.documentElement.appendChild(node.documentElement)

	if group:
		points = ""
		convexhull = ConvexHull(group)
		for pt in convexhull.polygon:
			points += "%f,%f,0 " % (pt.lng,pt.lat)
		
		XML = """
		<Polygon>
			<tessellate>1</tessellate>
			<outerBoundaryIs>
				<LinearRing>
					<coordinates>%s</coordinates>
				</LinearRing>
			</outerBoundaryIs>
		</Polygon>
		"""	% points

		node = xml.dom.minidom.parseString(XML)
		dom.documentElement.appendChild(node.documentElement)
		
	return dom
	
if __name__ == "__main__":
	marker = Placemarker(name="Test",desc="Description",styleUrl="123" , point = LatLng(22,104) )
	print marker.toxml()
