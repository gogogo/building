import sys
from gogogo.models import *
from gogogo.geo.LatLng import LatLng
from gogogo.geo.LatLngGroup import LatLngGroup
from Grouper import Grouper,GroupSwapOptimizer
from google.appengine.ext import db
from gogogo.geo.ConvexHull import ConvexHull

clusters = []
shapes = []
entities = Cluster.all().fetch(100)

while entities:
	for entry in entities:
		clusters.append(entry)	
		
	entities = Cluster.all().filter('__key__ >', entities[-1].key()).fetch(100)

entities = Shape.all().filter("ownerKind = ","gogogo_cluster").fetch(100)

while entities:
	for entry in entities:
		shapes.append(entry)	
		
	entities = Shape.all().filter("ownerKind = ","gogogo_cluster").filter('__key__ >', entities[-1].key()).fetch(100)

db.delete(clusters)
db.delete(shapes)
