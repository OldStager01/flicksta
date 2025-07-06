import os
import tempfile
import requests
import boto3
import cloudinary.uploader
import cloudinary.api

from urllib.parse import urlparse
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.conf import settings

from f_users.models import Profile
from f_posts.models import Tag
from flicksta.storages import icon_storage_location, avatar_storage_location


class Command(BaseCommand):
    help = "Migrate media files between AWS S3 and Cloudinary"

    def handle(self, *args, **kwargs):
        self.stdout.write("Choose migration direction:")
        self.stdout.write("1. S3 to Cloudinary")
        self.stdout.write("2. Cloudinary to S3")

        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            self.stdout.write("🔁 Starting migration from S3 to Cloudinary...")
            self.migrate_s3_to_cloudinary()
        elif choice == "2":
            self.stdout.write("🔁 Starting migration from Cloudinary to S3...")
            self.migrate_cloudinary_to_s3()
        else:
            self.stderr.write("❌ Invalid choice. Exiting.")
            return

    def is_s3_url(self, url):
        """Check if URL is from S3"""
        return 's3.amazonaws.com' in url or 'amazonaws.com' in url

    def is_cloudinary_url(self, url):
        """Check if URL is from Cloudinary"""
        return 'cloudinary.com' in url

    def get_s3_key_from_url(self, url):
        """Extract S3 key from URL"""
        parsed = urlparse(url)
        # Remove leading slash
        return parsed.path.lstrip('/')

    def check_s3_object_exists(self, s3_client, bucket, key):
        """Check if S3 object exists"""
        try:
            s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def migrate_s3_to_cloudinary(self):
        """Migrate files from S3 to Cloudinary without deleting from S3"""
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=getattr(settings, "AWS_S3_REGION_NAME", "ap-south-1")
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        # First, let's list what's actually in the S3 bucket
        self.stdout.write("🔍 Checking S3 bucket contents...")
        try:
            response = s3.list_objects_v2(Bucket=bucket, MaxKeys=10)
            if 'Contents' in response:
                self.stdout.write(f"📁 Found {len(response['Contents'])} objects in bucket. Sample objects:")
                for obj in response['Contents'][:5]:
                    self.stdout.write(f"   - {obj['Key']}")
            else:
                self.stdout.write("📁 Bucket appears to be empty")
        except Exception as e:
            self.stderr.write(f"❌ Error listing bucket contents: {e}")

        # --- Migrate Tags ---
        self.stdout.write("📋 Migrating Tags...")
        tag_count = 0
        for tag in Tag.objects.exclude(image=''):
            if not tag.image:
                continue

            try:
                # Debug: Show current image info
                self.stdout.write(f"🔍 Tag '{tag.name}': image.name='{tag.image.name}'")
                
                # Try to get the URL to see what storage is being used
                try:
                    current_url = tag.image.url
                    self.stdout.write(f"   URL: {current_url}")
                    
                    # Skip if already on Cloudinary
                    if self.is_cloudinary_url(current_url):
                        self.stdout.write(f"⏭️ Tag '{tag.name}' already on Cloudinary")
                        continue
                        
                except Exception as url_error:
                    self.stdout.write(f"   ⚠️  Cannot get URL: {url_error}")
                    continue

                # Try different possible S3 key formats
                possible_keys = [
                    f"{icon_storage_location}{os.path.basename(tag.image.name)}",  # With media/icons prefix
                ]
                
                # If URL is available, try extracting key from it
                if hasattr(tag.image, 'url'):
                    try:
                        url_key = self.get_s3_key_from_url(tag.image.url)
                        possible_keys.insert(0, url_key)
                    except:
                        pass

                found_key = None
                for key in possible_keys:
                    if key and self.check_s3_object_exists(s3, bucket, key):
                        found_key = key
                        self.stdout.write(f"   ✅ Found S3 object at: {key}")
                        break
                    else:
                        self.stdout.write(f"   ❌ Not found at: {key}")

                if not found_key:
                    self.stderr.write(f"❌ No S3 object found for Tag '{tag.name}' - skipping")
                    continue

                # Download and upload to Cloudinary
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    try:
                        s3.download_file(bucket, found_key, tmp.name)
                        
                        # Get original filename
                        original_filename = os.path.basename(tag.image.name)
                        filename_without_ext = os.path.splitext(original_filename)[0]
                        
                        # Upload directly to Cloudinary with correct folder structure
                        upload_result = cloudinary.uploader.upload(
                            tmp.name,
                            folder=icon_storage_location.rstrip('/'),  # Remove trailing slash
                            public_id=filename_without_ext,  # Use original filename without extension
                            resource_type="auto",
                            use_filename=True,
                            unique_filename=False,
                            overwrite=True
                        )
                        
                        self.stdout.write(f"📤 Upload Result: {upload_result}")  # Debugging line
                        
                        # FIXED: Set the image field name to match the Cloudinary public_id
                        # This preserves the folder structure in the database
                        public_id = upload_result['public_id']
                        file_format = upload_result['format']
                        
                        # The public_id already includes the folder path (e.g., "media/icons/filename")
                        # So we use it directly with the file extension
                        cloudinary_filename = f"{public_id}.{file_format}"
                        
                        # Set the field name directly - this preserves the Cloudinary structure
                        tag.image.name = cloudinary_filename
                        
                        # Save the model
                        tag.save()
                        
                        tag_count += 1
                        cloudinary_url = upload_result['secure_url']
                        self.stdout.write(f"✅ Tag '{tag.name}' migrated to Cloudinary: {cloudinary_url}")
                        self.stdout.write(f"   New image.name: {tag.image.name}")
                        
                    except Exception as e:
                        self.stderr.write(f"❌ Failed to migrate Tag '{tag.name}': {e}")
                    finally:
                        if os.path.exists(tmp.name):
                            os.unlink(tmp.name)
                            
            except Exception as e:
                self.stderr.write(f"❌ Error processing Tag '{tag.name}': {e}")

        # --- Migrate Profiles ---
        self.stdout.write("👤 Migrating Profiles...")
        profile_count = 0
        for profile in Profile.objects.exclude(image=''):
            if not profile.image:
                continue

            try:
                # Debug: Show current image info
                self.stdout.write(f"🔍 Profile '{profile.user.username}': image.name='{profile.image.name}'")
                
                # Try to get the URL to see what storage is being used
                try:
                    current_url = profile.image.url
                    self.stdout.write(f"   URL: {current_url}")
                    
                    # Skip if already on Cloudinary
                    if self.is_cloudinary_url(current_url):
                        self.stdout.write(f"⏭️ Profile '{profile.user.username}' already on Cloudinary")
                        continue
                        
                except Exception as url_error:
                    self.stdout.write(f"   ⚠️  Cannot get URL: {url_error}")
                    continue

                # Try different possible S3 key formats
                possible_keys = [
                    f"{avatar_storage_location}{os.path.basename(profile.image.name)}",  # With media/avatars prefix
                ]
                
                # If URL is available, try extracting key from it
                if hasattr(profile.image, 'url'):
                    try:
                        url_key = self.get_s3_key_from_url(profile.image.url)
                        possible_keys.insert(0, url_key)
                    except:
                        pass

                found_key = None
                for key in possible_keys:
                    if key and self.check_s3_object_exists(s3, bucket, key):
                        found_key = key
                        self.stdout.write(f"   ✅ Found S3 object at: {key}")
                        break
                    else:
                        self.stdout.write(f"   ❌ Not found at: {key}")

                if not found_key:
                    self.stderr.write(f"❌ No S3 object found for Profile '{profile.user.username}' - skipping")
                    continue

                # Download and upload to Cloudinary
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    try:
                        s3.download_file(bucket, found_key, tmp.name)
                        
                        # Get original filename
                        original_filename = os.path.basename(profile.image.name)
                        filename_without_ext = os.path.splitext(original_filename)[0]
                        
                        # Upload directly to Cloudinary with correct folder structure
                        upload_result = cloudinary.uploader.upload(
                            tmp.name,
                            folder=avatar_storage_location.rstrip('/'),  # Remove trailing slash
                            public_id=filename_without_ext,  # Use original filename without extension
                            resource_type="auto",
                            use_filename=True,
                            unique_filename=False,
                            overwrite=True
                        )
                        
                        self.stdout.write(f"📤 Upload Result: {upload_result}")  # Debugging line
                        
                        # FIXED: Set the image field name to match the Cloudinary public_id
                        # This preserves the folder structure in the database
                        public_id = upload_result['public_id']
                        file_format = upload_result['format']
                        
                        # The public_id already includes the folder path (e.g., "media/avatars/filename")
                        # So we use it directly with the file extension
                        cloudinary_filename = f"{public_id}.{file_format}"
                        
                        # Set the field name directly - this preserves the Cloudinary structure
                        profile.image.name = cloudinary_filename
                        
                        # Save the model
                        profile.save()
                        
                        profile_count += 1
                        cloudinary_url = upload_result['secure_url']
                        self.stdout.write(f"✅ Profile '{profile.user.username}' migrated to Cloudinary: {cloudinary_url}")
                        self.stdout.write(f"   New image.name: {profile.image.name}")
                        
                    except Exception as e:
                        self.stderr.write(f"❌ Failed to migrate Profile '{profile.user.username}': {e}")
                    finally:
                        if os.path.exists(tmp.name):
                            os.unlink(tmp.name)
                            
            except Exception as e:
                self.stderr.write(f"❌ Error processing Profile '{profile.user.username}': {e}")

        self.stdout.write(f"🎉 Migration complete! Tags: {tag_count}, Profiles: {profile_count}")

    def migrate_cloudinary_to_s3(self):
        """Migrate files from Cloudinary to S3 without deleting from Cloudinary"""
        
        # Initialize S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=getattr(settings, "AWS_S3_REGION_NAME", "ap-south-1")
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        
        # --- Migrate Tags ---
        self.stdout.write("📋 Migrating Tags...")
        tag_count = 0
        for tag in Tag.objects.exclude(image=''):
            if not tag.image or not hasattr(tag.image, 'url'):
                continue

            try:
                current_url = tag.image.url
                
                # Skip if already on S3
                if self.is_s3_url(current_url):
                    self.stdout.write(f"⏭️ Tag '{tag.name}' already on S3")
                    continue

                # Only migrate if it's currently on Cloudinary
                if not self.is_cloudinary_url(current_url):
                    self.stdout.write(f"⏭️ Tag '{tag.name}' not on Cloudinary, skipping")
                    continue

                self.stdout.write(f"🔄 Migrating Tag '{tag.name}' from Cloudinary to S3...")
                self.stdout.write(f"   Current URL: {current_url}")

                # Download from Cloudinary
                response = requests.get(current_url, timeout=30)
                response.raise_for_status()
                
                if response.status_code == 200:
                    # Generate proper filename and S3 key
                    original_filename = os.path.basename(urlparse(current_url).path)
                    if not original_filename or '.' not in original_filename:
                        # Extract extension from content-type if possible
                        content_type = response.headers.get('content-type', '')
                        if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                            ext = '.jpg'
                        elif 'image/png' in content_type:
                            ext = '.png'
                        elif 'image/gif' in content_type:
                            ext = '.gif'
                        elif 'image/webp' in content_type:
                            ext = '.webp'
                        else:
                            ext = '.jpg'  # default
                        original_filename = f"tag_{tag.id}_{tag.slug}{ext}"
                    
                    # Construct S3 key with proper path
                    s3_key = f"{icon_storage_location}{original_filename}"
                    
                    # Upload directly to S3 (REMOVED ACL to fix the error)
                    with tempfile.NamedTemporaryFile() as tmp_file:
                        tmp_file.write(response.content)
                        tmp_file.flush()
                        
                        # Upload to S3 without ACL
                        s3.upload_file(
                            tmp_file.name,
                            bucket,
                            s3_key,
                            ExtraArgs={
                                'ContentType': response.headers.get('content-type', 'image/jpeg')
                                # Removed ACL parameter
                            }
                        )
                    
                    # Verify upload
                    if self.check_s3_object_exists(s3, bucket, s3_key):
                        # Update model with new S3 path
                        tag.image.name = s3_key
                        tag.save()
                        
                        tag_count += 1
                        self.stdout.write(f"✅ Tag '{tag.name}' migrated to S3: s3://{bucket}/{s3_key}")
                    else:
                        raise Exception("File verification failed - object not found in S3")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.stderr.write(f"❌ Error processing Tag '{tag.name}': {e}")

        # --- Migrate Profiles ---
        self.stdout.write("👤 Migrating Profiles...")
        profile_count = 0
        for profile in Profile.objects.exclude(image=''):
            if not profile.image or not hasattr(profile.image, 'url'):
                continue

            try:
                current_url = profile.image.url
                
                # Skip if already on S3
                if self.is_s3_url(current_url):
                    self.stdout.write(f"⏭️ Profile '{profile.user.username}' already on S3")
                    continue

                # Only migrate if it's currently on Cloudinary
                if not self.is_cloudinary_url(current_url):
                    self.stdout.write(f"⏭️ Profile '{profile.user.username}' not on Cloudinary, skipping")
                    continue

                self.stdout.write(f"🔄 Migrating Profile '{profile.user.username}' from Cloudinary to S3...")
                self.stdout.write(f"   Current URL: {current_url}")
                
                # FIX: Clean up duplicate path segments in Cloudinary URLs
                # Remove duplicate avatars/ in the path
                if '/avatars/avatars/' in current_url:
                    current_url = current_url.replace('/avatars/avatars/', '/avatars/')
                    self.stdout.write(f"   Fixed URL: {current_url}")

                # Download from Cloudinary
                response = requests.get(current_url, timeout=30)
                response.raise_for_status()
                
                if response.status_code == 200:
                    # Generate proper filename and S3 key
                    original_filename = os.path.basename(urlparse(current_url).path)
                    if not original_filename or '.' not in original_filename:
                        # Extract extension from content-type if possible
                        content_type = response.headers.get('content-type', '')
                        if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                            ext = '.jpg'
                        elif 'image/png' in content_type:
                            ext = '.png'
                        elif 'image/gif' in content_type:
                            ext = '.gif'
                        elif 'image/webp' in content_type:
                            ext = '.webp'
                        else:
                            ext = '.jpg'  # default
                        original_filename = f"profile_{profile.user.id}_{profile.user.username}{ext}"
                    
                    # Construct S3 key with proper path
                    s3_key = f"{avatar_storage_location}{original_filename}"
                    
                    # Upload directly to S3 (REMOVED ACL to fix the error)
                    with tempfile.NamedTemporaryFile() as tmp_file:
                        tmp_file.write(response.content)
                        tmp_file.flush()
                        
                        # Upload to S3 without ACL
                        s3.upload_file(
                            tmp_file.name,
                            bucket,
                            s3_key,
                            ExtraArgs={
                                'ContentType': response.headers.get('content-type', 'image/jpeg')
                                # Removed ACL parameter
                            }
                        )
                    
                    # Verify upload
                    if self.check_s3_object_exists(s3, bucket, s3_key):
                        # Update model with new S3 path
                        profile.image.name = s3_key
                        profile.save()
                        
                        profile_count += 1
                        self.stdout.write(f"✅ Profile '{profile.user.username}' migrated to S3: s3://{bucket}/{s3_key}")
                    else:
                        raise Exception("File verification failed - object not found in S3")
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.stderr.write(f"❌ Error processing Profile '{profile.user.username}': {e}")

        self.stdout.write(f"🎉 Migration complete! Tags: {tag_count}, Profiles: {profile_count}")
