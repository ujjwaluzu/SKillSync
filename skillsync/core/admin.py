from django.contrib import admin

from .models import (
    Bid,
    ChatMessage,
    ChatThread,
    Notification,
    PortfolioItem,
    Profile,
    Project,
    ProjectAIInsight,
    Review,
    SavedProject,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "role", "rating", "completed_projects", "availability")
    list_filter = ("role", "availability")
    search_fields = ("user__username", "full_name", "skills")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title_or_summary", "user", "complexity", "status", "estimated_price", "created_at")
    list_filter = ("status", "complexity")
    search_fields = ("title", "description", "user__username")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("project", "freelancer", "amount", "proposed_days", "status", "match_score")
    list_filter = ("status",)
    search_fields = ("project__title", "freelancer__username")


admin.site.register(ProjectAIInsight)
admin.site.register(SavedProject)
admin.site.register(Notification)
admin.site.register(Review)
admin.site.register(PortfolioItem)
admin.site.register(ChatThread)
admin.site.register(ChatMessage)
