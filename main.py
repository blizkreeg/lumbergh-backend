# ****************************************** PACKAGES **************************************

import webapp2
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app

import sys
import urllib
import json
import rules
import docclasscsv
import re
import pickle

# ****************************************** APIs **************************************

# POST https://lumberghme.appspot.com/user
  # email: <email>
  # key: lumbergh

  # returns JSON {"status": true/false}

# POST https://lumberghme.appspot.com/message
  # email: <email>
  # id: <message-id>
  # body: <thread-body>
  # subject: <message-subject>
  # key: lumbergh

  # returns JSON {"status": true/false, "is_task": true/false, "is_urgent": true/false}

# GET https://lumberghme.appspot.com/message?email=<email>&id=<message-id>&key=lumbergh
  # returns JSON {"status": true/false}

# GET https://lumberghme.appspot.com/list?email=<email>&key=lumbergh
  # returns JSON array of all tasks that aren't done yet
  # [{"is_urgent": false, "is_task": true, "is_done": false, "id": "123456"}, {"is_urgent": false, "is_task": true, "is_done": false, "id": "123456"}]

# POST https://lumberghme.appspot.com/status
  # email: <email>
  # id: <message-id>
  # is_done: true/yes/1/t OR false/no/0/f
  # key: lumbergh

# POST https://lumberghme.appspot.com/train
  # email: <email>
  # id: <message-id>
  # body: <thread-body>
  # is_task: true/yes/1/t OR false/no/0/f
  # key: lumbergh

# ****************************************** CONSTANTS **************************************

SECRET_KEY = "lumbergh"

# ****************************************** MODELS **************************************

class Feature(db.Model):
  for_id = db.StringProperty()
  val = db.TextProperty()

class Category(db.Model):
  for_id = db.StringProperty()
  val = db.TextProperty()

class Account(db.Model):
  email = db.EmailProperty()

class Message(db.Model):
  mid = db.StringProperty()
  is_done = db.BooleanProperty()
  is_task = db.BooleanProperty()
  is_urgent = db.BooleanProperty()
  show = db.BooleanProperty()
  subject = db.StringProperty()

# ****************************************** FUNCTIONS TO READ/WRITE THE TRAINING DATA **************************************

def write_features(data, feature_key='global'):
  features = Feature.gql("WHERE for_id = :1", feature_key).get()
  if not features:
    features = Feature(for_id = feature_key)
  features.val = db.Text(data)
  status = features.put()
  return status

def write_categories(data, category_key='global'):
  categories = Category.gql("WHERE for_id = :1", category_key).get()
  if not categories:
    categories = Category(for_id = category_key)
  categories.val = db.Text(data)
  status = categories.put()
  return status

def read_features(feature_key='global'):
  features = Feature.gql("WHERE for_id = :1", feature_key).get()
  if features:
    return features.val
  else:
    return ""

def read_categories(category_key='global'):
  categories = Category.gql("WHERE for_id = :1", category_key).get()
  if categories:
    return categories.val
  else:
    return ""

# ****************************************** TRAINING DATA INITIALIZE **************************************

# initialize
c1 = docclasscsv.fisherclassifier(docclasscsv.getwordsnew)

# set threshold
c1.setthreshold('task', 1.0)
c1.setthreshold('nontask', 2.0)

# read feature category file
features = read_features()
if(features == ""):
  print "no features found in datastore"
  c1.readfc("fc_out.txt")
else:
  print "features found in datastore!"
  c1.fc = pickle.loads(str(features))

# read category file
categories = read_categories()
if(categories == ""):
  print "no categories found in datastore"
  c1.readcc("cc_out.txt")
else:
  print "categories found in datastore!"
  c1.cc = pickle.loads(str(categories))

# ****************************************** FUNCTIONS **************************************

def has_secret_key(request):
  key = request.get('key')
  if key == SECRET_KEY:
    return True
  else:
    return False

def write_json_response(response, data):
  response.headers['Content-Type'] = 'application/json'
  response.out.write(json.dumps(data))

def str2bool(v):
  return v.lower() in ("yes", "True", "true", "t", "1")

# ****************************************** REQUEST HANDLERS **************************************

# class MainPage(webapp2.RequestHandler):
#     def get(self):

#         user = users.get_current_user()

#         if user:
#           self.response.headers['Content-Type'] = 'text/plain'
#           self.response.out.write('Hello' + user.nickname())
#         else:
#           self.redirect(users.create_login_url(self.request.uri))

class AccountHandler(webapp2.RequestHandler):
  def post(self):
    if has_secret_key(self.request) == False:
      return None

    # see if user exists
    user = Account.gql("WHERE email = :1", self.request.get('email')).get()
    if user:
      write_json_response(self.response, {"status": "true"})
    else:
      # create the user account
      user = Account(email = self.request.get('email'))
      status = user.put()

      if status:
        write_json_response(self.response, {"status": "true"})
      else:
        write_json_response(self.response, {"status": "false"})

  def get(self):
    if has_secret_key(self.request) == False:
      return None

    user = Account.gql("WHERE email = :1", self.request.get('email')).get()
    if user:
      write_json_response(self.response, {"status": "true"})
    else:
      write_json_response(self.response, {"status": "false"})

class MessageHandler(webapp2.RequestHandler):

  def should_skip_message_for_tasks(self, body):
    if "unsubscribe" in body:
      return True
    return False

  def store_message(self, user):
    # get message params
    mid = self.request.get('id')
    email = self.request.get('email')
    body = self.request.get('body')
    subject = self.request.get('subject')

    body = re.sub('<[^<]+?>', '', body)
    body = urllib.unquote(body)

    # see if task and urgent
    is_regex_task = rules.check_if_task(body)
    is_urgent = rules.check_if_urgent(body) or rules.check_if_urgent(subject)

    if self.should_skip_message_for_tasks(body):
      classified_body = "nontask"
      classified_subj = "nontask"
    elif(is_regex_task):
      c1.train(body, 'task')
      classified_body = "task"
      classified_subj = "task"
    else:
      classified_body = c1.classify(body)
      classified_subj = c1.classify(subject)

    # print "subject: " + subject
    # print "body: %s" %(body)
    # print "urgency: %s" %(is_urgent)
    # print "regex task: %s" %(is_regex_task)
    # print "classified_body: %s" %(classified_body)
    # print "classified_subj: %s" %(classified_subj)

    if is_regex_task or classified_body == "task" or classified_subj == "task":
      is_task = True
    else:
      is_task = False

    # create message
    self.msg = Message(parent=user)
    self.msg.mid = mid
    self.msg.is_done = False
    self.msg.is_task = is_task
    self.msg.is_urgent = is_urgent
    self.msg.show = True
    self.msg.subject = subject

    status = self.msg.put()

    return status

  def post(self):
    if has_secret_key(self.request) == False:
      return None

    # check if user account exists
    user = Account.gql("WHERE email = :1", self.request.get('email')).get()
    if user:
      exists = Message.gql("WHERE mid = :1 AND ANCESTOR IS :2", self.request.get('id'), user.key()).get()
      if exists:
        write_json_response(self.response, {"status": "true"})
      else:
        status = False
        try:
          status = self.store_message(user)
        except:
          print "error while parsing the message!"

        if status:
          write_json_response(self.response, {"status": "true", "is_task": str(self.msg.is_task), "is_urgent": str(self.msg.is_urgent)})
        else:
          write_json_response(self.response, {"status": "false"})
    else:
      # create the user account
      user = Account(email = self.request.get('email'))
      status = user.put()

      if status:
        # if successful, create the message
        status = self.store_message(user)
        write_json_response(self.response, {"status": "true"})
      else:
        write_json_response(self.response, {"status": "false"})

  def get(self):
    if has_secret_key(self.request) == False:
      return None

    user = Account.gql("WHERE email = :1", self.request.get('email')).get()

    if user:
      msg = Message.gql("WHERE show = true AND mid = :1 AND ANCESTOR IS :2", self.request.get('id'), user.key()).get()
      if msg:
        write_json_response(self.response, {"status": "true",
                                            "mid": str(msg.mid),
                                            "is_done": str(msg.is_done),
                                            "is_task": str(msg.is_task),
                                            "is_urgent": str(msg.is_urgent),
                                            "subject": str(msg.subject)})
      else:
        write_json_response(self.response, {"status": "false"})
    else:
      write_json_response(self.response, {"status": "false"})

class ListHandler(webapp2.RequestHandler):
  def get(self):
    if has_secret_key(self.request) == False:
      return None

    user = Account.gql("WHERE email = :1", self.request.get('email')).get()
    if user:
      msgs = Message.gql("WHERE show = True AND ANCESTOR IS :1 ORDER BY mid DESC", user.key())
      msgs_list = []
      for msg in msgs:
        msg_hash = {}
        msg_hash['id'] = str(msg.mid)
        msg_hash['is_task'] = str(msg.is_task)
        msg_hash['is_urgent'] = str(msg.is_urgent)
        msg_hash['is_done'] = str(msg.is_done)
        msg_hash['subject'] = msg.subject

        msgs_list.append(msg_hash)
      write_json_response(self.response, msgs_list)
    else:
      write_json_response(self.response, {"status": "false"})

class StatusHandler(webapp2.RequestHandler):
  def post(self):
    if has_secret_key(self.request) == False:
      return None

    user = Account.gql("WHERE email = :1", self.request.get('email')).get()

    if user:
      msg = Message.gql("WHERE mid = :1 AND ANCESTOR IS :2", self.request.get('id'), user.key()).get()
      if msg:
        msg.is_done = str2bool(self.request.get('is_done'))
        if msg.is_done:
          msg.show = False
        status = msg.put()

        if status:
          write_json_response(self.response, {"status": "true"})
        else:
          write_json_response(self.response, {"status": "false"})
      else:
        write_json_response(self.response, {"status": "false"})
    else:
      write_json_response(self.response, {"status": "false"})


class TrainHandler(webapp2.RequestHandler):
  def post(self):
    if has_secret_key(self.request) == False:
      return None

    user = Account.gql("WHERE email = :1", self.request.get('email')).get()

    if user:
      msg = Message.gql("WHERE mid = :1 AND ANCESTOR IS :2", self.request.get('id'), user.key()).get()
      if msg:
        is_task = str2bool(self.request.get('is_task'))
        body = self.request.get('body')
        body = urllib.unquote(body)
        if is_task:
          c1.train(body, 'task')
          s = write_features(pickle.dumps(c1.fc))
          s = write_categories(pickle.dumps(c1.cc))
          msg.is_task = True
          msg.show = True
          msg.is_done = False
        else:
          c1.train(body, 'nontask')
          s = write_features(pickle.dumps(c1.fc))
          s = write_categories(pickle.dumps(c1.cc))
          msg.is_task = False
          msg.show = False

        status = msg.put()

        if status:
          write_json_response(self.response, {"status": "true"})
        else:
          write_json_response(self.response, {"status": "false"})
      else:
        write_json_response(self.response, {"status": "false"})
    else:
      write_json_response(self.response, {"status": "false"})

# ****************************************** ROUTER **************************************

app = webapp2.WSGIApplication([# ('/', MainPage),
                              ('/message', MessageHandler),
                              ('/user', AccountHandler),
                              ('/list', ListHandler),
                              ('/status', StatusHandler),
                              ('/train', TrainHandler)],
                              debug=True)
