#!/usr/bin/python
# -*- coding: utf-8 -*-

from HK1980 import *

import sys
import os
import csv
import codecs
import csv, codecs, cStringIO

from optparse import make_option, OptionParser

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

class UnicodeWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, quoting=csv.QUOTE_MINIMAL, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, quoting=quoting, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)


if __name__ == "__main__":
	option_list = [
		make_option("-s", "--skip-first",
					action="store_true",  dest="skip_first",default=False),
		make_option('-x',"--excahnge", action="store_true",
			dest="exchange",default=False)			
    ]

	parser = OptionParser(option_list = option_list,usage="usage: csv-hk1980-to-wgs84 [options] input.csv [geo_x [geo_y]]")
	(options , args ) = parser.parse_args()

	x = 0
	y = 1
	first = True

	try:
		input = args[0]
	except:
		parser.print_help()
		sys.exit(-1)
		
	try:
		x = int(args[1])
		y = int(args[2])
	except IndexError:
		pass

	reader = UnicodeReader(open(input))
	writer = UnicodeWriter(sys.stdout)
	
	for row in reader:
		if first:
			first = False
			if options.skip_first:
				continue
		(lat,lng) = hk1980_to_wgs84(float(row[y]),float(row[x]))
		
		if options.exchange:	
			row[x] = str(lat)
			row[y] = str(lng)

		else:

			row[y] = str(lat)
			row[x] = str(lng)


		writer.writerow(row)
