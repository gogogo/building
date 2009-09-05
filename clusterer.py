import sys
from gogogo.models import *
from gogogo.geo.LatLng import LatLng
from gogogo.geo.LatLngGroup import LatLngGroup
from Grouper import Grouper,GroupSwapOptimizer
from google.appengine.ext import db
from gogogo.geo.ConvexHull import ConvexHull
from gogogo.models.MLStringProperty import MLStringProperty
from gogogo.views.db.forms import next_key_name
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

# Start processing

clusterer = Grouper()

for c in clusters: # Initializer clusters
    g = LatLngGroup()
    g.set_data(c)
    for key in c.members:
        pt = LatLng()
        s = stops[key.id_or_name()]
        pt.lat = s.latlng.lat
        pt.lng = s.latlng.lon
        pt.set_data(s)
        g.append(pt)
        
        if c.station != None:
            g.set_fixed_centroid(LatLng(c.station.latlng.lat ,c.station.latlng.lon ) )
        
        del stops[key.id_or_name()]
        
    clusterer.appendGroup(g)

stations = []
for id in  stops:
    s = stops[id]
    if s.location_type == 1:        
        #Create cluster based on station
        stations.append(s)

        key_name = next_key_name(Cluster , MLStringProperty.to_key_name(s.name))
        cluster = Cluster(key_name = key_name)
        cluster.set_station(s)

        pt = LatLng(s.latlng.lat,s.latlng.lon)
        pt.set_data(s)
        
        g = LatLngGroup()
        g.set_data(cluster)
        g.append(pt)
        g.set_fixed_centroid(pt)
        
        clusterer.appendGroup(g)

print "%d stations found"	% len(stations)

for stop in stations:
    del stops[stop.key().id_or_name()]

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

# Convert stop that are not belonged to any cluster to LatLng
pts = []
for id in  stops:
    s = stops[id]
    pt = LatLng()
    pt.lat = s.latlng.lat
    pt.lng = s.latlng.lon
    pt.set_data(s)
    pts.append(pt)

print "%d of stops are not listed in any cluster" % len(stops)

pts.sort(LatLngCompare)

for pt in pts:
    clusterer.append(pt)

saveClusterList = []
saveShapeList = []
newShapeCount = 0

for g in clusterer.getGroups():
    cluster = g.get_data()

    if cluster == None:
        cluster = Cluster() # Create a new cluster entry
        g.set_data(cluster)

    cluster.members = []
    for pt in g.pts: # Found newly added stop
        cluster.members.append(pt.get_data().key())		
        
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
    cluster = g.get_data()
    if cluster == None:
        continue

    shape = cluster.shape
    if shape == None:
        key_name = next_key_name(Shape , cluster.key().name())
        shape = Shape(key_name = key_name)
        shape.set_owner(cluster)
        shape.type = 1
        shape.color = "#08f6dd"
        
        newShapeCount += 1
        
        saveClusterList.append(cluster)
        db.put(shape)
        
        cluster.shape = shape
        
    shape.points = []

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

