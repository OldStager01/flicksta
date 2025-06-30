from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    bucket_name = 'flicksta-aws-bucket'
    file_overwrite = False
    
class StaticStorage(S3Boto3Storage):
    bucket_name = 'flicksta-aws-bucket'
    location = 'static'
    
# Per-field Storage Instances for use in models

class AvatarStorage(MediaStorage):
    location = 'avatars'

class IconStorage(MediaStorage):
    location = 'icons'


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