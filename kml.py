"""
KML Generation utility
"""

import xml.dom.minidom

XML = """
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
</Document>
</kml>	
"""

def kml_dom():
	dom = xml.dom.minidom.parseString(XML)
	dom.documentNode = dom.getElementsByTagName("Document")[0]
	return dom

