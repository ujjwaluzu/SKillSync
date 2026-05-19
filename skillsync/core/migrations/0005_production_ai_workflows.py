# Generated manually for the SkillSync production-level workflow upgrade.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0004_alter_bid_freelancer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="role",
            field=models.CharField(
                choices=[("client", "Client"), ("freelancer", "Freelancer")],
                default="freelancer",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="availability",
            field=models.CharField(
                choices=[("available", "Available"), ("busy", "Busy"), ("offline", "Offline")],
                default="available",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="bio",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="completed_projects",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="profile",
            name="full_name",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="profile",
            name="headline",
            field=models.CharField(blank=True, max_length=180),
        ),
        migrations.AddField(
            model_name="profile",
            name="hourly_rate",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="location",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="profile",
            name="portfolio_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="rating",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3),
        ),
        migrations.AddField(
            model_name="profile",
            name="skills",
            field=models.TextField(
                blank=True,
                help_text="Comma-separated skills, for example: Django, UI Design, Payments",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="total_reviews",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="project",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="projects",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="min_price",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="project",
            name="max_price",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="budget_justification",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="complexity",
            field=models.CharField(
                choices=[
                    ("basic", "Basic"),
                    ("intermediate", "Intermediate"),
                    ("advanced", "Advanced"),
                    ("expert", "Expert"),
                ],
                default="intermediate",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="confidence_score",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="estimated_days",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="estimated_price",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="estimated_time_label",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="project",
            name="skills",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[
                    ("open", "Open"),
                    ("in_review", "In Review"),
                    ("in_progress", "In Progress"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                ],
                default="open",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="tags",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="project",
            name="title",
            field=models.CharField(blank=True, default="", max_length=180),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="project",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="bid",
            name="amount",
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name="bid",
            name="freelancer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bids",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="bid",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bids",
                to="core.project",
            ),
        ),
        migrations.AddField(
            model_name="bid",
            name="cover_letter",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="bid",
            name="match_score",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="bid",
            name="proposed_days",
            field=models.PositiveIntegerField(default=7),
        ),
        migrations.AddField(
            model_name="bid",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("shortlisted", "Shortlisted"),
                    ("accepted", "Accepted"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="bid",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="project",
            name="accepted_bid",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="accepted_for_projects",
                to="core.bid",
            ),
        ),
        migrations.CreateModel(
            name="ProjectAIInsight",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("extracted_skills", models.JSONField(blank=True, default=list)),
                ("generated_tags", models.JSONField(blank=True, default=list)),
                ("feature_summary", models.JSONField(blank=True, default=dict)),
                ("similar_projects", models.JSONField(blank=True, default=list)),
                ("recommended_freelancers", models.JSONField(blank=True, default=list)),
                ("model_version", models.CharField(default="rf-tfidf-v2", max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_insight",
                        to="core.project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("message", models.TextField()),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("system", "System"),
                            ("project", "Project"),
                            ("bid", "Bid"),
                            ("message", "Message"),
                            ("review", "Review"),
                        ],
                        default="system",
                        max_length=20,
                    ),
                ),
                ("target_url", models.CharField(blank=True, max_length=240)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PortfolioItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                ("project_url", models.URLField(blank=True)),
                ("skills", models.CharField(blank=True, max_length=240)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portfolio_items",
                        to="core.profile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.PositiveSmallIntegerField(default=5)),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="core.project",
                    ),
                ),
                (
                    "reviewee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reviewer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews_written",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SavedProject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "freelancer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_projects",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_by",
                        to="core.project",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("freelancer", "project"), name="unique_saved_project")
                ],
            },
        ),
        migrations.CreateModel(
            name="ChatThread",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="client_threads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "freelancer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="freelancer_threads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chat_threads",
                        to="core.project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ChatMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "thread",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="core.chatthread",
                    ),
                ),
            ],
        ),
        migrations.AlterModelOptions(
            name="project",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="bid",
            options={"ordering": ("amount", "-match_score", "-created_at")},
        ),
        migrations.AlterModelOptions(
            name="notification",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="review",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="portfolioitem",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="chatthread",
            options={"ordering": ("-updated_at",)},
        ),
        migrations.AlterModelOptions(
            name="chatmessage",
            options={"ordering": ("created_at",)},
        ),
    ]
