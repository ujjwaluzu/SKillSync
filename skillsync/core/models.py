from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    ROLE_CHOICES = (
        ("client", "Client"),
        ("freelancer", "Freelancer"),
    )

    AVAILABILITY_CHOICES = (
        ("available", "Available"),
        ("busy", "Busy"),
        ("offline", "Offline"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="freelancer")
    full_name = models.CharField(max_length=120, blank=True)
    headline = models.CharField(max_length=180, blank=True)
    bio = models.TextField(blank=True)
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated skills, for example: Django, UI Design, Payments",
    )
    location = models.CharField(max_length=120, blank=True)
    hourly_rate = models.PositiveIntegerField(default=0)
    completed_projects = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    portfolio_url = models.URLField(blank=True)
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default="available",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name} ({self.get_role_display()})"

    @property
    def display_name(self):
        return self.full_name or self.user.get_full_name() or self.user.username

    def skill_list(self):
        return [skill.strip() for skill in self.skills.split(",") if skill.strip()]


class Project(models.Model):
    STATUS_CHOICES = (
        ("open", "Open"),
        ("in_review", "In Review"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    COMPLEXITY_CHOICES = (
        ("basic", "Basic"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("expert", "Expert"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=180, blank=True)
    description = models.TextField()
    min_price = models.PositiveIntegerField(default=0)
    max_price = models.PositiveIntegerField(default=0)
    estimated_price = models.PositiveIntegerField(default=0)
    estimated_days = models.PositiveIntegerField(default=0)
    estimated_time_label = models.CharField(max_length=80, blank=True)
    complexity = models.CharField(
        max_length=20,
        choices=COMPLEXITY_CHOICES,
        default="intermediate",
    )
    confidence_score = models.PositiveIntegerField(default=0)
    skills = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    budget_justification = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    accepted_bid = models.ForeignKey(
        "Bid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_for_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title_or_summary

    @property
    def title_or_summary(self):
        if self.title:
            return self.title
        return self.description[:70]

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.pk])

    @property
    def budget_range(self):
        return f"Rs. {self.min_price:,} - Rs. {self.max_price:,}"


class Bid(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("shortlisted", "Shortlisted"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="bids")
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.PositiveIntegerField()
    proposed_days = models.PositiveIntegerField(default=7)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    match_score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("amount", "-match_score", "-created_at")

    def __str__(self):
        return f"{self.freelancer.username} - Rs. {self.amount}"


class ProjectAIInsight(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="ai_insight",
    )
    extracted_skills = models.JSONField(default=list, blank=True)
    generated_tags = models.JSONField(default=list, blank=True)
    feature_summary = models.JSONField(default=dict, blank=True)
    similar_projects = models.JSONField(default=list, blank=True)
    recommended_freelancers = models.JSONField(default=list, blank=True)
    model_version = models.CharField(max_length=40, default="rf-tfidf-v2")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI insight for {self.project.title_or_summary}"


class SavedProject(models.Model):
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_projects",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("freelancer", "project"),
                name="unique_saved_project",
            )
        ]

    def __str__(self):
        return f"{self.freelancer.username} saved {self.project.title_or_summary}"


class Notification(models.Model):
    KIND_CHOICES = (
        ("system", "System"),
        ("project", "Project"),
        ("bid", "Bid"),
        ("message", "Message"),
        ("review", "Review"),
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=160)
    message = models.TextField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="system")
    target_url = models.CharField(max_length=240, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    reviewee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.rating}/5 for {self.reviewee.username}"


class PortfolioItem(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="portfolio_items",
    )
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    project_url = models.URLField(blank=True)
    skills = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class ChatThread(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_threads",
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_threads",
    )
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="freelancer_threads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"{self.client.username} and {self.freelancer.username}"


class ChatMessage(models.Model):
    thread = models.ForeignKey(
        ChatThread,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Message from {self.sender.username}"
