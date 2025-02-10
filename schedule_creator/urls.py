# from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
# from ms_identity_web.django.msal_views_and_urls import MsalViews
# from edu_resources.views import auth_callback

# msal_urls = MsalViews(settings.MS_IDENTITY_WEB).url_patterns()

urlpatterns = [
    settings.AUTH.urlpattern,
    path('admin/', admin.site.urls),
    path('', include('edu_resources.urls')),
    # path('oauth2/', include('django_auth_adfs.urls')),
    # path('auth-callback/', auth_callback, name='auth_callback'),
    # settings.AUTH.urlpattern,
]
