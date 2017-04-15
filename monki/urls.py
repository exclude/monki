from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from monki.boards import views as boards
from monki.home import views as home

admin.site.site_header = 'xchan'


router = DefaultRouter()
router.register(r'categories', boards.CategoryViewSet)
router.register(r'boards', boards.BoardViewSet)
router.register(r'threads', boards.ThreadViewSet)
router.register(r'post', boards.PostViewSet)


urlpatterns = [
    url(r'^$', home.IndexView.as_view(), name='index'),

    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),

    url(r'^board/(?P<board>\w+)/$', boards.BoardView.as_view(), name='board'),
    url(r'^board/(?P<board>\w+)/thread/(?P<thread>\d+)/$', boards.BoardView.as_view(), name='thread'),

    url(r'^post/(?P<pk>\d+)/$', boards.PostView.as_view(), name='post'),
    url(r'^post/(?P<pk>\d+)/delete/$', boards.PostDeleteView.as_view(), name='post-delete'),

    url(r'^catalog/(?P<board>\w+)/$', boards.CatalogView.as_view(), name='catalog'),

    url(r'^news/$', home.NewsView.as_view(), name='news'),
    url(r'^faq/$', home.FAQView.as_view(), name='faq'),
    url(r'^rules/$', home.RulesView.as_view(), name='rules'),
    url(r'^bans/$', home.BansView.as_view(), name='bans'),
    url(r'^stats/$', home.StatsView.as_view(), name='stats'),

    # In the end to not conflict with other rules
    url(r'^(?P<board>\w+)/$', boards.KusabaCompatView.as_view()),
    url(r'^(?P<board>\w+)/res/(?P<thread>\d+)\.html$', boards.KusabaCompatView.as_view()),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
