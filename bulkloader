#!/usr/bin/python

from optparse import make_option, OptionParser
import sys
import os

# Supported models
models = ["agency","stop","route","shape","trip"]

def model_default_filename(model):
	return "data/%s.txt" % model

def upload(model,url,file,options):
	opt = ""
	if options.debug:
		opt += " --email=x.com "
	
	cmd = "appcfg.py upload_data --config_file=../gogogo-hk/gogogo/loader.py --filename=%s --url %s/remote_api --kind=gogogo_%s %s ../gogogo-hk " % (
		file,url,"%s" % model , opt)
	
	print cmd
	os.system(cmd)

def upload_all(url,options):
	for m in models:
		file = model_default_filename(m)
		if os.path.exists(file):
			print "Upload %s" % model
			upload(m,url,file,options)	

if __name__ == "__main__":
	option_list = [
		make_option("-d", "--debug",
					action="store_true",  dest="debug",default=False),
		make_option("-u", "--url",
					action="store", type="string", dest="url",default="http://localhost:8000"),					
    ]

	parser = OptionParser(option_list = option_list,usage="usage: bulkloader all|%s [file]" % "|".join(models))
	(options , args ) = parser.parse_args()

	try:

		model = args[0]
		url = options.url
		
		if model == "all":

			upload_all(url,options)

		else:
		
			if not model in  models:
				raise ValueError('Unknown model : %s ' % model)
		
			try:
				file = args[1]
			except:
				file = model_default_filename(model)

			upload(model,url,file,options)		
		
	except Exception,v:	
		print v
		print 
		parser.print_help()
		sys.exit(-1)

	
