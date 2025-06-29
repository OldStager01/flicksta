# Generated by Django 5.2.3 on 2025-06-29 12:33

import cloudinary.models
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "image",
                    cloudinary.models.CloudinaryField(
                        blank=True, max_length=255, null=True, verbose_name="image"
                    ),
                ),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("order", models.IntegerField(blank=True, default=0, null=True)),
            ],
            options={
                "ordering": ["order", "name"],
            },
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="LikedComment",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="f_posts.comment",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("user", "comment")},
            },
        ),
        migrations.AddField(
            model_name="comment",
            name="likes",
            field=models.ManyToManyField(
                blank=True,
                related_name="liked_comments",
                through="f_posts.LikedComment",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="LikedPost",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="LikedReply",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("artist", models.CharField(blank=True, max_length=255, null=True)),
                ("url", models.URLField(blank=True, max_length=2000, null=True)),
                ("image", models.URLField(max_length=2000)),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="posts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "likes",
                    models.ManyToManyField(
                        blank=True,
                        related_name="likedposts",
                        through="f_posts.LikedPost",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        blank=True, related_name="posts", to="f_posts.tag"
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddField(
            model_name="likedpost",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="f_posts.post"
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="parent_post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="f_posts.post",
            ),
        ),
        migrations.CreateModel(
            name="Reply",
            fields=[
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.CharField(
                        default=uuid.uuid4,
                        editable=False,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="replies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "likes",
                    models.ManyToManyField(
                        blank=True,
                        related_name="liked_replies",
                        through="f_posts.LikedReply",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parent_comment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="f_posts.comment",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddField(
            model_name="likedreply",
            name="reply",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="f_posts.reply"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="likedpost",
            unique_together={("user", "post")},
        ),
        migrations.AlterUniqueTogether(
            name="likedreply",
            unique_together={("user", "reply")},
        ),
    ]
