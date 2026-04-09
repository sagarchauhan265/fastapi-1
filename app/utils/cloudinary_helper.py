import re
import logging
import cloudinary
import cloudinary.uploader
from app.config.settings import settings

logger = logging.getLogger(__name__)

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def upload_image(file_bytes: bytes, folder: str = "products") -> str:
    result = cloudinary.uploader.upload(file_bytes, folder=folder)
    return result["secure_url"]


def delete_image(image_url: str) -> None:
    """Extract public_id from Cloudinary URL and delete the image."""
    # URL format: https://res.cloudinary.com/<cloud>/image/upload/v<version>/<folder>/<name>.<ext>
    match = re.search(r'/upload/(?:v\d+/)?(.+)', image_url)
    if not match:
        return
    public_id = match.group(1).rsplit(".", 1)[0]  # strip file extension
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        logger.warning("Failed to delete Cloudinary image '%s': %s", public_id, e)