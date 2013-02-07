# Create your views here.
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
############################
############################

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
	if request.POST:
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

		postdata = request.POST
		f = LoginForm(postdata)
		if f.is_valid():
			u = auth.authenticate(username=postdata['username'], password=postdata['password'])
			if u:
				if u.is_active:
					auth.login(request, u)

					if request.GET.get('next'):
						redirect_to = get_safe_url(request.GET['next'], request.get_host())
					else:
						redirect_to = '/'

					return HttpResponseRedirect(redirect_to)
			else:
				f= FailedLogin()
				f.ip = ip
				f.save()

				mail_admins('Failed login attempt', str(request.POST))
				return HttpResponseRedirect('/login')

	else:
		f = LoginForm()

	return render_to_response('core/login.html', {'form':f.as_p()}, context_instance=RequestContext(request))


def api_login_required(fn):
 	def wrap(request, *args, **kwargs):
 		key = request.GET.get('key')
 		user = User.objects.filter(api_key=key)
 		if user:
 			request.user = user[0]
 			return fn(request, *args, **kwargs)
 		else:
 			return HttpResponse(status=403)
 		 			
	return wrap





@login_required()
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/login')


############################
############################
@login_required()
def home(request):
	tags = Tag.objects.order_by('name')
	return render_to_response('core/index.html', {'tags':tags})


@login_required()
def filter_tag(request, slug):
	if slug.lower() == 'all':
		items = Item.objects.order_by('-added')
	else:
		items = Item.objects.filter(tags__slug=slug).order_by('-added')

	tags = Tag.objects.order_by('name')

	return render_to_response('core/index.html', {'items':items, 'tags':tags})


@login_required()
def filter_search(request, searchterm):
	items = Item.objects.filter(Q(title__icontains=searchterm) | Q(content__icontains=searchterm)).order_by('-added')
	return render_to_response('core/items.html', {'items':items})


############################
############################

@login_required()
def item(request):
	if request.POST:
		f = ItemForm(request.POST)
		if f.is_valid():
			f.save()
			return HttpResponseRedirect('/')

	else:
		f = ItemForm()

	return render_to_response('core/item.html', {'form':f.as_p() }, context_instance=RequestContext(request))


@login_required()
def item_edit(request, id):
	i = Item.objects.get(pk=id)

	if request.POST:
		f = ItemForm(request.POST, instance=i)		
		if f.is_valid():
			f.save()
			return HttpResponseRedirect('/')

	else:		
		f = ItemForm(instance=i)

	return render_to_response('core/item.html', {'form':f.as_p() }, context_instance=RequestContext(request))


@login_required()
def item_delete(request, id):
	i = Item(id)
	i.delete()
	
	return HttpResponseRedirect('/')

############################
############################


@login_required()
def tags(request):
	tags = Tag.objects.order_by('name')
	return render_to_response('core/tags.html', {'tags':tags})


@login_required()
def tag(request):
	if request.POST:
		f = TagForm(request.POST)
		if f.is_valid():
			f.save()
			return HttpResponseRedirect('/')
	else:
		f = TagForm()

	return render_to_response('core/tag.html', {'form':f.as_p() }, context_instance=RequestContext(request))


@login_required()
def tag_edit(request, id):
	i = Tag.objects.get(pk=id)

	if request.POST:
		f = TagForm(request.POST, instance=i)
		if f.is_valid():
			f.save()
			return HttpResponseRedirect('/')
	else:
		f = TagForm(instance=i)

	return render_to_response('core/tag.html', {'form':f.as_p() }, context_instance=RequestContext(request))


@login_required()
def tag_delete(request, id):
	i = Tag(id)
	i.delete()
	
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


@api_login_required
def api_tags(request):
	tags = [{'id':str(t['id']), 'name':str(t['name']), 'slug':str(t['slug'])} for t in Tag.objects.values().order_by('name')]

	return JSONResponse(tags, request.GET.get('callback'))


@api_login_required
def api_filter_tag(request, slug):
	if slug.lower() == 'all':
		items = [{'id':str(i['id']), 'title':str(i['title']), 'content':str(i['content'])} for i in Item.objects.order_by('-added').values('id', 'title', 'content')]
	else:
		items = [{'id':str(i['id']), 'title':str(i['title']), 'content':str(i['content'])} for i in Item.objects.filter(tags__slug=slug).order_by('-added').values('id', 'title', 'content')]
	
	return JSONResponse(items, request.GET.get('callback'))
	

@api_login_required
def api_filter_search(request, searchterm):
	_items = Item.objects.filter(Q(title__icontains=searchterm) | Q(content__icontains=searchterm)).order_by('-added').values('id', 'title', 'content')
	items = [{'title':str(i['title']), 'content':str(i['content'])} for i in _items]

	return JSONResponse(items, request.GET.get('callback'))


@csrf_exempt
def api_save_item(request):
	if request.POST:
		f = ItemForm(request.POST)
		if f.is_valid():
			f.save()

	return JSONResponse([], request.GET.get('callback'))


@csrf_exempt
def api_login(request):
	username = request.POST.get('username')
	password = request.POST.get('password')

	if username and password:
		u = auth.authenticate(username=username, password=password)
		if u:
			if u.is_active:
				return JSONResponse({'key':u.api_key}, request.GET.get('callback'))
			else:
				mail_admins('Inactive user trying to log in', str(request.POST))
				return HttpResponse(status=403)
		else:
			mail_admins('Failed login attempt', str(request.POST))
			return HttpResponse(status=403)

	else:
		mail_admins('Failed login attempt, username and password not present', str(request.POST))
		return HttpResponse(status=403)