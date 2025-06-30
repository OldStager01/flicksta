import os
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

def validate_file_size(file):
    file_size = file.size
    file_extension = os.path.splitext(file.name)[1].lower()
    
    # Check file extension and apply appropriate size limit
    if file_extension in settings.ALLOWED_IMAGE_EXTENSIONS:
        max_size = settings.MAX_IMAGE_SIZE
        file_type = "image"
    else:
        raise ValidationError('File type not allowed.')
    
    if file_size > max_size:
        raise ValidationError('File size too large. Maximum allowed size for %(file_type)s is %(max_size)s MB.') % {
                'file_type': file_type,
                'max_size': max_size / (1024 * 1024)
            }
        

def validate_file_extension(file):
    file_extension = os.path.splitext(file.name)[1].lower()
    allowed_extensions = (settings.ALLOWED_IMAGE_EXTENSIONS)
    
    if file_extension not in allowed_extensions:
        raise ValidationError(
            _('File extension "%(extension)s" is not allowed. Allowed extensions are: %(allowed)s') % {
                'extension': file_extension,
                'allowed': ', '.join(allowed_extensions)
            }
        )