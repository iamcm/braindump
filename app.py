import random
import string
import json
import datetime
import os 
import bottle
import settings
from Helpers import logger
from EntityManager import EntityManager
from Auth.auth import AuthService, User, AuthPlugin
from Auth.apps import auth_app
from models.Models import *
from Helpers.emailHelper import Email

auth_plugin = AuthPlugin(EntityManager())


#######################################################
# Static files
#######################################################
if settings.PROVIDE_STATIC_FILES:
    @bottle.route('/static/<filepath:path>', skip=True)
    def index(filepath):
        return bottle.static_file(filepath, root=settings.ROOTPATH +'/static/')




#######################################################
# Decorators
#######################################################
def JSONResponse(callback):
    def wrapper(*args, **kwargs):
        bottle.response.content_type = 'text/json'
        return callback(*args, **kwargs)
    return wrapper


def ForceHTTP(callback):
    def wrapper(*args, **kwargs):
        if bottle.request.environ.get('HTTP_HTTPS') == 'on':
            return bottle.redirect(bottle.request.url.replace('https://','http://'))

        return callback(*args, **kwargs)
    return wrapper


def ForceHTTPS(callback):
    def wrapper(*args, **kwargs):
        if bottle.request.environ.get('HTTP_HTTPS') == 'off':
            return bottle.redirect(bottle.request.url.replace('http://','https://'))

        return callback(*args, **kwargs)
    return wrapper





def get_tags():
    return EntityManager().find('Tag', sort=[('slug', 1)])


def common_view_data(extradata=None):
    vd = {
        'tags': get_tags()
    }

    if extradata:
        vd.update(extradata)

    return vd




def save_item(item, title, content, tagIds, newtagname):
    em = EntityManager()

    item.title = title
    item.content = content
    item.tagIds = []
    for tagId in tagIds:
        item.tagIds.append(tagId)

    if newtagname:
        t = Tag()
        t.name = newtagname
        t = em.save('Tag', t)

        item.tagIds.append(str(t._id))
    
    em.save('Item', item)


#######################################################
# Main app routes
#######################################################
@bottle.route('/')
def index(): 
    return bottle.template('index.tpl', vd=common_view_data())


@bottle.route('/tag/:slug')
def index(slug):
    em = EntityManager()

    tag = em.find_one('Tag', {'slug': slug})

    if tag:
        criteria = {
            'tagIds':{
                '$in':[str(tag._id)]
            }
        }
        items = em.find('Item', criteria, sort=[('added', -1)])

        if bottle.request.GET.get('apikey'):
            bottle.response.content_type = 'text/json'
            return json.dumps([em.entity_to_json_safe_dict(i) for i in items])
        else:
            return bottle.template('index.tpl', vd=common_view_data({'items':items}))
        
    else:
        return bottle.HTTPError(400)


@bottle.route('/items')
def index():
    em = EntityManager()

    items = em.find('Item', sort=[('added', -1)])

    if bottle.request.GET.get('apikey'):
        bottle.response.content_type = 'text/json'
        return json.dumps([em.entity_to_json_safe_dict(i) for i in items])
    else:
        return bottle.template('index.tpl', vd=common_view_data({'items':items}))


@bottle.route('/item', method='GET')
def index():
    return bottle.template('item.tpl', vd=common_view_data({'item':Item()}))



@bottle.route('/item', method='POST')
def index():
    t = bottle.request.POST.get('title')
    c = bottle.request.POST.get('content')
    tagIds = bottle.request.POST.getall('tagIds[]')
    newtagname = bottle.request.POST.get('tag')

    if (t and tagIds) or (t and newtagname):
        save_item(Item(), t, c, tagIds, newtagname)

    return bottle.redirect('/items')


@bottle.route('/item/:itemid/edit', method='GET')
def index(itemid):
    em = EntityManager()
    
    item = em.find_one_by_id('Item', itemid)

    return bottle.template('item.tpl', vd=common_view_data({'item':item}))


@bottle.route('/item/:itemid/content', method='GET')
def index(itemid):
    em = EntityManager()
    
    item = em.find_one_by_id('Item', itemid)

    return item.content.replace('\n','<br />')


@bottle.route('/item/:itemid/edit', method='POST')
def index(itemid):
    t = bottle.request.POST.get('title')
    c = bottle.request.POST.get('content')
    tagIds = bottle.request.POST.getall('tagIds[]')
    newtagname = bottle.request.POST.get('tag')

    if (t and tagIds) or (t and newtagname):
        em = EntityManager()

        i = em.find_one_by_id('Item', itemid)

        save_item(i, t, c, tagIds, newtagname)

    return bottle.redirect('/items')


@bottle.route('/item/:itemid/delete', method='GET')
def index(itemid):
    em = EntityManager()
    
    em.remove_one('Item', itemid)

    return bottle.redirect('/items')


@bottle.route('/item/:itemid/delete', method='POST')
def index(itemid):
    em = EntityManager()
    
    em.remove_one('Item', itemid)

    return bottle.redirect('/items')






@bottle.route('/tags')
def index():
    if bottle.request.GET.get('apikey'):
        bottle.response.content_type = 'text/json'
        return json.dumps([EntityManager().entity_to_json_safe_dict(t) for t in get_tags()])
    else:
        return bottle.template('tags.tpl', vd=common_view_data())


@bottle.route('/tag', method='GET')
def index():
    return bottle.template('tag.tpl', vd={'tag':Tag()})


@bottle.route('/tag', method='POST')
def index():
    if bottle.request.POST.get('name') and bottle.request.POST.get('name').strip() != '':
        em = EntityManager()

        t = Tag()
        t.name = bottle.request.POST.get('name')
        
        em.save('Tag', t)

    return bottle.redirect('/tags')


@bottle.route('/tag/:tagid/edit', method='GET')
def index(tagid):
    em = EntityManager()
    tag = em.find_one_by_id('Tag', tagid)

    return bottle.template('tag.tpl', vd={'tag':tag})


@bottle.route('/tag/:tagid/edit', method='POST')
def index(tagid):
    if bottle.request.POST.get('name') and bottle.request.POST.get('name').strip() != '':
        em = EntityManager()

        t = em.find_one_by_id('Tag', tagid)

        t.name = bottle.request.POST.get('name')
        
        em.save('Tag', t)

    return bottle.redirect('/tags')


@bottle.route('/tag/:tagid/delete')
def index(tagid):
    em = EntityManager()
    
    em.remove_one('Tag', tagid)

    return bottle.redirect('/tags')


@bottle.route('/api-key', method='GET')
def index():
    em = EntityManager()

    user = em.find_one('User', {'_id':bottle.session.user_id})

    return bottle.template('api-key.tpl', vd=common_view_data({'key':user.api_key}))


@bottle.route('/api-key', method='POST')
def index():
    a = AuthService(EntityManager())

    a.generate_api_key(bottle.session.user_id)

    return bottle.redirect('/api-key')


@bottle.route('/search/:searchterm')
def api_search(searchterm):
    return run_search(searchterm)


@bottle.route('/search/items')
def search():
    searchterm = bottle.request.GET.get('name')
    return run_search(searchterm)


def run_search(searchterm):
    em = EntityManager()

    raw_items = em.fuzzy_text_search('Item', searchterm, 'title')
    raw_items = raw_items + em.fuzzy_text_search('Item', searchterm, 'content')

    ids = [];
    items = []
    for i in raw_items:
        if i._id not in ids:
            ids.append(i._id)
            items.append(i)

    if bottle.request.GET.get('apikey'):
        bottle.response.content_type = 'text/json'
        return json.dumps([em.entity_to_json_safe_dict(i) for i in items])

    elif bottle.request.GET.get('ajax') == "1":
        return bottle.template('items.tpl', {'items':items})

    else:
        return bottle.template('index.tpl', vd=common_view_data({'items':items}))

    


#######################################################



app = bottle.app()
app.install(auth_plugin)
app.mount('/auth/', auth_app)


if __name__ == '__main__':
    with open(settings.ROOTPATH +'/app.pid','w') as f:
        f.write(str(os.getpid()))

    if settings.DEBUG: 
        bottle.debug() 
        
    bottle.run(app=app,server=settings.SERVER, reloader=settings.DEBUG, host=settings.APPHOST, port=settings.APPPORT, quiet=(settings.DEBUG==False) )
