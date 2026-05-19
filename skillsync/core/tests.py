from django.contrib.auth.models import User
from django.test import TestCase

from .models import Profile
from .services.ai_engine import analyze_project, score_freelancer


class AIEngineTests(TestCase):
    def test_project_analysis_extracts_budget_drivers(self):
        analysis = analyze_project(
            "Build ecommerce website with payment integration, login, and admin dashboard"
        )

        self.assertIn("Payments", analysis.skills)
        self.assertIn("Authentication", analysis.skills)
        self.assertGreater(analysis.estimated_price, 0)
        self.assertGreater(analysis.confidence_score, 0)
        self.assertIn("payment integration", analysis.budget_justification)

    def test_freelancer_match_uses_skill_overlap(self):
        user = User.objects.create_user(username="freelancer")
        profile = Profile.objects.get(user=user)
        profile.skills = "Django, Payments, Authentication, Admin Dashboard"
        profile.completed_projects = 4
        profile.rating = 4.5
        profile.save()

        score = score_freelancer(
            profile,
            ["Django", "Payments", "Authentication"],
            "Django project with payments",
            40000,
        )

        self.assertGreaterEqual(score["match_percentage"], 70)
        self.assertIn("Payments", score["skill_overlap"])
