import sys
from gogogo.models import *
from gogogo.geo.LatLng import LatLng
from gogogo.geo.LatLngGroup import LatLngGroup
from Grouper import Grouper,GroupSwapOptimizer
from google.appengine.ext import db
from gogogo.geo.ConvexHull import ConvexHull

# Clusterer - Divide stops into cluster (For producing non-optimized result)

print "Running clusterer..."
print "Loading data from server"

# Stop loading
stops = {}

entities = Stop.all().fetch(100)
while entities:
	for entry in entities:
		stops[entry.key().id_or_name()] = entry
	entities = Stop.all().filter('__key__ >', entities[-1].key()).fetch(100)

print "%d of stops loaded" % len(stops)

clusters = []

# Cluster loading
entities = Cluster.all().fetch(100)

while entities:
	for entry in entities:
		clusters.append(entry)	
		
	entities = Cluster.all().filter('__key__ >', entities[-1].key()).fetch(100)

print "%d of clusters loaded" % len(clusters)

clusterer = Grouper()

for c in clusters:
	g = LatLngGroup()
	g.setData(c)
	for key in c.members:
		pt = LatLng()
		s = stops[key.id_or_name()]
		pt.lat = s.latlng.lat
		pt.lng = s.latlng.lon
		pt.setData(s)
		g.append(pt)
		
		del stops[key.id_or_name()]
		
	clusterer.appendGroup(g)

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

pts = []
for id in  stops:
	s = stops[id]
	pt = LatLng()
	pt.lat = s.latlng.lat
	pt.lng = s.latlng.lon
	pt.setData(s)
	pts.append(pt)

print "%d of stops are not listed in any cluster" % len(stops)

pts.sort(LatLngCompare)

for pt in pts:
	clusterer.append(pt)

saveClusterList = []
saveShapeList = []
newShapeCount = 0

for g in clusterer.getGroups():
	cluster = g.getData()
	
	if cluster == None:
		cluster = Cluster() # Create a new cluster entry
		g.setData(cluster)
	
	cluster.members = []
	for pt in g.pts: # Found newly added stop
		cluster.members.append(pt.getData().key())		
		
	center = g.get_centroid()
	
	cluster.center = db.GeoPt(center.lat,center.lng)

	cluster.update_geohash()
	
	cluster.radius = float(g.get_radius())

	saveClusterList.append(cluster)
	

print "Writing %d of cluster data back to server" % len(saveClusterList)
db.put(saveClusterList)

clusters = saveClusterList
saveClusterList = []

for g in clusterer.getGroups():
	cluster = g.getData()
	if cluster == None:
		continue

	shape = cluster.shape
	if shape == None:
		shape = Shape()
		shape.setOwner(cluster)
		shape.type = 1
		shape.color = "#08f6dd"
		
		newShapeCount += 1
		
		saveClusterList.append(cluster)
		db.put(shape)
		
		cluster.shape = shape
	
	convexhull = ConvexHull(g)
	for pt in convexhull.polygon:
		shape.points.append(pt.lat)
		shape.points.append(pt.lng)
		
	saveShapeList.append(shape)
	
print "%d of shapes created " % newShapeCount

print "Writing %d of cluster data back to server" % len(saveClusterList)
db.put(saveClusterList)
			
print "Writing %d of shape data back to server" % len(saveShapeList)
db.put(saveShapeList)

