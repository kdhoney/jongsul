from django.conf.urls import patterns, url
from .views import UploadURLView, UploadDetailView, UploadImg, ImgListView

urlpatterns = patterns('',
    url(r'^$', UploadURLView.as_view(), name="upload-url"),
    url(r'^up/$', UploadImg),
    url(r'^show/(?P<pk>\d+)/$', UploadDetailView.as_view(), name="upload-detail"),
    url(r'^imglist/$', ImgListView.as_view(), name="imglist-url")
)
