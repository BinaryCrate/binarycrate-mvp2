from django.views.generic.base import TemplateView

# Create your views here.

class LandingPageView(TemplateView):

    template_name = "landingpage.html"

