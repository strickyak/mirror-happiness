# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Request Handler for /notify endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import re
import io
import json
import logging
import webapp2

from random import choice
from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName
from google.appengine.api import urlfetch

from model import Credentials
import util

import gerund
terp = gerund.terp

DOUBLE_BRACE = re.compile('{{').search

CAT_UTTERANCES = [
    "<em class='green'>Purr...</em>",
    "<em class='red'>Hisss... scratch...</em>",
    "<em class='yellow'>Meow...</em>"
]


class NotifyHandler(webapp2.RequestHandler):
  """Request Handler for notification pings."""

  def post(self):
    """Handles notification pings."""
    logging.info('Got a notification with payload %s', self.request.body)
    data = json.loads(self.request.body)
    userid = data['userToken']
    # TODO: Check that the userToken is a valid userToken.
    self.mirror_service = util.create_service(
        'mirror', 'v1',
        StorageByKeyName(Credentials, userid, 'credentials').get())
    if data.get('collection') == 'locations':
      self._handle_locations_notification(data)
    elif data.get('collection') == 'timeline':
      self._handle_timeline_notification(data)

  def _handle_locations_notification(self, data):
    """Handle locations notification."""
    location = self.mirror_service.locations().get(id=data['itemId']).execute()
    text = 'Python Quick Start says you are at %s by %s.' % \
        (location.get('latitude'), location.get('longitude'))
    body = {
        'text': text,
        'location': location,
        'menuItems': [{'action': 'NAVIGATE'}],
        'notification': {'level': 'DEFAULT'}
    }
    self.mirror_service.timeline().insert(body=body).execute()

  def _handle_timeline_notification(self, data):
    """Handle timeline notification."""
    for user_action in data.get('userActions', []):
      # Fetch the timeline item.
      item = self.mirror_service.timeline().get(id=data['itemId']).execute()

      if user_action.get('type') == 'SHARE':
        # Create a dictionary with just the attributes that we want to patch.
        body = {
            'text': 'Python Quick Start got your photo! %s' % item.get('text', '')
        }

        # Patch the item. Notice that since we retrieved the entire item above
        # in order to access the caption, we could have just changed the text
        # in place and used the update method, but we wanted to illustrate the
        # patch method here.
        self.mirror_service.timeline().patch(
            id=data['itemId'], body=body).execute()

        # Only handle the first successful action.
        break
      elif user_action.get('type') in ['LAUNCH', 'REPLY']:
        note_text = item.get('text', '*NONE*')

        if DOUBLE_BRACE(note_text):
          logging.info("Ignoring Double Bracy Action :::: %s :::: %s" % (note_text, user_action))
          return

        try:
          z = terp.Run(note_text)
        except Exception as ex:
          z = "ERROR: %s" % ex

        item['text'] = "{{ %s }}\n%s" % (note_text, z)
        logging.info("notify/user_action/text = %s", item['text'])
        item['html'] = None
        item['menuItems'] = [{ 'action': 'REPLY' }, { 'action': 'DELETE' }];

        self.mirror_service.timeline().update(
            id=item['id'], body=item).execute()

        media = None
        if type(z) is list and len(z) > 0:
          for zi in z:
            logging.info("z[i] = %s", zi)

          yy = ''
          # Should be a list, with last element (top of stack) a list.
          tos = z[-1]
          if type(tos) is list and len(tos) > 0:
            for y in tos:
              logging.info("y = %s", y)
              # If items in that TOS are lists of 9, append to yy.
              if type(y) is list and len(y) == 9:
                yy += ','.join([str(int(yi)) for yi in y]) + ',,,'
                logging.info("yy = %s", yy)
        
            if len(yy):
              body = {
                'notification': {'level': 'DEFAULT'},
                'text': '',
              }
              media_link = 'http://node1.yak.net:2018/%s' % yy
              logging.info("fetching = %s", media_link)
              resp = urlfetch.fetch(media_link, deadline=10)
              logging.info("resp.content = %s", (resp.content))
              media = MediaIoBaseUpload(
                  io.BytesIO(resp.content), mimetype='image/png', resumable=True)

              logging.info("pushing image to timeline")
              self.mirror_service.timeline().insert(body=body, media_body=media).execute()
              logging.info("pushed image to timeline")

        logging.info("END NOTIFY")

      else:
        logging.info(
            "I don't know what to do with this notification: %s", user_action)


NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
