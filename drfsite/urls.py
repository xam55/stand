from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from wmen.views import ReportCreateView, ReportDetailView, WomenApiView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),


    path('api/v1/womenlist/', WomenApiView.as_view()),

    path('api/v1/womenlist/<int:pk>/',WomenApiView.as_view()),

    path('api/v1/reports/', ReportCreateView.as_view()),
    path('api/v1/reports/<int:pk>/', ReportDetailView.as_view()),

    path('api/v1/accounts/', include('accounts.urls')),


    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
]

urlpatterns += staticfiles_urlpatterns()
