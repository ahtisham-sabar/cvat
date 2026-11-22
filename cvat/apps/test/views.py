from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvat.apps.engine.models import JobType, LabeledImage, LabeledShape, LabeledTrack, Task
from cvat.apps.engine.permissions import TaskPermission


def _count_by_label(queryset, *fields):
    return queryset.order_by().values_list("label_id", *fields).annotate(count=Count("id"))


def count_annotations_per_label(task_id: int) -> dict[int, dict[str, int]]:
    """Counts annotations per label and type in the database, one GROUP BY query per model.

    Shapes are split by shape type (polygon, rectangle, mask, ...); tracks and tags are
    reported as "track" and "tag". Only annotation jobs are counted: ground truth and
    consensus replica jobs repeat frames that already belong to annotation jobs. Skeleton
    points (parent is set) are part of their skeleton and are not counted separately.
    """
    in_task = {"job__segment__task_id": task_id, "job__type": JobType.ANNOTATION}
    counts: dict[int, dict[str, int]] = {}

    def add(label_id: int, annotation_type: str, count: int) -> None:
        by_type = counts.setdefault(label_id, {})
        by_type[annotation_type] = by_type.get(annotation_type, 0) + count

    shapes = LabeledShape.objects.filter(**in_task, parent__isnull=True)
    for label_id, shape_type, count in _count_by_label(shapes, "type"):
        add(label_id, shape_type, count)

    tracks = LabeledTrack.objects.filter(**in_task, parent__isnull=True)
    for label_id, count in _count_by_label(tracks):
        add(label_id, "track", count)

    for label_id, count in _count_by_label(LabeledImage.objects.filter(**in_task)):
        add(label_id, "tag", count)

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
        labels = []
        for label in task.get_labels():
            by_type = counts.get(label.id, {})
            labels.append(
                {
                    "id": label.id,
                    "name": label.name,
                    "count": sum(by_type.values()),
                    "by_type": by_type,
                }
            )
        labels.sort(key=lambda label: (-label["count"], label["name"]))

        return Response(
            {
                "task_id": task.id,
                "total": sum(label["count"] for label in labels),
                "types": sorted({t for label in labels for t in label["by_type"]}),
                "labels": labels,
            }
        )
