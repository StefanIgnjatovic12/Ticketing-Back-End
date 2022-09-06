import magic
from django.core.exceptions import ValidationError
import os

def validate_file_type(file):
    valid_mime_types = ['application/pdf', 'text/plain', 'application/msword']
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Unsupported file type.')
    valid_file_extensions = ['.pdf', '.txt', '.doc', '.docx']
    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_file_extensions:
        raise ValidationError('Unacceptable file extension.')