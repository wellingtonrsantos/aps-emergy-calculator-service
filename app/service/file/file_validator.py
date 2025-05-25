ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def validate_file_mime(file) -> bool:
    return file.content_type in ALLOWED_MIME_TYPES
