"""Marine Parts URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from oscar.app import application


urlpatterns = [
    url(
        r'^i18n/',
        include('django.conf.urls.i18n')
    ),
    # The Django admin is not officially supported; expect breakage.
    # Nonetheless, it's often useful for debugging.

    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/', include('haystack.urls')),
]

# Prefix Oscar URLs with language codes
urlpatterns += i18n_patterns(
    # Oscar's normal URLs
    url(r'^', application.urls),
)


urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
