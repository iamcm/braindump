from django.shortcuts import redirect, render_to_response, HttpResponseRedirect, HttpResponse
from core.models import Item, Tag, FailedLogin, BannedIP, User
from core.forms import ItemForm, TagForm, LoginForm
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.mail import mail_admins
from django.views.decorators.csrf import csrf_exempt

from urlparse import urlparse
from datetime import datetime, timedelta
import string
from random import sample
from braindump import settings
#sphinx related
try:
	import MySQLdb
except:
	"""
	live server has MySQLdb installed by default but locally i would need to install the mysql 
	client libraries (maybe even mysql?) so i opt for a pure python mysql client as its required
	for sphinx interations
	"""
	import pymysql as MySQLdb
import sys
sys.path.append(settings.SPHINX_PATH)
import sphinxapi
############################
############################

sphinxclient = sphinxapi.SphinxClient()	

def add_to_sphinx(index, id, text):
	conn = MySQLdb.connect(host='127.0.0.1', port=9306)
	cursor = conn.cursor()
	cursor.execute("REPLACE INTO rt_%s (id, text) VALUES (%s, '%s')" % (index, str(id), text.replace("'","") ))
	conn.commit()

def remove_from_sphinx(index, id):
	conn = MySQLdb.connect(host='127.0.0.1', port=9306)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM rt_%s WHERE id=%s" % (index, str(id)))
	conn.commit()



def generate_api_key():
	key = ''
	for i in sample(string.letters + string.digits, 30):
		key += i

	return key


def get_safe_url(url, safehost):
	parsed = urlparse(url)
	if parsed.netloc and parsed.netloc != safehost:
		#this is bad redirect to home
		return '/'
	else:
		return url

def login(request):
	if request.method == 'POST':
		ip = request.META['REMOTE_ADDR']
		# check for banned ip
		banned = BannedIP.objects.values_list('ip')
		if len(banned)>0 and ip in banned[0]:
			return HttpResponseRedirect('/login')

		# check for more than 3 failed attempts in the last 5 minutes
		dt = datetime.now() - timedelta(minutes=5)
		if FailedLogin.objects.filter(added__gt=dt).count() > 2:
			b = BannedIP()
			b.ip = ip
			b.save()
			return HttpResponseRedirect('/login')

		success_redirect = get_safe_url(request.GET['next'], request.get_host()) if request.GET.get('next') else '/'
		
		return process_login(request, success_redirect, '/login')

	else:
		f = LoginForm()

	return render_to_response('core/login.html', {'form':f.as_p()}, context_instance=RequestContext(request))


def process_login(request, success_redirect=None, error_redirect=None, success_response=None):
	f = LoginForm(request.POST)
	
	if f.is_valid():
		u = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
		if u:
			if u.is_active:
				auth.login(request, u)

				if success_redirect:
					return HttpResponseRedirect(success_redirect)
				elif success_response:
					return success_response
				else:
					return HttpResponse(200)

			else:
				mail_admins('Inactive user attempted to login', '')

				if error_redirect:
					return HttpResponseRedirect(error_redirect)
				else:
					return HttpResponse(status=403)

		else:
			f = FailedLogin()
			f.ip = request.META['REMOTE_ADDR']
			f.save()

			mail_admins('Failed login attempt', '')
			if error_redirect:
				return HttpResponseRedirect(error_redirect)
			else:
				return HttpResponse(status=403)

	else:
		return False





@login_required()
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/login')


############################
############################
@login_required()
def home(request):
	tags = Tag.objects.all()
	return render_to_response('core/index.html', {'tags':tags})


@login_required()
def filter_tag(request, slug):
	if slug.lower() == 'all':
		items = Item.objects.all()
	else:
		items = Item.objects.filter(tags__slug=slug)

	tags = Tag.objects.all()

	return render_to_response('core/index.html', {'items':items, 'tags':tags})


#@login_required()
#def filter_search(request, searchterm):
#	items = Item.objects.filter(Q(title__icontains=searchterm) | Q(content__icontains=searchterm))
#	return render_to_response('core/items.html', {'items':items})

@login_required()
def filter_search(request, searchterm):
	tagids = [int(r['id']) for r in sphinxclient.Query(searchterm+'*', index='rt_tag')['matches']]
	itemids = [int(r['id']) for r in sphinxclient.Query(searchterm+'*', index='rt_item')['matches']]

	items = Item.objects.filter(Q(id__in=itemids) | Q(tags__id__in=set(tagids)))
	return render_to_response('core/items.html', {'items':set(items)})


############################
############################

@login_required()
def item(request):
	if request.method == 'POST':

		postdata = request.POST.copy()
		t = None
		
		if request.POST.get('newTag'):
			t = Tag()
			t.name = request.POST.get('newTag') 
			t.save()	

			if 'tags' in postdata:
				postdata.appendlist('tags', str(t.id))
			else:
				postdata['tags'] = str(t.id)

		f = ItemForm(postdata)
		if f.is_valid():
			i = f.save()

			add_to_sphinx('item', i.id, i.title +' '+i.content)

			if request.POST.get('newTag'):
				add_to_sphinx('tag', t.id, t.name)


			return HttpResponseRedirect('/')
		else:
			if t:
				remove_from_sphinx('tag', t.id)
				t.delete()

	else:
		f = ItemForm()

	return render_to_response('core/item.html', {'form':f.as_p(), 'newTags':request.POST.get('newTag') or '' }, context_instance=RequestContext(request))


@login_required()
def item_edit(request, id):
	i = Item.objects.get(pk=id)

	if request.method == 'POST':
		f = ItemForm(request.POST, instance=i)		
		if f.is_valid():
			i = f.save()
			
			add_to_sphinx('item', i.id, i.title +' '+i.content)

			return HttpResponseRedirect('/')

	else:		
		f = ItemForm(instance=i)

	return render_to_response('core/item.html', {'form':f.as_p() }, context_instance=RequestContext(request))


@login_required()
def item_delete(request, id):
	i = Item(id)
	i.delete()

	remove_from_sphinx('item', id)
	
	return HttpResponseRedirect('/')

############################
############################


@login_required()
def tags(request):
	tags = Tag.objects.all()
	return render_to_response('core/tags.html', {'tags':tags})


@login_required()
def tag(request):
	if request.method == 'POST':
		f = TagForm(request.POST)
		if f.is_valid():
			t = f.save()

			add_to_sphinx('tag', t.id, t.name)

			return HttpResponseRedirect('/')
	else:
		f = TagForm()

	return render_to_response('core/tag.html', {'form':f.as_p() }, context_instance=RequestContext(request))


@login_required()
def tag_edit(request, id):
	i = Tag.objects.get(pk=id)

	if request.method == 'POST':
		f = TagForm(request.POST, instance=i)
		if f.is_valid():
			t = f.save()

			add_to_sphinx('tag', t.id, t.name)

			return HttpResponseRedirect('/')
	else:
		f = TagForm(instance=i)

	return render_to_response('core/tag.html', {'form':f.as_p() }, context_instance=RequestContext(request))


@login_required()
def tag_delete(request, id):
	i = Tag(id)
	i.delete()
	
	remove_from_sphinx('tag', id)

	return HttpResponseRedirect('/')	

@login_required()
def api_key(request):
	key = request.user.api_key

	return render_to_response('core/api_key.html', {'key':key })

@login_required()
def api_key_generate(request):
	key = generate_api_key()
	while User.objects.filter(api_key=key).exists():
		key = generate_api_key()

	request.user.api_key = key
	request.user.save()

	return redirect('api_key')


############################
############################
############################
############################
############################
############################
# API
############################
############################
############################
############################
############################
############################
import json

def JSONResponse(data, callback):
	callback = callback or 'jsonp'
	data = json.dumps(data)
	#data = '%s({"data":%s})' % (callback, json.dumps(data))
	response = HttpResponse(data, content_type="application/json", )
	response['Access-Control-Allow-Origin'] = '*'
	response['Access-Control-Allow-Headers'] = 'X-Requested-With'
	response['Access-Control-Allow-Methods'] = 'GET'
	return response


@login_required(login_url='/mobile/index.html#login')
def api_tags(request):
	tags = [{'id':str(t['id']), 'name':str(t['name']), 'slug':str(t['slug'])} for t in Tag.objects.values()]

	return JSONResponse(tags, request.GET.get('callback'))


@login_required(login_url='/mobile/index.html#login')
def api_filter_tag(request, slug):
	if slug.lower() == 'all':
		items = [{'id':str(i['id']), 'title':str(i['title']), 'content':str(i['content'])} for i in Item.objects.values('id', 'title', 'content')]
	else:
		items = [{'id':str(i['id']), 'title':str(i['title']), 'content':str(i['content'])} for i in Item.objects.filter(tags__slug=slug).values('id', 'title', 'content')]
	
	return JSONResponse(items, request.GET.get('callback'))
	

@login_required(login_url='/mobile/index.html#login')
def api_filter_search(request, searchterm):
	_items = Item.objects.filter(Q(title__icontains=searchterm) | Q(content__icontains=searchterm)).values('id', 'title', 'content')
	items = [{'id':str(i['id']), 'title':str(i['title']), 'content':str(i['content'])} for i in _items]

	return JSONResponse(items, request.GET.get('callback'))


@csrf_exempt
@login_required(login_url='/mobile/index.html#login')
def api_save_item(request):
	if request.method == 'POST':
		f = ItemForm(request.POST)
		if f.is_valid():
			i = f.save()

			add_to_sphinx('item', i.id, i.title +' '+i.content)

	return JSONResponse([], request.GET.get('callback'))


@csrf_exempt
def api_login(request):
	username = request.POST.get('username')
	password = request.POST.get('password')

	if username and password:
		return process_login(request, success_response=JSONResponse([], request.GET.get('callback')))

	else:
		mail_admins('Failed login attempt, username and password not present', '')
		return HttpResponse(status=403)