#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from address.models import Address
from address.utilities import address_tools
from bestway.models import User
from bestway.utilities import bw_tools, algorithm
from bestway.form import *


"""
    This module contains all the views of the Bestway application.
"""

################################################################################
#####                                VIEWS                                 #####
################################################################################

class SignUpView(CreateView):
    """
        This view allows the user to login or create an account.
    """
    form_class = AccountForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

################################################################################

@login_required
def account(request):
    """
        This view allows the user to see the details of his account.
    """
    return render(request, 'account.html')

################################################################################

def home(request):
    """
        This view is the home page of the Bestway application. We generate the
        forms we need to save the start and the end addresses.
    """
    if request.method == 'POST':
        address_form = AddressForm(request.POST)

        if request.user.is_active:

            if address_form.is_valid():
                start = bw_tools.clean_address(address_form.cleaned_data['start'])
                end = bw_tools.clean_address(address_form.cleaned_data['end'])
                start_json = bw_tools.request_to_GeoApiGouvFr(start, 'start')
                end_json = bw_tools.request_to_GeoApiGouvFr(end, 'end')

                Address.objects.filter(user_id=request.user.id, start=True).delete()
                Address.objects.filter(user_id=request.user.id, end=True).delete()

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
            return render(
                request, 'home.html', 
                {"alerts": ["Pour pouvoir utiliser l'application connecte toi "
                "ou crée un compte. C'est gratuit et sans engagement."]}
            )

    else:
        address_form = AddressForm()

    return render(request, 'home.html', {"address_form": address_form})

################################################################################

@login_required
def destinations(request):
    """
        This view generate the form we need to save all the stops the user has
        to do during the day. We make sure that he doesn't save two times the
        same addresses wich it would be unusefull and also that he cannot save
        more than 5 stops which represents already 120 differents ways.
    """
    if request.method == 'POST':
        stops_form = StopsForm(request.POST)

        if stops_form.is_valid():
            stop = bw_tools.clean_address(stops_form.cleaned_data['stops'])
            stop_json = bw_tools.request_to_GeoApiGouvFr(stop, 'stop')
            number_of_stop = address_tools.create_address_object(
                stop_json,
                User.objects.get(id=request.user.id)
            )

            if number_of_stop == 5:
                return redirect('result')
            else:
                pass

    else:
        stops_form = StopsForm()

    return render(request, 'destinations.html', {"stops_form": stops_form})

################################################################################

@login_required
def result(request):
    """
        This view calculate the Bestway and put it in the template used for.
        We create objects to separate the values of longitude and latitude in each
        addresses iin the list to not get problems when we substract values.
        We delete all the addresses in the database after the result is display
        in the template.
    """
    id_user = int(request.user.id)
    list_of_addresses = Address.objects.filter(user_id=id_user).values()
    list_of_addresses = algorithm.addresses_list(list_of_addresses)
    ways = algorithm.find_all_differents_ways(
        list_of_addresses, len(list_of_addresses)-2
    )

    mirrors_ways = []
    mirrors_ways.append(ways)
    mirrors_ways.append(ways)

    for mirror in mirrors_ways:
        for list_of_ways in mirror:
            for addresses in list_of_ways:
                index = list_of_ways.index(addresses)
                for key, value in addresses.items():
                    if key == 'start' and value == True:
                        address_object = Address.objects.get(
                            name=addresses['address'], start=True
                        )
                        address = {
                            "address": address_object.name,
                            "nature": 'start',
                            "longitude": address_object.longitude,
                            "latitude": address_object.latitude,
                            "distance": 0
                        }
                        list_of_ways[index] = address

                    elif key == 'end' and value == True:
                        address_object = Address.objects.get(
                            name=addresses['address'], end=True
                        )
                        address = {
                            "address": address_object.name,
                            "nature": 'end',
                            "longitude": address_object.longitude,
                            "latitude": address_object.latitude,
                            "distance": 0
                        }
                        list_of_ways[index] = address

                    elif key == 'stop' and value == True:
                        address_object = Address.objects.get(
                            name=addresses['address'], stop=True
                        )
                        address = {
                            "address": address_object.name,
                            "nature": 'stop',
                            "longitude": address_object.longitude,
                            "latitude": address_object.latitude,
                            "distance": 0
                        }
                        list_of_ways[index] = address

    all_ways = algorithm.calculate_distances(mirrors_ways)

    the_bestway = algorithm.find_the_bestway(all_ways)

    Address.objects.filter(user_id=request.user.id).delete()

    return render(request, 'result.html', {
        'start': [the_bestway[0]],
        'stops': the_bestway[1:-1],
        'end': [the_bestway[-1]]
        }
    )

################################################################################

def conditions(request):
    """
        This view is used to publish the using-conditions and polities of
        the Bestway application.
    """
    return render(request, 'conditions.html')

################################################################################

def mentions_legales(request):
    """
        This view is used to publish the legal-mentions of the Bestway application.
    """
    return render(request, 'mentions_legales.html')
