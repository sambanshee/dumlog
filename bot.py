# -*- coding: utf-8 -*-
import bottle
import datetime
from bottle import *
from google.appengine.api import users
from google.appengine.ext import ndb
from markdown2 import markdown
 
app = Bottle()

tags_list = [u"Чушь", u"Креатив", u"Косплей", u"Фоточке"]

database_key = ndb.Key('Posts', 'submitted_posts')

class Posts(ndb.Model):
    content = ndb.TextProperty(indexed=True, required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    title = ndb.StringProperty(indexed=True, required=True)
    #tags = ndb.StringProperty(required=True, repeated=True, choices=set(tags_list))
    tags = ndb.StringProperty(repeated=True, choices=set(tags_list))

@app.route('/')
def main_page():
   
    posts_query = Posts.query(ancestor=database_key).order(-Posts.date) 
    posts = posts_query.fetch(10)   
    output = template('posts.html', posts=posts)
    return output

@app.route('/posts/<url_id>')
def single_post(url_id):
    posts = ndb.Key(urlsafe=url_id)
    post = Posts.query(ancestor=posts).fetch()
    #posts = { "post": post }
    output = template('posts.html', posts=post)
#    output =""
#    for i  in post:
#      output = output + post 
    return output   

@app.route('/sign', method='POST')

@app.route('/add')
def write_article():
    user = users.get_current_user()
    if not user:
        redirect(users.create_login_url(request.url))
    elif not users.is_current_user_admin():
        redirect('/')
    output = template('add.html', tags_list = tags_list)
    return output

@app.route('/add', method='POST')
def add_article():
    user = users.get_current_user()
    if not user:
        redirect(users.create_login_url('/add'))
    elif not users.is_current_user_admin():
        redirect('/')

    post = Posts(parent=database_key)
    post.content = request.forms.get('content')
    post.title = request.forms.get('title')
    tags = request.forms.getall('tags')
    post_tags = []
    for tag in tags:
      post_tags.append(tag.decode('utf-8'))
    post.tags = post_tags
    #return post_tags
    post.put()
    redirect('/')    

@app.route('/error')
def error_page():  
  return "Error!"

@app.error(403)
def Error403(code):
    return 'Get your codes right dude, you caused some error!'

@app.error(404)
def Error404(code):
    return 'Stop cowboy, what are you trying to find?'

run(app=app, server='gae', debug=True)