#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpRequest
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from address.models import Address
from address.utilities import address_tools
from bestway.models import User
from bestway.utilities import bw_tools, algorithm
from bestway.form import *

from itertools import permutations
# Create your views here.

class SignUpView(CreateView):
    """
        This view allows the user to login or create an account.
    """
    form_class = AccountForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def account(request):
     return render(request, 'account.html')

def home(request):

    if request.method == 'POST':
        address_form = AddressForm(request.POST)

        if address_form.is_valid():
            start = bw_tools.clean_address(address_form.cleaned_data['start'])
            end = bw_tools.clean_address(address_form.cleaned_data['end'])
            start_json = bw_tools.request_to_GeoApiGouvFr(start, 'start')
            end_json = bw_tools.request_to_GeoApiGouvFr(end, 'end')

            address_tools.create_address_object(
                start_json,
                User.objects.get(id=request.user.id)
            )
            address_tools.create_address_object(
                end_json,
                User.objects.get(id=request.user.id)
            )

            return redirect('destinations')

    else:
        address_form = AddressForm()

    return render(request, 'home.html', {"address_form": address_form})

@login_required
def destinations(request):

    if request.method == 'POST':
        stops_form = StopsForm(request.POST)

        if stops_form.is_valid():
            stop = bw_tools.clean_address(stops_form.cleaned_data['stops'])
            stop_json = bw_tools.request_to_GeoApiGouvFr(stop, 'stop')
            address_tools.create_address_object(
                stop_json,
                User.objects.get(id=request.user.id)
            )

    else:
        stops_form = StopsForm()

    return render(request, 'destinations.html', {"stops_form": stops_form})

@login_required
def result(request):

    id_user = int(request.user.id)
    list_of_addresses = Address.objects.filter(user_id=id_user).values()
    list_of_addresses = algorithm.addresses_list(list_of_addresses)
    ways = algorithm.find_all_differents_ways(list_of_addresses, len(list_of_addresses)-2)

    mirrors_ways = []
    mirrors_ways.append(ways)
    mirrors_ways.append(ways)

    for mirror in mirrors_ways:
        for list_of_ways in mirror:
            for addresses in list_of_ways:
                address = {
                    "address": addresses,
                    "nature": "start",
                    "longitude": 0,
                    "latitude": 0,
                    "distance": 0
                }

    # list_of_ways_of_address = [
    #     [
    #         [
    #             {'address': 'départ', 'nature': 'start', 'long': 30, 'lat': 50, "distance": 0},
    #             {'address': 'pointA', 'nature': 'stop', 'long': 30, 'lat': 80, "distance": 0},
    #             {'address': 'pointB', 'nature': 'stop', 'long': 20, 'lat': 70, "distance": 0},
    #             {'address': 'arrivée', 'nature': 'end', 'long': 10, 'lat': 40, "distance": 0}
    #         ],
    #         [
    #             {'address': 'départ', 'nature': 'start', 'long': 30, 'lat': 50, "distance": 0},
    #             {'address': 'pointB', 'nature': 'stop', 'long': 20, 'lat': 70, "distance": 0},
    #             {'address': 'pointA', 'nature': 'stop', 'long': 30, 'lat': 80, "distance": 0},
    #             {'address': 'arrivée', 'nature': 'end', 'long': 10, 'lat': 40, "distance": 0}
    #         ]
    #     ],
    #     [
    #         [
    #             {'address': 'départ', 'nature': 'start', 'long': 30, 'lat': 50, "distance": 0},
    #             {'address': 'pointA', 'nature': 'stop', 'long': 30, 'lat': 80, "distance": 0},
    #             {'address': 'pointB', 'nature': 'stop', 'long': 20, 'lat': 70, "distance": 0},
    #             {'address': 'arrivée', 'nature': 'end', 'long': 10, 'lat': 40, "distance": 0}
    #         ],
    #         [
    #             {'address': 'départ', 'nature': 'start', 'long': 30, 'lat': 50, "distance": 0},
    #             {'address': 'pointB', 'nature': 'stop', 'long': 20, 'lat': 70, "distance": 0},
    #             {'address': 'pointA', 'nature': 'stop', 'long': 30, 'lat': 80, "distance": 0},
    #             {'address': 'arrivée', 'nature': 'end', 'long': 10, 'lat': 40, "distance": 0}
    #         ]
    #     ]
    # ]

    # shortest_way = algorithm.calculate_distances(ways)

    # shortest_way  = algorithm.find_the_bestway(shortest_way)

    return render(request, 'result.html')

@login_required
def delete_user_addresses(request):

    id_user = int(request.user.id)
    if request.method == 'POST':
        address_tools.delete_user_addresses(id_user)
        return redirect('home')

def conditions(request):

    return render(request, 'conditions.html')

def mentions_legales(request):

    return render(request, 'mentions_legales.html')