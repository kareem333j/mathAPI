from django.contrib import admin
from django.urls import path, include

# static files && media files
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    # admin
    path('admin/', admin.site.urls),
    # blog
    path('', include('blog.urls')),
    # API
    path('api/', include('math_api.urls')),
    path('api/user/', include('users.urls', namespace='users')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # API themes view
    # soon
]


urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)








# from django.contrib import admin
# from django.urls import path, include
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

# # API schemas
# from rest_framework.schemas import get_schema_view   # openapi
# from rest_framework.documentation import include_docs_urls  # coreapi
# from rest_framework_swagger.views import get_swagger_view
# schema_view = get_swagger_view(title='BlogAPI')

# # (media & static) requirements
# from django.conf import settings
# from django.conf.urls.static import static



# urlpatterns = [
#     # tokens
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     # admin
#     path('admin/', admin.site.urls),
#     # API
#     path('', include('blog.urls')),
#     path('api/', include('blog_api.urls')),
#     path('api/user/', include('users.urls', namespace='users')),
#     path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
#     # API themes view
#     path('docs/', include_docs_urls(title='BlogAPI')),
#     path('swagger/', get_swagger_view(title='BlogAPI')),
#     path('schema/', get_schema_view(
#         title="BlogAPI",
#         description="API for the BlogAPI",
#         version='1.0.0'    
#     ), name='openapi-schema'),
# ]

# urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
