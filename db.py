import logging

OKAY = 0
try:
	from google.appengine.ext import ndb

	class Word(ndb.Model):
		name = ndb.StringProperty(indexed=True)
		code = ndb.StringProperty(indexed=False)

	Parent = ndb.Key('Key', 'Key') 

	def Delete(name):
		w = Scan(name)
		if w:
			w.key.delete()

	def Store(name, code):
		w = Scan(name)
		if not ww:
			w = Word(parent=Parent)
		w.name = name
		w.code = code
		w.put()

	def Scan(name=None):
		if name:
			zz = Word.query(Word.name == name, ancestor=Parent).fetch(999)
			if not zz:
				return None
			if len(zz) > 1:
				db.delete([z.key for z in zz[1:]])
			return zz[0]
		else:
			return Word.query(ancestor=Parent).fetch(999)

	OKAY = 250
except:
	logging.error("Failed to import NDB")
