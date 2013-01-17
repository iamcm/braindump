# Create your views here.
from django.shortcuts import render_to_response, HttpResponseRedirect
from core.models import Item, Tag
from core.forms import ItemForm, TagForm, LoginForm
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import auth

from urlparse import urlparse
############################
############################

def get_safe_url(url, safehost):
	parsed = urlparse(url)
	if parsed.netloc and parsed.netloc != safehost:
		#this is bad redirect to home
		return '/'
	else:
		return url

def login(request):
	if request.POST:
		postdata = request.POST
		f = LoginForm(postdata)
		if f.is_valid():
			u = auth.authenticate(username=postdata['username'], password=postdata['password'])
			if u and u.is_active:
				auth.login(request, u)

				if request.GET['next']:
					redirect_to = get_safe_url(request.GET['next'], request.get_host())
				else:
					redirect_to = '/'

				return HttpResponseRedirect(redirect_to)

	else:
		f = LoginForm()
	return render_to_response('core/login.html', {'form':f.as_p()}, context_instance=RequestContext(request))


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
		items = Item.objects.order_by('-added')
	else:
		items = Item.objects.filter(tags__slug=slug).order_by('-added')

	tags = Tag.objects.all()

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
	tags = Tag.objects.all()
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
