from uuid import uuid4
from fastapi import UploadFile
from app.firebase.firebase import bucket


def upload_file(file: UploadFile):
    file_ext = file.filename.split(".")[-1]
    unique_name = f"{uuid4()}.{file_ext}"

    blob = bucket.blob(unique_name)

    blob.upload_from_file(file.file, content_type=file.content_type)

    # make public (for demo simplicity)
    blob.make_public()

    return blob.public_url