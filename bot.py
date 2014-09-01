# -*- coding: utf-8 -*-
import bottle
import datetime
from bottle import *
from google.appengine.api import users
from google.appengine.ext import ndb
from markdown2 import markdown

app = Bottle()

tags_list = [u"Чушь", u"Креатив", u"Косплей", u"Фоточке", ]

database_key = ndb.Key('Posts', 'submitted_posts')

class Posts(ndb.Model):
    content = ndb.TextProperty(indexed=False, required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    title = ndb.StringProperty(indexed=True, required=True)
    #tags = ndb.StringProperty(required=True, repeated=True, choices=set(tags_list))
    tags = ndb.StringProperty(repeated=True, choices=set(tags_list))
    images = ndb.StringProperty(repeated=True)

@app.route('/')
def main_page():  
    posts_query = Posts.query(ancestor=database_key).order(-Posts.date) 
    posts = posts_query.fetch()   
    output = template('posts.html', posts=posts, tags_list = tags_list)
    return output

@app.route('/who')
def main_page():  
    posts_query = Posts.query(Posts.title=="Кто здесь?").order(-Posts.date) 
    posts = posts_query.fetch()   
    output = template('posts.html', posts=posts, tags_list = tags_list)
    return output
    
@app.route('/tags/<tag>')
def main_page(tag):
   
    posts_query = Posts.query(Posts.tags==tag.decode('utf-8')).order(-Posts.date) 
    posts = posts_query.fetch() 
    if not posts:
        redirect('/')
    output = template('posts.html', posts=posts, tags_list = tags_list)
    return output   
   
@app.route('/posts/<url_id>')
def single_post(url_id):
    posts = ndb.Key(urlsafe=url_id)
    post = Posts.query(ancestor=posts).fetch()
    output = template('posts.html', posts=post, tags_list=tags_list)
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
    photos = []
    for photo_id in range(1,9):
        photo = request.forms.get('photo_%s' % photo_id)
        photos.append(photo)
    #return post_tags
    post.images = photos
    post.put()
    redirect('/')    

@app.route('/edit/<url_id>')
def edit_post(url_id):
    user = users.get_current_user()
    if not user:
        redirect(users.create_login_url('/add'))
    elif not users.is_current_user_admin():
        redirect('/')
    posts = ndb.Key(urlsafe=url_id)
    post = Posts.query(ancestor=posts).fetch()
    photos = {}
    i = 1
    for photo in post[0].images:
        photos["%s" % i] = photo
        i += 1
    output = template('add.html', tags_list = tags_list, title = post[0].title, content = post[0].content, selection = post[0].tags, action="edit", photos=photos, url_id=url_id )
    return output
    
@app.route('/edit', method='POST')
def edit_post():
    user = users.get_current_user()
    if not user:
        redirect(users.create_login_url('/add'))
    elif not users.is_current_user_admin():
        redirect('/')
    
    url_id = request.forms.get('url_id')
    #return url_id
    post = ndb.Key(urlsafe=url_id).get()
    #post = Posts.query(ancestor=post_key).fetch()
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