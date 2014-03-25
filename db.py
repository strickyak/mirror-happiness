import logging

OKAY = 0
try:
	from google.appengine.ext import ndb

	class Word(ndb.Model):
		name = ndb.StringProperty(indexed=False)
		code = ndb.StringProperty(indexed=False)

	Parent = ndb.Key('Key', 'Key') 

	def Store(name, code):
		w = Word(parent=Parent)
		w.name = name
		w.code = code
		w.put()

	def Scan():
		return Word.query(ancestor=Parent).fetch(100)

	OKAY = 250
except:
	logging.error("Failed to import NDB")
