from django.urls import path

from .views import ActiveSessionListView, EntryView, ExitView

urlpatterns = [
    path("entry/", EntryView.as_view(), name="session-entry"),
    path("exit/", ExitView.as_view(), name="session-exit"),
    path("active/", ActiveSessionListView.as_view(), name="session-active-list"),
]