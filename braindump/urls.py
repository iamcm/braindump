from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'core.views.home', name='home'),
    url(r'^login$', 'core.views.login', name='login'),
    url(r'^logout$', 'core.views.logout', name='logout'),
    url(r'^filter/tag/([a-zA-Z-]+)$', 'core.views.filter_tag', name='filter_tag'),
    url(r'^filter/search/([a-zA-Z- ]+)$', 'core.views.filter_search', name='filter_search'),
    url(r'^item$', 'core.views.item', name='item'),
    url(r'^item/(\d+)$', 'core.views.item_edit', name='item_edit'),
    url(r'^item/delete/(\d+)$', 'core.views.item_delete', name='item_delete'),
    url(r'^tags$', 'core.views.tags', name='tags'),
    url(r'^tag$', 'core.views.tag', name='tag'),
    url(r'^tag/(\d+)$', 'core.views.tag_edit', name='tag_edit'),
    url(r'^tag/delete/(\d+)$', 'core.views.tag_delete', name='tag_delete'),
    # url(r'^braindump/', include('braindump.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
