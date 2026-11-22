from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvat.apps.engine.models import JobType, LabeledImage, LabeledShape, LabeledTrack, Task
from cvat.apps.engine.permissions import TaskPermission


def count_annotations_per_label(task_id: int) -> dict[int, int]:
    """Counts shapes, tracks and tags per label in the database, one GROUP BY query each.

    Only annotation jobs are counted: ground truth and consensus replica jobs repeat
    frames that already belong to annotation jobs. Skeleton points (parent is set)
    are part of their skeleton and are not counted separately.
    """
    in_task = {"job__segment__task_id": task_id, "job__type": JobType.ANNOTATION}
    querysets = [
        LabeledShape.objects.filter(**in_task, parent__isnull=True),
        LabeledTrack.objects.filter(**in_task, parent__isnull=True),
        LabeledImage.objects.filter(**in_task),
    ]

    counts: dict[int, int] = {}
    for queryset in querysets:
        rows = queryset.order_by().values_list("label_id").annotate(count=Count("id"))
        for label_id, count in rows:
            counts[label_id] = counts.get(label_id, 0) + count
    return counts


class TaskAnnotationCountsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id: int):
        task = get_object_or_404(Task, pk=task_id)

        permission = TaskPermission.create_base_perm(
            request, self, TaskPermission.Scopes.VIEW_ANNOTATIONS, iam_context=None, obj=task
        )
        if not permission.check_access().allow:
            raise PermissionDenied()

        counts = count_annotations_per_label(task.id)
        labels = [
            {"id": label.id, "name": label.name, "count": counts.get(label.id, 0)}
            for label in task.get_labels()
        ]
        labels.sort(key=lambda label: (-label["count"], label["name"]))

        return Response(
            {
                "task_id": task.id,
                "total": sum(label["count"] for label in labels),
                "labels": labels,
            }
        )
