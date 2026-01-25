from django.urls import path
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView
# )

from . import views

urlpatterns = [
    # auth token
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/refresh/", TokenRefreshView.as_view(), name="refresh_token")

    path("login/", views.LoginApiView.as_view(), name="login"),
    path("token/refresh", views.RefreshTokenAPIView.as_view(), name="refresh_token"),

    # metrix service api's
    path("api/insert/item/<str:pid>", views.CreateSingleWorkItem.as_view(), name="single_item"),
    path("api/bulk/insert/<str:pid>", views.CreateBulkInsert.as_view(), name="bulk insert"),

    # transaction service APIs
    path("api/items/date-range", views.GetWorkItemByDateRange.as_view(), name="get-range"),

]

