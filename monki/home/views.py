import datetime

from django.views import generic

from monki.boards.models import Ban, Image, Post, Video
from monki.home.models import New, FAQ, Rule


class IndexView(generic.TemplateView):
    template_name = 'home/index.html'


class NewsView(generic.ListView):
    model = New
    template_name = 'home/news.html'


class FAQView(generic.ListView):
    model = FAQ
    template_name = 'home/faq.html'


class RulesView(generic.ListView):
    model = Rule
    template_name = 'home/rules.html'


class BansView(generic.ListView):
    model = Ban
    template_name = 'home/bans.html'


class StatsView(generic.TemplateView):
    template_name = 'home/stats.html'

    def get_uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])

        return str(datetime.timedelta(seconds=uptime_seconds))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'bans': Ban.objects.count(),
            'images': Image.objects.count(),
            'posts': Post.objects.count(),
            'videos': Video.objects.count(),
            'uptime': self.get_uptime()
        })

        return context
