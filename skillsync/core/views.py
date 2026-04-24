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