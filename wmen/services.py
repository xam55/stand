from django.core.paginator import Paginator
from django.db import IntegrityError, transaction

from .cache import get_or_set_women_page
from .models import Report, Women
from .tasks import build_women_report_task, generate_woman_report, process_photo_task

WOMEN_PAGE_SIZE = 20


def get_women_page(*, page: int) -> dict:
    return get_or_set_women_page(page, lambda: _build_women_page(page))


def _build_women_page(page: int) -> dict:
    paginator = Paginator(Women.objects.order_by("-time_create", "-pk"), WOMEN_PAGE_SIZE)
    page_obj = paginator.page(page)
    return {
        "count": paginator.count,
        "pages": paginator.num_pages,
        "page": page_obj.number,
        "results": list(page_obj.object_list),
    }


@transaction.atomic
def create_woman(*, data: dict) -> Women:
    data = dict(data)
    photo = data.pop("photo", None)
    woman = Women.objects.create(**data, photo_raw=photo)
    transaction.on_commit(lambda: generate_woman_report.delay(woman.pk))
    if photo:
        transaction.on_commit(lambda: process_photo_task.delay(woman.pk))
    return woman


@transaction.atomic
def update_woman(*, pk: int, data: dict) -> Women:
    data = dict(data)
    photo_sent = "photo" in data
    photo = data.pop("photo", None)

    woman = Women.objects.select_for_update().get(pk=pk)
    for field, value in data.items():
        setattr(woman, field, value)

    if photo_sent:
        _delete_files_on_commit(woman.photo_raw)
        woman.photo_raw = photo
        if photo is None:
            _delete_files_on_commit(woman.photo)
            woman.photo = None

    woman.save()
    if photo:
        transaction.on_commit(lambda: process_photo_task.delay(woman.pk))
    return woman


@transaction.atomic
def delete_woman(*, pk: int) -> None:
    woman = Women.objects.select_for_update().get(pk=pk)
    _delete_files_on_commit(woman.photo, woman.photo_raw)
    woman.delete()


def _delete_files_on_commit(*files) -> None:
    for file in files:
        if file:
            storage, name = file.storage, file.name
            transaction.on_commit(lambda storage=storage, name=name: storage.delete(name))


@transaction.atomic
def request_report(*, user) -> tuple[Report, bool]:
    active = Report.objects.filter(user=user, status__in=Report.ACTIVE_STATUSES).first()
    if active:
        return active, False

    try:
        with transaction.atomic():
            report = Report.objects.create(user=user)
    except IntegrityError:
        return Report.objects.get(user=user, status__in=Report.ACTIVE_STATUSES), False

    transaction.on_commit(lambda: build_women_report_task.delay(report.pk))
    return report, True


def get_user_report(*, user, pk: int) -> Report:
    return Report.objects.get(pk=pk, user=user)
