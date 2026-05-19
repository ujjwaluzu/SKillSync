from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
from .services.ai_engine import (
    analyze_project,
    infer_title,
    recommendation_badges,
    score_freelancer,
)


def _profile_for(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def _role_required(request, role):
    return request.user.is_authenticated and _profile_for(request.user).role == role


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def landing(request):
    if request.user.is_authenticated:
        role = _profile_for(request.user).role
        return redirect("client_dashboard" if role == "client" else "freelancer_dashboard")
    return render(request, "core/landing.html")


def signup(request, role):
    valid_roles = dict(Profile.ROLE_CHOICES)
    if role not in valid_roles:
        messages.error(request, "Choose a valid account type.")
        return redirect("landing")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        full_name = request.POST.get("full_name", "").strip()
        skills = request.POST.get("skills", "").strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "That username is already taken.")
            return redirect("signup", role=role)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        user.save(update_fields=["first_name"])

        profile = _profile_for(user)
        profile.role = role
        profile.full_name = full_name
        profile.skills = skills if role == "freelancer" else ""
        profile.headline = "Ready to hire talent" if role == "client" else "Available for AI-matched projects"
        profile.save()

        messages.success(request, "Account created. You can sign in now.")
        return redirect("login")

    return render(request, "core/signup.html", {"role": role, "role_label": valid_roles[role]})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            role = _profile_for(user).role
            messages.success(request, f"Welcome back, {_profile_for(user).display_name}.")
            return redirect("client_dashboard" if role == "client" else "freelancer_dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("landing")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_project(request):
    if _profile_for(request.user).role != "client":
        return Response({"error": "Only clients can create projects."}, status=403)

    description = request.data.get("description", "").strip()
    title = request.data.get("title", "").strip() or infer_title(description)
    if not description:
        return Response({"error": "Description is required."}, status=400)

    freelancer_profiles = Profile.objects.select_related("user").filter(role="freelancer")
    analysis = analyze_project(
        description,
        freelancer_profiles=freelancer_profiles,
        similar_queryset=Project.objects.exclude(user=request.user),
    )
    project = Project.objects.create(
        user=request.user,
        title=title,
        description=description,
        min_price=analysis.min_price,
        max_price=analysis.max_price,
        estimated_price=analysis.estimated_price,
        estimated_days=analysis.estimated_days,
        estimated_time_label=analysis.time_label,
        complexity=analysis.complexity,
        confidence_score=analysis.confidence_score,
        skills=analysis.skills,
        tags=analysis.tags,
        budget_justification=analysis.budget_justification,
    )
    ProjectAIInsight.objects.create(
        project=project,
        extracted_skills=analysis.skills,
        generated_tags=analysis.tags,
        feature_summary=analysis.feature_summary,
        similar_projects=analysis.similar_projects,
        recommended_freelancers=analysis.recommended_freelancers,
    )

    return Response(
        {
            "id": project.id,
            "title": project.title_or_summary,
            "price_range": project.budget_range,
            "estimated_days": project.estimated_days,
            "complexity": project.complexity,
            "confidence": project.confidence_score,
            "skills": project.skills,
            "tags": project.tags,
            "budget_justification": project.budget_justification,
        }
    )


@api_view(["GET"])
def get_projects(request):
    projects = Project.objects.select_related("user").all()
    data = [
        {
            "id": project.id,
            "title": project.title_or_summary,
            "description": project.description,
            "price": project.budget_range,
            "status": project.status,
            "complexity": project.complexity,
        }
        for project in projects
    ]
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_bid(request):
    if _profile_for(request.user).role != "freelancer":
        return Response({"error": "Only freelancers can bid."}, status=403)

    project = get_object_or_404(Project, id=request.data.get("project_id"), status="open")
    amount = _safe_int(request.data.get("amount"))
    if amount <= 0:
        return Response({"error": "Bid amount must be positive."}, status=400)

    profile = _profile_for(request.user)
    match = score_freelancer(profile, project.skills, project.description, project.estimated_price)
    bid = Bid.objects.create(
        project=project,
        freelancer=request.user,
        amount=amount,
        proposed_days=_safe_int(request.data.get("proposed_days"), project.estimated_days or 7),
        cover_letter=request.data.get("cover_letter", ""),
        match_score=match["match_percentage"],
    )
    Notification.objects.create(
        recipient=project.user,
        title="New bid received",
        message=f"{profile.display_name} bid Rs. {amount:,} on {project.title_or_summary}.",
        kind="bid",
        target_url=project.get_absolute_url(),
    )

    return Response({"message": "Bid placed", "bid_id": bid.id, "match_score": bid.match_score})


@api_view(["GET"])
def get_bids(request, project_id):
    bids = Bid.objects.filter(project_id=project_id).select_related("freelancer")
    data = [
        {
            "freelancer": bid.freelancer.username,
            "amount": bid.amount,
            "proposed_days": bid.proposed_days,
            "match_score": bid.match_score,
            "status": bid.status,
        }
        for bid in bids
    ]
    return Response(data)


@login_required
def client_dashboard(request):
    if not _role_required(request, "client"):
        messages.error(request, "Client access required.")
        return redirect("landing")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        if not description:
            messages.error(request, "Project description is required.")
            return redirect("client_dashboard")

        freelancer_profiles = Profile.objects.select_related("user").filter(role="freelancer")
        analysis = analyze_project(
            description,
            freelancer_profiles=freelancer_profiles,
            similar_queryset=Project.objects.exclude(user=request.user),
        )
        project = Project.objects.create(
            user=request.user,
            title=title or infer_title(description),
            description=description,
            min_price=analysis.min_price,
            max_price=analysis.max_price,
            estimated_price=analysis.estimated_price,
            estimated_days=analysis.estimated_days,
            estimated_time_label=analysis.time_label,
            complexity=analysis.complexity,
            confidence_score=analysis.confidence_score,
            skills=analysis.skills,
            tags=analysis.tags,
            budget_justification=analysis.budget_justification,
        )
        ProjectAIInsight.objects.create(
            project=project,
            extracted_skills=analysis.skills,
            generated_tags=analysis.tags,
            feature_summary=analysis.feature_summary,
            similar_projects=analysis.similar_projects,
            recommended_freelancers=analysis.recommended_freelancers,
        )

        for recommendation in analysis.recommended_freelancers:
            Notification.objects.create(
                recipient_id=recommendation["user_id"],
                title="Recommended project match",
                message=(
                    f"{project.title_or_summary} matches your profile "
                    f"at {recommendation['match_percentage']}%."
                ),
                kind="project",
                target_url=project.get_absolute_url(),
            )

        messages.success(request, "Project posted with AI budget, time, skills, and recommendations.")
        return redirect(project.get_absolute_url())

    projects = (
        Project.objects.filter(user=request.user)
        .select_related("accepted_bid", "accepted_bid__freelancer", "ai_insight")
        .prefetch_related("bids", "bids__freelancer")
    )

    project_cards = []
    for project in projects:
        bids = project.bids.select_related("freelancer", "freelancer__profile").order_by(
            "-match_score",
            "amount",
        )
        project_cards.append(
            {
                "project": project,
                "bids": bids,
                "best_bid": bids.first(),
                "recommendations": getattr(project, "ai_insight", None).recommended_freelancers
                if hasattr(project, "ai_insight")
                else [],
            }
        )

    analytics = {
        "total_projects": projects.count(),
        "open_projects": projects.filter(status="open").count(),
        "total_bids": Bid.objects.filter(project__user=request.user).count(),
        "avg_budget": int(projects.aggregate(avg=Avg("estimated_price"))["avg"] or 0),
    }

    return render(
        request,
        "core/client.html",
        {
            "project_cards": project_cards,
            "analytics": analytics,
            "recent_notifications": request.user.notifications.all()[:5],
        },
    )


@login_required
def freelancer_dashboard(request):
    if not _role_required(request, "freelancer"):
        messages.error(request, "Freelancer access required.")
        return redirect("landing")

    profile = _profile_for(request.user)
    projects = Project.objects.filter(status="open").exclude(user=request.user).select_related("user")

    query = request.GET.get("q", "").strip()
    complexity = request.GET.get("complexity", "").strip()
    min_budget = _safe_int(request.GET.get("min_budget"))
    saved_only = request.GET.get("saved") == "1"

    if query:
        projects = projects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
            | Q(skills__icontains=query)
        )
    if complexity:
        projects = projects.filter(complexity=complexity)
    if min_budget:
        projects = projects.filter(max_price__gte=min_budget)
    if saved_only:
        projects = projects.filter(saved_by__freelancer=request.user)

    paginator = Paginator(projects.distinct(), 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    saved_ids = set(
        SavedProject.objects.filter(freelancer=request.user).values_list("project_id", flat=True)
    )

    project_cards = []
    for project in page_obj.object_list:
        score = score_freelancer(profile, project.skills, project.description, project.estimated_price)
        existing_bid = project.bids.filter(freelancer=request.user).first()
        project_cards.append(
            {
                "project": project,
                "match": score,
                "badges": recommendation_badges(score["match_percentage"], project),
                "saved": project.id in saved_ids,
                "existing_bid": existing_bid,
            }
        )

    analytics = {
        "available_projects": projects.count(),
        "saved_projects": len(saved_ids),
        "active_bids": Bid.objects.filter(freelancer=request.user, status="pending").count(),
        "accepted_bids": Bid.objects.filter(freelancer=request.user, status="accepted").count(),
    }

    return render(
        request,
        "core/freelancer.html",
        {
            "project_cards": project_cards,
            "page_obj": page_obj,
            "analytics": analytics,
            "filters": {
                "q": query,
                "complexity": complexity,
                "min_budget": min_budget or "",
                "saved": saved_only,
            },
        },
    )


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related(
            "user",
            "user__profile",
            "accepted_bid",
            "accepted_bid__freelancer",
            "ai_insight",
        ).prefetch_related("bids", "reviews"),
        id=project_id,
    )
    profile = _profile_for(request.user)
    bids = project.bids.select_related("freelancer", "freelancer__profile").order_by(
        "-match_score",
        "amount",
    )
    match = None
    is_saved = False
    existing_bid = None

    if profile.role == "freelancer":
        match = score_freelancer(profile, project.skills, project.description, project.estimated_price)
        is_saved = SavedProject.objects.filter(freelancer=request.user, project=project).exists()
        existing_bid = bids.filter(freelancer=request.user).first()

    return render(
        request,
        "core/project_detail.html",
        {
            "project": project,
            "bids": bids,
            "match": match,
            "is_saved": is_saved,
            "existing_bid": existing_bid,
            "reviews": project.reviews.select_related("reviewer", "reviewee")[:6],
            "ai_insight": getattr(project, "ai_insight", None),
        },
    )


@login_required
def place_bid_form(request, project_id):
    if not _role_required(request, "freelancer"):
        messages.error(request, "Freelancer access required.")
        return redirect("landing")

    project = get_object_or_404(Project, id=project_id, status="open")
    if request.method == "POST":
        amount = _safe_int(request.POST.get("amount"))
        proposed_days = _safe_int(request.POST.get("proposed_days"), project.estimated_days or 7)
        cover_letter = request.POST.get("cover_letter", "").strip()

        if amount <= 0:
            messages.error(request, "Enter a valid bid amount.")
            return redirect(project.get_absolute_url())

        profile = _profile_for(request.user)
        match = score_freelancer(profile, project.skills, project.description, project.estimated_price)
        existing_bid = Bid.objects.filter(project=project, freelancer=request.user).first()
        if existing_bid:
            existing_bid.amount = amount
            existing_bid.proposed_days = proposed_days
            existing_bid.cover_letter = cover_letter
            existing_bid.match_score = match["match_percentage"]
            existing_bid.status = "pending"
            existing_bid.save()
            bid = existing_bid
            messages.success(request, "Your bid has been updated.")
        else:
            bid = Bid.objects.create(
                project=project,
                freelancer=request.user,
                amount=amount,
                proposed_days=proposed_days,
                cover_letter=cover_letter,
                match_score=match["match_percentage"],
            )
            messages.success(request, "Bid placed successfully.")

        Notification.objects.create(
            recipient=project.user,
            title="Bid update",
            message=f"{profile.display_name} bid Rs. {bid.amount:,} on {project.title_or_summary}.",
            kind="bid",
            target_url=project.get_absolute_url(),
        )

    return redirect(project.get_absolute_url())


@login_required
def accept_bid(request, bid_id):
    bid = get_object_or_404(Bid.objects.select_related("project", "freelancer"), id=bid_id)
    project = bid.project

    if project.user != request.user:
        messages.error(request, "Only the client can accept bids for this project.")
        return redirect(project.get_absolute_url())
    if request.method != "POST":
        messages.error(request, "Use the project workflow to accept a bid.")
        return redirect(project.get_absolute_url())

    with transaction.atomic():
        Bid.objects.filter(project=project).exclude(id=bid.id).update(status="rejected")
        bid.status = "accepted"
        bid.save(update_fields=["status", "updated_at"])
        project.accepted_bid = bid
        project.status = "in_progress"
        project.save(update_fields=["accepted_bid", "status", "updated_at"])
        ChatThread.objects.get_or_create(
            project=project,
            client=request.user,
            freelancer=bid.freelancer,
        )

    Notification.objects.create(
        recipient=bid.freelancer,
        title="Bid accepted",
        message=f"Your bid on {project.title_or_summary} was accepted.",
        kind="bid",
        target_url=project.get_absolute_url(),
    )
    messages.success(request, "Bid accepted and project moved to in progress.")
    return redirect(project.get_absolute_url())


@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.user != request.user:
        messages.error(request, "Only the client can complete this project.")
        return redirect(project.get_absolute_url())
    if request.method != "POST":
        messages.error(request, "Use the project workflow to complete a project.")
        return redirect(project.get_absolute_url())

    already_completed = project.status == "completed"
    project.status = "completed"
    project.save(update_fields=["status", "updated_at"])
    if project.accepted_bid and not already_completed:
        Profile.objects.filter(user=project.accepted_bid.freelancer).update(
            completed_projects=F("completed_projects") + 1
        )
        Notification.objects.create(
            recipient=project.accepted_bid.freelancer,
            title="Project completed",
            message=f"{project.title_or_summary} has been marked completed.",
            kind="project",
            target_url=project.get_absolute_url(),
        )
    messages.success(request, "Project marked as completed.")
    return redirect(project.get_absolute_url())


@login_required
def toggle_saved_project(request, project_id):
    if not _role_required(request, "freelancer"):
        messages.error(request, "Only freelancers can save projects.")
        return redirect("landing")
    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER") or "freelancer_dashboard")

    project = get_object_or_404(Project, id=project_id)
    saved = SavedProject.objects.filter(freelancer=request.user, project=project).first()
    if saved:
        saved.delete()
        messages.info(request, "Project removed from saved list.")
    else:
        SavedProject.objects.create(freelancer=request.user, project=project)
        messages.success(request, "Project saved.")
    return redirect(request.META.get("HTTP_REFERER") or project.get_absolute_url())


@login_required
def profile_view(request, username=None):
    profile_user = get_object_or_404(User, username=username) if username else request.user
    profile = _profile_for(profile_user)
    is_owner = profile_user == request.user

    if request.method == "POST" and is_owner:
        action = request.POST.get("action", "profile")
        if action == "portfolio":
            PortfolioItem.objects.create(
                profile=profile,
                title=request.POST.get("portfolio_title", "").strip(),
                description=request.POST.get("portfolio_description", "").strip(),
                project_url=request.POST.get("portfolio_url", "").strip(),
                skills=request.POST.get("portfolio_skills", "").strip(),
            )
            messages.success(request, "Portfolio item added.")
        else:
            profile.full_name = request.POST.get("full_name", "").strip()
            profile.headline = request.POST.get("headline", "").strip()
            profile.bio = request.POST.get("bio", "").strip()
            profile.skills = request.POST.get("skills", "").strip()
            profile.location = request.POST.get("location", "").strip()
            profile.hourly_rate = _safe_int(request.POST.get("hourly_rate"))
            profile.portfolio_url = request.POST.get("portfolio_url", "").strip()
            profile.availability = request.POST.get("availability", profile.availability)
            profile.save()

            profile_user.email = request.POST.get("email", "").strip()
            profile_user.first_name = profile.full_name
            profile_user.save(update_fields=["email", "first_name"])
            messages.success(request, "Profile updated.")
        return redirect("profile")

    context = {
        "profile_user": profile_user,
        "profile_obj": profile,
        "is_owner": is_owner,
        "portfolio_items": profile.portfolio_items.all(),
        "reviews": profile_user.reviews_received.select_related("reviewer", "project")[:6],
        "projects": Project.objects.filter(user=profile_user)[:5],
        "bids": Bid.objects.filter(freelancer=profile_user).select_related("project")[:5],
    }
    return render(request, "core/profile.html", context)


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    if request.GET.get("mark_read") == "1":
        notifications.update(is_read=True)
        messages.success(request, "Notifications marked as read.")
        return redirect("notifications")
    return render(request, "core/notifications.html", {"notifications": notifications})


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect(notification.target_url or "notifications")


@login_required
def inbox(request):
    threads = ChatThread.objects.filter(Q(client=request.user) | Q(freelancer=request.user)).select_related(
        "project",
        "client",
        "freelancer",
    )
    return render(request, "core/inbox.html", {"threads": threads})


@login_required
def chat_thread(request, thread_id):
    thread = get_object_or_404(
        ChatThread.objects.select_related("project", "client", "freelancer"),
        id=thread_id,
    )
    if request.user not in (thread.client, thread.freelancer):
        messages.error(request, "You do not have access to this conversation.")
        return redirect("inbox")

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            ChatMessage.objects.create(thread=thread, sender=request.user, body=body)
            recipient = thread.freelancer if request.user == thread.client else thread.client
            Notification.objects.create(
                recipient=recipient,
                title="New message",
                message=f"{request.user.username} sent a message.",
                kind="message",
                target_url=reverse("chat_thread", args=[thread.id]),
            )
            messages.success(request, "Message sent.")
        return redirect("chat_thread", thread_id=thread.id)

    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    return render(request, "core/chat_thread.html", {"thread": thread})


@login_required
def start_chat(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)
    other_user = get_object_or_404(User, id=user_id)
    if request.user == project.user:
        client, freelancer = request.user, other_user
    else:
        client, freelancer = project.user, request.user

    thread, _ = ChatThread.objects.get_or_create(project=project, client=client, freelancer=freelancer)
    return redirect("chat_thread", thread_id=thread.id)


@login_required
def submit_review(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)
    reviewee = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        Review.objects.create(
            project=project,
            reviewer=request.user,
            reviewee=reviewee,
            rating=clamp_rating(_safe_int(request.POST.get("rating"), 5)),
            comment=request.POST.get("comment", "").strip(),
        )
        Notification.objects.create(
            recipient=reviewee,
            title="New review received",
            message=f"{request.user.username} reviewed your work on {project.title_or_summary}.",
            kind="review",
            target_url=project.get_absolute_url(),
        )
        messages.success(request, "Review submitted.")
    return redirect(project.get_absolute_url())


def clamp_rating(value):
    return max(1, min(5, value))
