from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
from django.core.exceptions import ValidationError
import os

def _s3_validate_and_save(self, name, content):
# Validate file size before uploading to S3
    file_size = getattr(content, 'size', None) or getattr(content.file, 'size', None)
    if file_size and file_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError(f'File too large. Maximum size is {settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024*1024):.1f}MB.')
    
    # Validate file extension
    file_extension = os.path.splitext(name)[1].lower()
    allowed_extensions = (settings.ALLOWED_IMAGE_EXTENSIONS)
    
    if file_extension not in allowed_extensions:
        raise ValidationError(f'File extension "{file_extension}" is not allowed.')


class MediaStorage(S3Boto3Storage):
    bucket_name = 'flicksta-aws-bucket'
    file_overwrite = False
    
    def _save(self, name, content):
        try:
            _s3_validate_and_save(self, name, content)
            return super()._save(name, content)
        except ValidationError as e:
            raise ValidationError(f'Error saving file: {str(e)}') 
        except Exception as e:
            raise ValidationError(f'An unexpected error occurred while saving the file: {str(e)}')
        
        
class StaticStorage(S3Boto3Storage):
    bucket_name = 'flicksta-aws-bucket'
    location = 'static'
    
    def _save(self, name, content):
        try:
            _s3_validate_and_save(self, name, content)
            return super()._save(name, content)
        except ValidationError as e:
            raise ValidationError(f'Error saving file: {str(e)}') 
        except Exception as e:
            raise ValidationError(f'An unexpected error occurred while saving the file: {str(e)}')

    
# Per-field Storage Instances for use in models

class AvatarStorage(MediaStorage):
    location = 'media/avatars'

class IconStorage(MediaStorage):
    location = 'media/icons'


if settings.ENVIRONMENT == 'production':
    if settings.STORAGE_SERVICE == 'cloudinary':
        from cloudinary_storage.storage import MediaCloudinaryStorage

        avatar_storage = MediaCloudinaryStorage()
        icon_storage = MediaCloudinaryStorage(resource_type='image')  # icons and svgs fall under image

    elif settings.STORAGE_SERVICE == 'aws':
        avatar_storage = AvatarStorage()
        icon_storage = IconStorage()
    else:
        from django.core.files.storage import FileSystemStorage

        avatar_storage = FileSystemStorage(location=settings.MEDIA_ROOT / 'avatars')
        icon_storage = FileSystemStorage(location=settings.MEDIA_ROOT / 'icons')

else:
    from django.core.files.storage import FileSystemStorage

    avatar_storage = FileSystemStorage(location=settings.MEDIA_ROOT / 'avatars')
    icon_storage = FileSystemStorage(location=settings.MEDIA_ROOT / 'icons')