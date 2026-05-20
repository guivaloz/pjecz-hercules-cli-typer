"""
Google Cloud Storage utilities
"""

from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.cloud.storage import Blob

from pjecz_hercules_cli_typer.utils.safe_string import safe_string

EXTENSIONS_MEDIA_TYPES = {
    "doc": "application/msword",
    "docx": "application/msword",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "pdf": "application/pdf",
    "png": "image/png",
    "xml": "application/xml",
    "xls": "xapplication/vnd.ms-excel",
    "xlsx": "xapplication/vnd.ms-excel",
}

MONTHS_ES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]

GOOGLE_STORAGE_HOST = "https://storage.googleapis.com"


class BucketNotFoundError(Exception):
    """Custom exception for bucket not found"""

    pass


class CopyBlobError(Exception):
    """Custom exception for copy blob error"""

    pass


class FileNotAllowedError(Exception):
    """Custom exception for file not allowed"""

    pass


class FileNotFoundError(Exception):
    """Custom exception for file not found"""

    pass


class NotValidUrlError(Exception):
    """Custom exception for not valid URL"""

    pass


class UploadFileError(Exception):
    """Custom exception for upload file error"""

    pass


def get_media_type_from_filename(filename: str) -> str:
    """
    Get media type from filename

    :param filename: Name of file
    :return: Media type
    """

    # Get extension
    extension = Path(filename).suffix[1:].lower()

    # Get media type
    try:
        media_type = EXTENSIONS_MEDIA_TYPES[extension]
    except KeyError as error:
        raise FileNotAllowedError("Tipo de archivo no permitido") from error

    # Return media type
    return media_type


def private_blob_name(bucket_name: str, base: str, fecha: date, filename: str, extension: str) -> str:
    """
    Get blob name from filename

    :return: Blob name
    """

    # Get the year in 20NN format
    year_str = fecha.strftime("%Y")

    # Get the month in two digits format
    month_str = fecha.strftime("%m")

    # Get the day in two digits format
    day_str = fecha.strftime("%d")

    # Always the extension in lower case
    extension = extension.lower()

    # Base is optional
    path_str = f"{year_str}/{month_str}/{day_str}/{filename}.{extension}"
    if base != "":
        path_str = f"{base}/{path_str}"

    # Return base, year, month, day and filename separated by slashes
    return f"{GOOGLE_STORAGE_HOST}/{bucket_name}/{path_str}"


def public_blob_name(
    bucket_name: str,
    base: str,
    distrito_clave: str,
    autoridad_clave: str,
    fecha: date,
    descripcion: str,
    hashed_id: str,
    extension: str,
) -> str:
    """
    Get blob name from filename

    :return: Blob name
    """

    # Get date in ISO format
    date_str = fecha.isoformat()

    # Get the year in 20NN format
    year_str = fecha.strftime("%Y")

    # Get the month in word format
    month_str = MONTHS_ES[fecha.month - 1]

    # Get the description as safe string, if it is empty, set it to "SIN_DESCRIPCION"
    descripcion = safe_string(descripcion, max_len=64, separator="-")
    if descripcion == "":
        descripcion = "sin-descripcion"

    # Get the filename as date in ISO, descrption and hashed_id separated by underscores
    filename = f"{date_str}-{descripcion}-{hashed_id}"

    # Always the extension in lower case
    extension = extension.lower()

    # Base is optional
    path_str = f"{distrito_clave}/{autoridad_clave}/{year_str}/{month_str}/{filename}.{extension}"
    if base != "":
        path_str = f"{base}/{path_str}"

    # Return base, year, month, day and filename separated by slashes
    return f"{GOOGLE_STORAGE_HOST}/{bucket_name}/{path_str}"


def get_blob_name_from_url(url: str) -> str:
    """
    Get blob name from URL

    :param url: URL of the file
    :return: Blob name
    """

    # Parse URL
    parsed_url = urlparse(url)

    # Get blob name
    try:
        blob_name_complete = parsed_url.path[1:]  # Extract the path and remove the first slash
        blob_name = "/".join(
            blob_name_complete.split("/")[1:]
        )  # Remove the first directory from the path, because it is the bucket name
    except IndexError as error:
        raise NotValidUrlError("URL no válida") from error

    # Return blob name unquoted
    return unquote(blob_name)


def check_file_exists_from_gcs(bucket_name: str, blob_name: str) -> bool:
    """
    Check if file exists in Google Cloud Storage

    :param bucket_name: Name of the bucket
    :param blob_name: Path to the file
    :return: True if file exists
    """

    # Get bucket
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except NotFound as error:
        raise BucketNotFoundError("Bucket no encontrado") from error

    # Get file
    blob = bucket.get_blob(blob_name)
    if blob is None:
        return False

    # Return True if file exists
    return True


def get_public_url_from_gcs(bucket_name: str, blob_name: str) -> str:
    """
    Get public URL from Google Cloud Storage

    :param bucket_name: Name of the bucket
    :param blob_name: Path to the file
    :return: Public URL
    """

    # Get bucket
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except NotFound as error:
        raise BucketNotFoundError("Bucket no encontrado") from error

    # Get file
    blob = bucket.get_blob(blob_name)
    if blob is None:
        raise FileNotFoundError("Archivo no encontrado")

    # Return public URL
    return blob.public_url


def get_file_from_gcs(bucket_name: str, blob_name: str) -> bytes:
    """
    Get file from Google Cloud Storage

    :param bucket_name: Name of the bucket
    :param blob_name: Path to the file
    :return: File content
    """

    # Get bucket
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except NotFound as error:
        raise BucketNotFoundError("Bucket no encontrado") from error

    # Get file
    blob = bucket.get_blob(blob_name)
    if blob is None:
        raise FileNotFoundError("Archivo no encontrado")

    # Return file content
    return blob.download_as_bytes()


def upload_file_to_gcs(bucket_name: str, blob_name: str, content_type: str, data: bytes) -> str:
    """
    Upload file to Google Cloud Storage

    :param bucket_name: Name of the bucket
    :param blob_name: Path to the file
    :param content_type: Content type of the file
    :param data: File content
    :return: Public URL
    """

    # Get bucket
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except NotFound as error:
        raise BucketNotFoundError("Bucket no encontrado") from error

    # Create blob
    blob = bucket.blob(blob_name)

    # Upload file
    try:
        blob.upload_from_string(data, content_type=content_type)
    except Exception as error:
        raise UploadFileError("Error al subir el archivo") from error

    # Return public URL
    return blob.public_url


def update_blob_name_in_gcs(bucket_name: str, old_blob_name: str, new_blob_name: str) -> str:
    """
    Update (rename/move) a blob in Google Cloud Storage

    This function copies the blob to a new location and deletes the old one,
    which is the standard approach for renaming in GCS.

    :param bucket_name: Name of the bucket
    :param old_blob_name: Current path/name of the file
    :param new_blob_name: New path/name for the file
    :return: Public URL of the new blob
    """

    # Get bucket
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except NotFound as error:
        raise BucketNotFoundError("Bucket no encontrado") from error

    # Get the old blob
    old_blob = bucket.get_blob(old_blob_name)
    if old_blob is None:
        raise FileNotFoundError(f"Archivo no encontrado: {old_blob_name}")

    # Copy to new blob name
    try:
        new_blob = bucket.copy_blob(old_blob, bucket, new_blob_name)
    except Exception as error:
        raise CopyBlobError(f"Error al copiar el archivo a {new_blob_name}") from error

    # Delete the old blob
    try:
        old_blob.delete()
    except Exception as error:
        # If deletion fails, we should clean up the new blob
        try:
            new_blob.delete()
        except Exception:
            pass
        raise CopyBlobError(f"Error al eliminar el archivo antiguo: {old_blob_name}") from error

    # Return public URL of the new blob
    return new_blob.public_url


def get_blobs_from_gcs(bucket_name: str, prefix: str) -> list[Blob]:
    """
    Get list of blob names from Google Cloud Storage with a given prefix

    :param bucket_name: Name of the bucket
    :param prefix: Prefix to filter blobs
    :return: List of blob names
    """

    # Get bucket
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except NotFound as error:
        raise BucketNotFoundError("Bucket no encontrado") from error

    # List blobs with the given prefix
    blobs = bucket.list_blobs(prefix=prefix)

    # Return list of blobs
    return [blob for blob in blobs]
