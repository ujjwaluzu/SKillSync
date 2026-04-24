from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project, Bid
from .ai import extract_features, estimate_price


@api_view(['POST'])
def create_project(request):
    text = request.data.get("description")

    features = extract_features(text)
    min_price, max_price = estimate_price(features)

    project = Project.objects.create(
        description=text,
        min_price=min_price,
        max_price=max_price
    )

    return Response({
        "id": project.id,
        "price_range": f"{min_price} - {max_price}"
    })


@api_view(['GET'])
def get_projects(request):
    projects = Project.objects.all()
    data = []

    for p in projects:
        data.append({
            "id": p.id,
            "description": p.description,
            "price": f"{p.min_price}-{p.max_price}"
        })

    return Response(data)


@api_view(['POST'])
def place_bid(request):
    project_id = request.data.get("project_id")
    freelancer = request.data.get("freelancer")
    amount = request.data.get("amount")

    project = Project.objects.get(id=project_id)

    bid = Bid.objects.create(
        project=project,
        freelancer=freelancer,
        amount=amount
    )

    return Response({"message": "Bid placed"})


@api_view(['GET'])
def get_bids(request, project_id):
    bids = Bid.objects.filter(project_id=project_id)

    data = []
    for b in bids:
        data.append({
            "freelancer": b.freelancer,
            "amount": b.amount
        })

    return Response(data)





from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Profile


def landing(request):
    return render(request, "core/landing.html")


def signup(request, role):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.create_user(username=username, password=password)
        user.profile.role = role
        user.profile.save()

        return redirect("/login/")

    return render(request, "core/signup.html", {"role": role})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)

            if user.profile.role == "client":
                return redirect("/client/")
            else:
                return redirect("/freelancer/")

    return render(request, "core/login.html")



from .models import Project
from .ai import extract_features, estimate_price

from .ml_model import predict_price, estimate_time

def client_dashboard(request):
    result = None

    if request.method == "POST":
        text = request.POST.get("description")

        min_p, max_p, avg = predict_price(text)
        time = estimate_time(avg)
        Project.objects.create(
            description=text,
            min_price=min_p,
            max_price=max_p
        )

        result = {
            "min": min_p,
            "max": max_p,
            "avg": avg,
            "time": time
        }

    return render(request, "core/client.html", {"result": result})

from .models import Bid

def freelancer_dashboard(request):
    projects = Project.objects.all()
    return render(request, "core/freelancer.html", {"projects": projects})




from django.shortcuts import redirect

def place_bid_form(request, project_id):
    if request.method == "POST":
        freelancer = request.POST.get("freelancer")
        amount = request.POST.get("amount")

        project = Project.objects.get(id=project_id)

        Bid.objects.create(
            project=project,
            freelancer=freelancer,
            amount=amount
        )

    return redirect("/freelancer/")