from django.conf.urls import url
from landingpage.views import LandingPageView


app_name = 'landingpage'


urlpatterns = [

    url(r'^$', LandingPageView.as_view(), name='landingpage'),



]
