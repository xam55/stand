import csv
import io
import logging
import tempfile

from django.core.files import File
from django.utils import timezone

from .models import Report, Women

logger = logging.getLogger(__name__)

CHUNK_SIZE = 2000
COLUMNS = ("id", "title", "category", "is_published", "time_create")


def build_report(*, report_id: int) -> None:
    started = Report.objects.filter(pk=report_id, status__in=Report.ACTIVE_STATUSES).update(
        status=Report.Status.RUNNING
    )
    if not started:
        return

    report = Report.objects.get(pk=report_id)
    with tempfile.TemporaryFile() as tmp:
        rows = _write_women_csv(tmp)
        tmp.seek(0)
        report.file.save(f"women-{report.pk}.csv", File(tmp), save=False)

    report.status = Report.Status.DONE
    report.rows = rows
    report.finished_at = timezone.now()
    report.save(update_fields=["file", "status", "rows", "finished_at"])
    logger.info("Отчёт #%s готов: %s строк", report_id, rows)


def mark_report_failed(*, report_id: int, error: Exception) -> None:
    logger.error("Отчёт #%s не собран: %s", report_id, error)
    Report.objects.filter(pk=report_id).update(
        status=Report.Status.FAILED,
        error=str(error),
        finished_at=timezone.now(),
    )


def _write_women_csv(binary_file) -> int:
    text = io.TextIOWrapper(binary_file, encoding="utf-8-sig", newline="")
    writer = csv.writer(text, delimiter=";")
    writer.writerow(COLUMNS)

    rows = 0
    women = Women.objects.order_by("pk").values_list(
        "pk", "title", "cat__name", "is_published", "time_create"
    )
    for row in women.iterator(chunk_size=CHUNK_SIZE):
        writer.writerow(row)
        rows += 1

    text.flush()
    text.detach()
    return rows
