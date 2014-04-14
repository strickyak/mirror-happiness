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
			logging.info('Delete : %s = %s', w.name, w.code)
			w.key.delete()

	def Store(name, code):
		w = Fetch(name)
		if not w:
			w = Word(parent=Parent)
		w.name = name
		w.code = code
		logging.info('Store : %s = %s', name, code)
		w.put()

	def Fetch(name):
		zz = Word.query(Word.name == name, ancestor=Parent).fetch(999)
		if not zz:
			logging.info('Fetch not found: %s', name)
			return None
		z = zz[0]
		logging.info('Fetch : %s = %s', z.name, z.code)
		return z
	def Scan():
		r = Word.query(ancestor=Parent).fetch(999)
		logging.info('Scan returns %s', [e.name for e in r])
		return r

	OKAY = 250
except:
	pass
