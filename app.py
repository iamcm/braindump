import random
import string
import json
import datetime
import os 
import bottle
import settings
from Helpers import logger
from EntityManager import EntityManager
from Auth.auth import AuthService, User
from models.Models import *
from Helpers.emailHelper import Email



#######################################################
# Static files
#######################################################
if settings.PROVIDE_STATIC_FILES:
    @bottle.route('/static/<filepath:path>')
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


def checklogin(callback, redirect_url='/login'):
    def wrapper(*args, **kwargs):

        if bottle.request.get_cookie('token'):
            a = AuthService(EntityManager())
            
            session =  a.check_session(bottle.request.get_cookie('token')
                                        , bottle.request.get('REMOTE_ADDR')
                                        , bottle.request.get('HTTP_USER_AGENT'))

            if not session:
                if redirect_url is not None:
                    return bottle.redirect(redirect_url)
                else:
                    return bottle.HTTPError(403, 'Access denied')

            else:
                bottle.response.set_cookie('token', str(session.public_id),\
                                       expires=session.expires,\
                                        httponly=True, path='/')
                
                bottle.session = session

                return callback(*args, **kwargs)

        
        elif bottle.request.GET.get('apikey'):
            users = self.em.find('User', {'api_key':bottle.request.GET.get('apikey')})

            if len(users)==1:
                return callback(*args, **kwargs)
            else:
                return bottle.HTTPError(403, 'Access denied')

        else:
            if redirect_url is not None:
                return bottle.redirect(redirect_url)
            else:
                return bottle.HTTPError(403, 'Access denied')

    return wrapper





#######################################################
# Main app routes
#######################################################
@bottle.route('/login')
def login():
    return bottle.template('login.tpl', vd={})


@bottle.route('/login', method='POST')
def login():
    e = bottle.request.POST.get('email')
    p = bottle.request.POST.get('password')
    ip = bottle.request.get('REMOTE_ADDR')
    ua = bottle.request.get('HTTP_USER_AGENT')

    error = None

    if e and p:
        a = AuthService(EntityManager())

        session = a.login(e, p, ip, ua)

        if session:
            bottle.response.set_cookie('token', str(session.public_id),\
                                       expires=session.expires,\
                                        httponly=True, path='/')

            # bottle.redirect('/') //this clears cookies
            res = bottle.HTTPResponse("", status=302, Location="/")
            res._cookies = bottle.response._cookies
            return res

        else:
            error = a.errors[0]

    return bottle.template('login.tpl', vd={
            'error':error
        })

@bottle.route('/logout')
@checklogin
def logout():
    a = AuthService(EntityManager())
    a.logout(bottle.session)

    bottle.redirect('/')



@bottle.route('/forgotten-password', method='GET')
def forgotten_password():
    return bottle.template('forgotten_password', vd={})


@bottle.route('/forgotten-password', method='POST')
def forgotten_password():
    e = bottle.request.POST.get('email')

    a = AuthService(EntityManager())
    token = a.generate_password_token(e)

    if token:
        e = Email(recipients=[e])
        body = 'You have requested to reset your password for www.fotodelic.co.uk, please follow this link to reset it:\n\r\n https://%s/reset-password/%s' % (bottle.request.environ['HTTP_HOST'], token)
        e.send('Fotodelic - password reset request', body)               

        return bottle.redirect('/forgotten-password-sent')


    return bottle.template('forgotten_password', vd={
            'error':a.errors[0]
        })



@bottle.route('/forgotten-password-sent', method='GET')
def forgotten_password():
    return bottle.template('forgotten_password_sent', vd={})



@bottle.route('/reset-password/:key', method='GET')
def index(key):
    return bottle.template('reset_password', vd={'key':key})


@bottle.route('/reset-password/:key', method='POST')
def index(key):
    k = bottle.request.POST.get('key')
    p = bottle.request.POST.get('password')
    p2 = bottle.request.POST.get('password2')
    error = None

    if (p and p2) and (p==p2):
        a = AuthService(EntityManager())
        if a.reset_password(key, p):
            return bottle.redirect('/reset-password-success')

        else:
            error = a.errors[0]

    else:
        error = 'Please enter two matching passwords'


    return bottle.template('reset_password', vd={
        'error': error
        })



@bottle.route('/reset-password-success', method='GET')
def index():
    return bottle.template('reset_password_success', vd={})





def common_view_data(extradata=None):
    vd = {
        'tags': EntityManager().find('Tag', sort=[('slug', 1)])
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
@checklogin
def index(): 
    return bottle.template('index.tpl', vd=common_view_data())


@bottle.route('/tag/:slug')
@checklogin
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

        return bottle.template('index.tpl', vd=common_view_data({'items':items}))
        
    else:
        return bottle.HTTPError(400)


@bottle.route('/items')
@checklogin
def index():
    em = EntityManager()

    items = em.find('Item', sort=[('added', -1)])

    return bottle.template('index.tpl', vd=common_view_data({'items':items}))


@bottle.route('/item', method='GET')
@checklogin
def index():
    return bottle.template('item.tpl', vd=common_view_data({'item':Item()}))



@bottle.route('/item', method='POST')
@checklogin
def index():
    t = bottle.request.POST.get('title')
    c = bottle.request.POST.get('content')
    tagIds = bottle.request.POST.getall('tagIds[]')
    newtagname = bottle.request.POST.get('tag')

    if (t and tagIds) or (t and newtagname):
        save_item(Item(), t, c, tagIds, newtagname)

    return bottle.redirect('/items')


@bottle.route('/item/:itemid/edit', method='GET')
@checklogin
def index(itemid):
    em = EntityManager()
    
    item = em.find_one_by_id('Item', itemid)

    return bottle.template('item.tpl', vd=common_view_data({'item':item}))


@bottle.route('/item/:itemid/edit', method='POST')
@checklogin
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


@bottle.route('/item/:itemid/delete')
@checklogin
def index(itemid):
    em = EntityManager()
    
    em.remove_one('Item', itemid)

    return bottle.redirect('/items')






@bottle.route('/tags')
@checklogin
def index():
    return bottle.template('tags.tpl', vd=common_view_data())


@bottle.route('/tag', method='GET')
@checklogin
def index():
    return bottle.template('tag.tpl', vd={'tag':Tag()})


@bottle.route('/tag', method='POST')
@checklogin
def index():
    if bottle.request.POST.get('name') and bottle.request.POST.get('name').strip() != '':
        em = EntityManager()

        t = Tag()
        t.name = bottle.request.POST.get('name')
        
        em.save('Tag', t)

    return bottle.redirect('/tags')


@bottle.route('/tag/:tagid/edit', method='GET')
@checklogin
def index(tagid):
    em = EntityManager()
    tag = em.find_one_by_id('Tag', tagid)

    return bottle.template('tag.tpl', vd={'tag':tag})


@bottle.route('/tag/:tagid/edit', method='POST')
@checklogin
def index(tagid):
    if bottle.request.POST.get('name') and bottle.request.POST.get('name').strip() != '':
        em = EntityManager()

        t = em.find_one_by_id('Tag', tagid)

        t.name = bottle.request.POST.get('name')
        
        em.save('Tag', t)

    return bottle.redirect('/tags')


@bottle.route('/tag/:tagid/delete')
@checklogin
def index(tagid):
    em = EntityManager()
    
    em.remove_one('Tag', tagid)

    return bottle.redirect('/tags')


@bottle.route('/tags')
@checklogin
def index():
    return bottle.template('tags.tpl', vd=common_view_data())


@bottle.route('/api-key', method='GET')
@checklogin
def index():
    em = EntityManager()

    user = em.find_one('User', {'_id':bottle.session.user_id})

    return bottle.template('api-key.tpl', vd=common_view_data({'key':user.api_key}))


@bottle.route('/api-key', method='POST')
@checklogin
def index():
    a = AuthService(EntityManager())

    a.generate_api_key(bottle.session.user_id)

    return bottle.redirect('/api-key')


@bottle.route('/search/items')
@checklogin
def index():
    searchterm = bottle.request.GET.get('name')
    
    em = EntityManager()

    raw_items = em.fuzzy_text_search('Item', searchterm, 'title')
    raw_items = raw_items + em.fuzzy_text_search('Item', searchterm, 'content')

    ids = [];
    items = []
    for i in raw_items:
        if i._id not in ids:
            ids.append(i._id)
            items.append(i)

    if bottle.request.GET.get('ajax') == "1":
        return bottle.template('items.tpl', {'items':items})
    else:
        return bottle.template('index.tpl', vd=common_view_data({'items':items}))

    


#######################################################



app = bottle.app()

if __name__ == '__main__':
    with open(settings.ROOTPATH +'/app.pid','w') as f:
        f.write(str(os.getpid()))

    if settings.DEBUG: 
        bottle.debug() 
        
    bottle.run(app=app,server=settings.SERVER, reloader=settings.DEBUG, host=settings.APPHOST, port=settings.APPPORT, quiet=(settings.DEBUG==False) )
