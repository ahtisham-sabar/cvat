from django.urls import path

from .views import TaskAnnotationCountsView

urlpatterns = [
    path(
        "test/tasks/<int:task_id>/annotation-counts",
        TaskAnnotationCountsView.as_view(),
        name="test-task-annotation-counts",
    ),
]
