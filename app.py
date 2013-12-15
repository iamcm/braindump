import random
import string
import json
import datetime
import os 
import bottle
import settings
from Helpers import logger
from mongorm.EntityManager import EntityManager
from Auth.auth import AuthService, User, AuthPlugin
from Auth.apps import auth_app
from models.Models import *
from Helpers.emailHelper import Email
from BottlePlugins import ViewdataPlugin
from forms.Forms import *
from FormBinder import FormBinderPlugin

auth_plugin = AuthPlugin(EntityManager())
form_binder_plugin = FormBinderPlugin()


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

def get_tags():
    return EntityManager().find('Tag', sort=[('slug', 1)])


def common_view_data():
    if bottle.request.session:
        user = EntityManager().find_one_by_id('User', bottle.request.session.user_id)
    else:
        user = None

    vd = {
        'tags': get_tags(),
        'logged_in_user': user
    }

    return vd

viewdata_plugin = ViewdataPlugin(callback_function=common_view_data)



def save_item(item, newtagname):
    em = EntityManager()

    if newtagname:
        existingTag = em.find_one('Tag', {'name':newtagname})
        if existingTag:
            newTagId = existingTag._id
        else:
            t = Tag()
            t.name = newtagname
            t = em.save('Tag', t)
            newTagId = t._id

        if not item.tagIds:
            item.tagIds = []

        item.tagIds.append(str(newTagId))
    
    em.save('Item', item)


#######################################################
# Main app routes
#######################################################
@bottle.route('/')
def index(): 
    return bottle.template('index.tpl', vd=bottle.response.viewdata)


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
            bottle.response.viewdata.update({'items':items})
            return bottle.template('index.tpl', vd=bottle.response.viewdata)
        
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
        bottle.response.viewdata.update({'items':items})
        return bottle.template('index.tpl', vd=bottle.response.viewdata)


@bottle.route('/item', method='GET')
def index():
    tags_select_items = [(str(t._id), t.name) for t in get_tags()]
    bottle.response.viewdata.update({
        'form': ItemForm(tags_select_items).get_html(form_id='form-add-item', row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('item.tpl', vd=bottle.response.viewdata)



@bottle.route('/item', method='POST', apply=[form_binder_plugin], form=ItemForm)
def index():
    form = bottle.request.form

    if form.is_valid():
        i = form.hydrate_entity(Item())
        save_item(i, form.get_value('newTag'))
        return bottle.redirect('/items')        

    for item in form.formitems:
        if item.name == 'tagIds':
            item.select_list_items = [(str(t._id), t.name) for t in get_tags()]

    bottle.response.viewdata.update({
        'form': form.get_html(row_class='form-group', submit_btn_class='btn btn-primary')
    })    

    return bottle.template('item.tpl', vd=bottle.response.viewdata)


@bottle.route('/item/:itemid/edit', method='GET')
def index(itemid):
    em = EntityManager()
    
    item = em.find_one_by_id('Item', itemid)

    tags_select_items = [(str(t._id), t.name) for t in get_tags()]

    bottle.response.viewdata.update({
        'form': ItemForm(tags_select_items, entity=item).get_html(form_id='form-add-item', action='/item', row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('item.tpl', vd=bottle.response.viewdata)


@bottle.route('/item/:itemid/content', method='GET')
def index(itemid):
    em = EntityManager()
    
    item = em.find_one_by_id('Item', itemid)

    return item.content.replace('\n','<br />')


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
        return bottle.template('tags.tpl', vd=bottle.response.viewdata)


@bottle.route('/tag', method='GET')
def index():
    bottle.response.viewdata.update({
        'form': TagForm().get_html(row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('tag.tpl', vd=bottle.response.viewdata)


@bottle.route('/tag', method='POST', apply=[form_binder_plugin], form=TagForm)
def index():
    form = bottle.request.form

    if form.is_valid():
        em = EntityManager()

        t = form.hydrate_entity(Tag())

        if EntityManager().find_raw('Tag', objfilter={'name': t.name}, count=True) == 0:
            em.save('Tag', t)

            return bottle.redirect('/tags')

        else:
            form.errors.append('A Tag with that name already exists')


    bottle.response.viewdata.update({
        'form': form.get_html(row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('tag.tpl', vd=bottle.response.viewdata)


@bottle.route('/tag/:tagid/edit', method='GET')
def index(tagid):
    em = EntityManager()
    tag = em.find_one_by_id('Tag', tagid)

    bottle.response.viewdata.update({
        'form': TagForm(entity=tag).get_html(action='/tag', row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('tag.tpl', vd=bottle.response.viewdata)


@bottle.route('/tag/:tagid/delete')
def index(tagid):
    em = EntityManager()
    
    em.remove_one('Tag', tagid)

    return bottle.redirect('/tags')


@bottle.route('/api-key', method='GET')
def index():
    em = EntityManager()

    user = em.find_one('User', {'_id':bottle.request.session.user_id})

    bottle.response.viewdata.update({'key':user.api_key})
    return bottle.template('api-key.tpl', vd=bottle.response.viewdata)


@bottle.route('/api-key', method='POST')
def index():
    a = AuthService(EntityManager())

    a.generate_api_key(bottle.request.session.user_id)

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
        bottle.response.viewdata.update({'items':items})
        return bottle.template('index.tpl', vd=bottle.response.viewdata)

    


#######################################################



app = bottle.app()
app.install(auth_plugin)
app.install(viewdata_plugin)

app.mount('/auth/', auth_app)


if __name__ == '__main__':
    with open(settings.ROOTPATH +'/app.pid','w') as f:
        f.write(str(os.getpid()))

    if settings.DEBUG: 
        bottle.debug() 
        
    if settings.SERVER == 'gunicorn':    
        bottle.run(server=settings.SERVER, host=settings.APPHOST, port=settings.APPPORT, worker_class='gevent')
    else:
        bottle.run(app=app, server=settings.SERVER, reloader=settings.DEBUG, host=settings.APPHOST, port=settings.APPPORT, quiet=(settings.DEBUG==False) )
    
