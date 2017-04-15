from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render
from django.utils import crypto, timezone
from django.utils.deprecation import MiddlewareMixin

from monki.boards.models import Ban


class UserCookieMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        cid = request.get_signed_cookie('cid', None)

        if not cid:
            response.set_signed_cookie(
                'cid',
                crypto.get_random_string(),
                max_age=settings.CSRF_COOKIE_AGE,
                httponly=True,
            )

        return response


class UserBanMiddleware(MiddlewareMixin):

    def process_request(self, request):

        if request.path.startswith(reverse('admin:index')):
            return None

        def banned(request, bans):
            response = render(request, 'banned.html', context={'bans': bans})
            response.status_code = 403
            response.reason_phrase = 'You\'re Banned!'

            return response

        if request.method == 'POST':
            bans = Ban.objects.filter(
                Q(ip_address=request.META['REMOTE_ADDR']),
                Q(expires_at__gte=timezone.now()) | Q(expires_at__isnull=True)
            )

            if bans:
                return banned(request, bans)

        return None
