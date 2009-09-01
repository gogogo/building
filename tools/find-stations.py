# Find stations
# Given a input file with the name of stations , dump the ID of all station with matching name

import codecs
from StringIO import StringIO

def run(input):
    from django.utils import simplejson
    from gogogo.models import Stop
    
    file = codecs.open(input ,"rt","utf-8")
    
    stops = {}

    # Stop loading
    print "Loading stops"
    entities = Stop.all().filter("location_type =",1).fetch(100)
    while entities:
        for entry in entities:
            stops[entry.key().id_or_name()] = entry
        entities = Stop.all().filter('__key__ >', entities[-1].key()).filter("location_type =",1).fetch(100)

    print "%d stations loaded" % len(stops)

    result = {}
    
    for line in file:
        name = line.rstrip("\n").rstrip("\r").strip(" ")
        if len(name) <= 1:
            continue

        result[name] = []
        for entry in stops:
            s = stops[entry]
            for item in s.name:
                if item.find(name) != -1:
                    result[name].append(s.key().id_or_name())
                    break
            
    text = StringIO()
	
    simplejson.dump(result,text,ensure_ascii=False,indent =1)
    print text.getvalue()
            


