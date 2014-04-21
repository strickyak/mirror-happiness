# Evaluate a note with Gerund for Glass.

import re
import io
import logging

from apiclient.http import MediaIoBaseUpload
from google.appengine.api import urlfetch

from gerund import terp

DOUBLE_BRACE = re.compile('{{').search

def RunForGlass(self, note_text, item=None):

  if DOUBLE_BRACE(note_text):
    logging.info("Ignoring Double Bracy Action :::: %s :::: %s" % (note_text, user_action))
    return

  try:
    z = terp.Run(note_text)
  except Exception as ex:
    z = "ERROR: %s" % ex

  if item is None:
    item = dict()

  result = "{{ %s }}\n%s" % (note_text, z)
  item['text'] = result
  logging.info("RunForGlass = %s", result)
  item['html'] = None
  item['menuItems'] = [{ 'action': 'REPLY' }, { 'action': 'DELETE' }];

  id = item.get('id')
  if id:
    self.mirror_service.timeline().update(id=id, body=item).execute()
    logging.info('Gerundive UPDATED %s %s', repr(id), repr(item))
  else:
    self.mirror_service.timeline().insert(body=item).execute()
    logging.info('Gerundive INSERTED %s', repr(item))

  media = None
  if type(z) is tuple and len(z) > 1: # ticks= is last.
    for zi in z:
      logging.info("z[i] = %s", zi)

    yy = ''
    # Should be a list, with last element (top of stack) a list.
    # Actually, last is 'ticks=...', so next-to-last:
    tos = z[-2]
    if type(tos) is list and len(tos) > 0:
      for y in tos:
        #logging.info("y = %s", y)
        # If items in that TOS are lists of 9, append to yy.
        if type(y) is list and len(y) == 9:
          yy += ','.join([str(int(yi)) for yi in y]) + ',,,'
          #logging.info("yy = %s", yy)
  
      if len(yy):
        body = {
          'notification': {'level': 'DEFAULT'},
          'text': '',
          'menuItems': [{ 'action': 'REPLY' }, { 'action': 'DELETE' }]
        }
        media_link = 'http://node1.yak.net:2018/%s' % yy
        logging.info("FETCHING = %s", media_link)
        resp = urlfetch.fetch(media_link, deadline=10)
        logging.info("LEN RESP.CONTENT = %s", len(resp.content))
        media = MediaIoBaseUpload(
            io.BytesIO(resp.content), mimetype='image/png', resumable=True)

        logging.info("PUSHING IMAGE TO timeline")
        self.mirror_service.timeline().insert(body=body, media_body=media).execute()
        logging.info("PUSHED IMAGE TO timeline")

  logging.info("END RunForGlass")
  return result
