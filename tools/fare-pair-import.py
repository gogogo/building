# Import data to fare pair
# 
# Format of input CSV (The first row will be skipped)
#
# from , to  , fare_type 1 , fare_type2 , fare_type3 , ....
#
#

import codecs
from StringIO import StringIO
import csv

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

def run(fare_stop_id, mapping_file,input_file,col):
    """
    @param fare_stop_id
    @param mapping_file The mapping file generated by find-stations.py
    @input_file A CSV file of fare data
    @col The column of fare
    """
    from gogogo.models import FareStop , FarePair , Stop
    from gogogo.models.utils import id_or_name
    from google.appengine.ext import db
    from django.utils import simplejson
    from gogogo.views.db.forms import next_key_name
    
    key = db.Key.from_path(FareStop.kind(),id_or_name(fare_stop_id))
    
    fare_stop = FareStop.get(key)
    
    if fare_stop == None:
        print "Error! fare_stop_id(%s) not found!" % fare_stop_id
        return
        
    file = codecs.open(mapping_file ,"rt","utf-8")
    
    data =""
    for line in file:
        data+=line
    
    mapping = simplejson.loads(data)
    
    reader = UnicodeReader(open(input_file))
    col = int(col)
    first = True
    
    to_save = []
    print "Loading from database...."
    
    #pairs = []
    pairs = {}
    entities = FarePair.all().filter("owner =",key).fetch(100)
    
    from_stop_property = getattr(FarePair, "from_stop")
    to_stop_property = getattr(FarePair, "to_stop")
    
    while entities:
        print "Loading 100 records from database..."
        for entry in entities:
            #pairs.append(entry)
            
            from_stop_key = from_stop_property.get_value_for_datastore(entry)
            to_stop_key = to_stop_property.get_value_for_datastore(entry)
            
            if not from_stop_key.id_or_name() in pairs:
                pairs[from_stop_key.id_or_name()] = {}
            pairs[from_stop_key.id_or_name()][to_stop_key.id_or_name()] = entry
        entities = FarePair.all().filter('__key__ >', entities[-1].key()).filter("owner  =",key).fetch(100)    
    
    for row in reader:
        if first:
            first = False
            continue
            
        try:
            #print row[0],row[1]
            
            try:
                fare = float(row[col])
            except ValueError:
                print "Warning. Value Error for %s to %s = %s" % (row[0],row[1],row[col])
                continue
            
            from_stop_id = mapping[row[0]][0]
            to_stop_id = mapping[row[1]][0]
            from_stop_key = db.Key.from_path(Stop.kind(),id_or_name(from_stop_id))
            to_stop_key = db.Key.from_path(Stop.kind(),id_or_name(to_stop_id))
            
            entry = None
            
            try:
                entry = pairs[from_stop_id][to_stop_id]
            except KeyError:
                pass
            
            #for pair in pairs:
                #if (str(pair.from_stop.key().id_or_name()) == from_stop_id and 
                    #str(pair.to_stop.key().id_or_name()) == to_stop_id):
                    #entry = pair
                    #break
                    
            if not entry:
                key_name = next_key_name(FarePair,FarePair.gen_key_name(owner = key,from_stop = from_stop_key,to_stop = to_stop_key))
                print "Create new entry %s " % key_name
                entry =  FarePair(owner = key , from_stop = from_stop_key , to_stop = to_stop_key ,key_name = key_name,fare = fare)
                to_save.append(entry)
            else:            
                if entry.fare != fare:
                    entry.fare = float(row[col])
                    to_save.append(entry)
                            
            if len(to_save) > 1000:
                print "Saving 1000 records to database..."
                db.put(to_save)
                to_save = []
            
            #print from_stop_id,to_stop_id , row[col]
        except KeyError,e:
            print "Station not found! : %s" % str(e)
    
    print "Saving to database..."
    db.put(to_save)
    print "%d of record saved" % len(to_save)
