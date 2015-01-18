import sys
import random
import string
import json
import datetime
import os 
import bottle
import settings
from Helpers import logger
from mongorm.EntityManager import EntityManager
from models.Models import *
from Helpers.emailHelper import Email
from forms.Forms import *
from FormBinder import FormBinderPlugin
from shared.decorators import authenticate, force_protocol
from shared.auth import *

form_binder_plugin = FormBinderPlugin()

CLIENT_ID = 'braindump_jdue18ju891fnjhue2n3c03'
#################################
#################################
#################################
CAN_REGISTER = False
@bottle.route('/login', method=['get'])
@force_protocol('https')
def index(**kw):
    content = login_get(bottle, CAN_REGISTER)
    return bottle.template('public', content=content)

@bottle.route('/login', method=['post'])
@force_protocol('https')
def index(**kw):
    return login_post(bottle, CLIENT_ID)

@bottle.route('/logout')
def index(**kw):
    return logout(bottle, CLIENT_ID)

if CAN_REGISTER:
    @bottle.route('/register', method=['get'])
    def index(**kw):
        header_text = "Register"
        content = register_get(bottle)
        return bottle.template('public', content=content)

    @bottle.route('/register', method=['post'])
    def index(**kw):
        user_id = register_post(bottle, CLIENT_ID, success_url=None)
        rpc('user_details', 'save', CLIENT_ID, user_id, {'email':bottle.request.POST.get('email')})
        return bottle.redirect('/login')
#################################
#################################
#################################


#######################################################
# Static files
#######################################################
if settings.PROVIDE_STATIC_FILES:
    @bottle.route('/static/<filepath:path>', skip=True)
    def index(filepath):
        return bottle.static_file(filepath, root=settings.ROOTPATH +'/static/')

@bottle.route('/userfiles/<filepath:path>')
def index(filepath):
    return bottle.static_file(filepath, root=settings.USERFILESPATH)




#######################################################
# Decorators
#######################################################

def get_tags():
    return EntityManager().find('Tag', sort=[('slug', 1)])


def common_view_data(session=None):
    if session:
        user = session['data']['user']
    else:
        user = None

    vd = {
        'tags': get_tags(),
        'logged_in_user': user
    }

    return vd




def save_item(item, newtagname):
    em = EntityManager()

    if item._id:
        #recall existing files for this item
        existingItem = em.find_one_by_id('Item', item._id)
        if existingItem is not None:
            for f in existingItem.files:
                item.files.append(f)



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


def randomfilename():
    return ''.join(random.sample(string.letters + string.digits, 25))


#######################################################
# Main app routes
#######################################################
@bottle.route('/')
@authenticate(CLIENT_ID)
def index(session): 
    return bottle.template('index.tpl', vd=common_view_data(session))


@bottle.route('/tag/:slug')
@authenticate(CLIENT_ID)
def index(slug, session):
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
            vd = common_view_data(session)
            vd.update({'items':items})
            return bottle.template('index.tpl', vd=vd)
        
    else:
        return bottle.HTTPError(400)


@bottle.route('/items')
@authenticate(CLIENT_ID)
def index(session):
    em = EntityManager()

    items = em.find('Item', sort=[('added', -1)])

    if bottle.request.GET.get('apikey'):
        bottle.response.content_type = 'text/json'
        return json.dumps([em.entity_to_json_safe_dict(i) for i in items])
    else:
        vd = common_view_data(session)
        vd.update({'items':items})
        return bottle.template('index.tpl', vd=vd)


@bottle.route('/item', method='GET')
@authenticate(CLIENT_ID)
def index(session):
    tags_select_items = [(str(t._id), t.name) for t in get_tags()]
    vd = common_view_data(session)
    vd.update({
        'form': ItemForm(tags_select_items).get_html(form_id='form-add-item', row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('item.tpl', vd=vd)



@bottle.route('/item', method='POST', apply=[form_binder_plugin], form=ItemForm)
@authenticate(CLIENT_ID)
def index(session):
    form = bottle.request.form

    if form.is_valid():
        i = form.hydrate_entity(Item())
        #associate any uploaded files:
        em = EntityManager()
        for f in em.find('File', {'session_id': session['session_id']}):
            f.session_id = None
            em.save('File', f)
            i.files.append(f)

        save_item(i, form.get_value('newTag'))

        return bottle.redirect('/items')        

    for item in form.formitems:
        if item.name == 'tagIds':
            item.select_list_items = [(str(t._id), t.name) for t in get_tags()]

    vd = common_view_data(session)
    vd.update({
        'form': form.get_html(row_class='form-group', submit_btn_class='btn btn-primary')
    })    

    return bottle.template('item.tpl', vd=vd)


@bottle.route('/item/:itemid/edit', method='GET')
@authenticate(CLIENT_ID)
def index(session, itemid):
    em = EntityManager()
    
    item = em.find_one_by_id('Item', itemid)

    tags_select_items = [(str(t._id), t.name) for t in get_tags()]

    vd = common_view_data(session)
    vd.update({
        'form': ItemForm(tags_select_items, entity=item).get_html(form_id='form-add-item', action='/item', row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('item.tpl', vd=vd)


@bottle.route('/item/:itemid/content', method='GET')
@authenticate(CLIENT_ID)
def index(session, itemid):
    em = EntityManager()
    
    item = em.find_one_by_id('Item', itemid)

    return item.content.replace('\n','<br />')


@bottle.route('/item/:itemid/delete', method='GET')
@authenticate(CLIENT_ID)
def index(session, itemid):
    em = EntityManager()
    
    item = em.find_one_by_id('Item', itemid)

    #delete any uploaded files for this item
    if item.files:
        for f in item.files:
            fullpath = os.path.join(settings.USERFILESPATH, f.sysname)
            #thumbpath = os.path.join(settings.USERFILESPATH, 'thumb_'+ f.sysname)

            os.system('rm '+ fullpath)
            #os.system('rm '+ thumbpath)

            em.remove_one('File', f._id)

    em.remove_one('Item', itemid)

    return bottle.redirect('/items')


@bottle.route('/item/:itemid/delete', method='POST')
@authenticate(CLIENT_ID)
def index(session, itemid):
    em = EntityManager()
    
    em.remove_one('Item', itemid)

    return bottle.redirect('/items')






@bottle.route('/tags')
@authenticate(CLIENT_ID)
def index(session):
    if bottle.request.GET.get('apikey'):
        bottle.response.content_type = 'text/json'
        return json.dumps([EntityManager().entity_to_json_safe_dict(t) for t in get_tags()])
    else:
        return bottle.template('tags.tpl', vd=common_view_data(session))


@bottle.route('/tag', method='GET')
@authenticate(CLIENT_ID)
def index(session):
    vd = common_view_data(session)
    vd.update({
        'form': TagForm().get_html(row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('tag.tpl', vd=vd)


@bottle.route('/tag', method='POST', apply=[form_binder_plugin], form=TagForm)
@authenticate(CLIENT_ID)
def index(session):
    form = bottle.request.form

    if form.is_valid():
        em = EntityManager()

        t = form.hydrate_entity(Tag())

        if EntityManager().find_raw('Tag', objfilter={'name': t.name}, count=True) == 0:
            em.save('Tag', t)

            return bottle.redirect('/tags')

        else:
            form.errors.append('A Tag with that name already exists')

    vd = common_view_data(session)
    vd.update({
        'form': form.get_html(row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('tag.tpl', vd=vd)


@bottle.route('/tag/:tagid/edit', method='GET')
@authenticate(CLIENT_ID)
def index(session, tagid):
    em = EntityManager()
    tag = em.find_one_by_id('Tag', tagid)

    vd = common_view_data(session)
    vd.update({
        'form': TagForm(entity=tag).get_html(action='/tag', row_class='form-group', submit_btn_class='btn btn-primary')
    })

    return bottle.template('tag.tpl', vd=vd)


@bottle.route('/tag/:tagid/delete')
@authenticate(CLIENT_ID)
def index(session, tagid):
    em = EntityManager()
    
    em.remove_one('Tag', tagid)

    return bottle.redirect('/tags')


@bottle.route('/api-key', method='GET')
@authenticate(CLIENT_ID)
def index(session):
    vd = common_view_data(session)
    vd.update({'key':session['data']['user']['api_key']})
    return bottle.template('api-key.tpl', vd=vd)


@bottle.route('/api-key', method='POST')
@authenticate(CLIENT_ID)
def index(session):
    user = rpc('auth','regenerate_api_key', {'clientId':CLIENT_ID, 'email':session['data']['user']['email']})
    session['data']['user'] = user

    rpc('session', 'save', CLIENT_ID, session['session_id'], session['data'])

    return bottle.redirect('/api-key')


@bottle.route('/search/:searchterm')
@authenticate(CLIENT_ID)
def index(session, searchterm):
    return run_search(session, searchterm)


@bottle.route('/search/items')
@authenticate(CLIENT_ID)
def index(session):
    searchterm = bottle.request.GET.get('name')
    return run_search(session, searchterm)


def run_search(session, searchterm):
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
        vd = common_view_data(session)
        vd.update({'items':items})
        return bottle.template('index.tpl', vd=vd)

    



@bottle.route('/upload', method='POST')
@authenticate(CLIENT_ID)
def index(session):
    uploadedFile = bottle.request.files.get('file')
    if uploadedFile:
        nicename, ext = os.path.splitext(uploadedFile.filename)

        newname = randomfilename() + ext
        savepath = os.path.join(settings.USERFILESPATH, newname)
        while os.path.isfile(savepath):
            newname = randomfilename() + ext
            savepath = os.path.join(settings.USERFILESPATH, newname)

        uploadedFile.save(savepath)

        """thumbpath = os.path.join(settings.USERFILESPATH, 'thumb_'+ newname)

        try:
            os.system('convert %s -resize 150 %s' % (savepath, thumbpath))
        except:
            os.system('cp %s %s' % (savepath, thumbpath))"""

        f = File()
        f.nicename = uploadedFile.filename
        f.sysname = newname
        f.session_id = session['session_id']
        EntityManager().save('File', f)


#######################################################

app = bottle.app()

if __name__ == '__main__':
    with open(settings.ROOTPATH +'/app.pid','w') as f:
        f.write(str(os.getpid()))

    if settings.DEBUG: 
        bottle.debug() 
        
    if settings.SERVER == 'gunicorn':    
        bottle.run(server=settings.SERVER, host=settings.APPHOST, port=settings.APPPORT, worker_class='gevent')
    else:
        bottle.run(app=app, server=settings.SERVER, reloader=settings.DEBUG, host=settings.APPHOST, port=settings.APPPORT, quiet=(settings.DEBUG==False) )
    
