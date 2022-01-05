from api.authentication.viewsets import (
    RegisterViewSet,
    LoginViewSet,
    ActiveSessionViewSet,
    LogoutViewSet,
)
from django.urls import path, include


from rest_framework import routers
from api.user.viewsets import RunAutoBalacer, UserViewSet, ApiKeyView, ApiKeyDetailView, AutoBalancerView, AutoBalancerDetail

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"edit", UserViewSet, basename="user-edit")

router.register(r"register", RegisterViewSet, basename="register")

router.register(r"login", LoginViewSet, basename="login")

router.register(r"checkSession", ActiveSessionViewSet, basename="check-session")

router.register(r"logout", LogoutViewSet, basename="logout")

urlpatterns = [
    path('apikeys', ApiKeyView.as_view()),
    path('apikey/<int:pk>', ApiKeyDetailView.as_view()),
    path('autobalancers', AutoBalancerView.as_view()),
    path('autobalancers/<int:pk>', AutoBalancerDetail.as_view()),
    path('run_autobalancer/<int:pk>', RunAutoBalacer.as_view()),
]

urlpatterns += router.urls