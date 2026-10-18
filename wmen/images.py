import io
import logging
from pathlib import PurePosixPath

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

from .models import Women

logger = logging.getLogger(__name__)

MAX_SIDE = 1920
QUALITY = 85
Image.MAX_IMAGE_PIXELS = 40_000_000


def process_photo(*, woman_id: int) -> None:
    woman = Women.objects.filter(pk=woman_id).first()
    if woman is None or not woman.photo_raw:
        return

    raw_name = woman.photo_raw.name
    with woman.photo_raw.open("rb") as source:
        raw = source.read()

    try:
        processed = _render(io.BytesIO(raw))
    except (OSError, Image.DecompressionBombError) as error:
        logger.warning("Фото записи #%s не обработано, файл отброшен: %s", woman_id, error)
        Women.objects.filter(pk=woman_id, photo_raw=raw_name).update(photo_raw=None)
        Women.photo_raw.field.storage.delete(raw_name)
        return

    woman.refresh_from_db(fields=["photo_raw"])
    if woman.photo_raw.name != raw_name:
        logger.info("Фото записи #%s сменилось во время обработки, результат отброшен", woman_id)
        return

    old_photo = woman.photo.name if woman.photo else None
    woman.photo.save(f"{PurePosixPath(raw_name).stem}.webp", ContentFile(processed), save=False)
    woman.photo_raw = None
    woman.save(update_fields=["photo", "photo_raw"])

    Women.photo_raw.field.storage.delete(raw_name)
    if old_photo:
        Women.photo.field.storage.delete(old_photo)


def _render(source) -> bytes:
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image.thumbnail((MAX_SIDE, MAX_SIDE))
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=QUALITY)
    return buffer.getvalue()
