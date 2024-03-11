import requests
import uuid
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.urls import reverse
from django.core import serializers
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import status, generics, serializers
from rest_framework.decorators import  permission_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.views import APIView

#from binance.client import Client
#from binance.websockets import BinanceSocketManager
#from binance.streams import BinanceSocketManager

from tanx_project.utility import update_alerts_in_cache_for_user
from .models import PriceAlert
from .serializers import PriceAlertSerializer, RegistrationSerializer


def index(request):
        return HttpResponse("Hello, world!")

class RegistrationAPIView(generics.GenericAPIView):

    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        #serializer.is_valid(raise_exception=True)
        #serializer.save()
        if serializer.is_valid():
            serializer.save()
            return Response({
                "RequestId": str(uuid.uuid4()),
                "Message": "User created successfully!!",

                "user": serializer.data
                },
                status=status.HTTP_201_CREATED
                )

        return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RestrictedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Your code here
        return JsonResponse({"response":"YOU ARE ALLOWED HERE"})


def signup(request):
        if request.method == 'POST':
                form = SignUpForm(request.POST)
                if form.is_valid():
                        form.save()
                        return redirect('login')
        else:
                form = SignUpForm()
        return render(request, 'registration:signup.html', {'form': form})


class CustomTokenObtainPairView(TokenObtainPairView):
        permission_classes = [AllowAny]

        def post(self, request, *args, **kwargs):
                serializer = self.get_serializer(data=request.data)
                print(request.data)
                if serializer.is_valid(raise_exception=True):
                        return Response(serializer.validated_data, status=HTTP_200_OK)
                else:
                        return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


def login_view(request):
        if request.method == 'POST':
                form = AuthenticationForm(request, data=request.POST)
                if form.is_valid():
                        username = form.cleaned_data.get('username')
                        password = form.cleaned_data.get('password')
                        user = authenticate(username=username, password=password)
                        if user is not None:
                                login(request, user)
                                return redirect(reverse('create_alert')) # Change 'dashboard' to your desired URL name
        else:
                form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

def logout_view(request):
        logout(request)
        return render(request, 'logout.html')


# Initialize the Binance client
"""client = Client('YOUR_API_KEY', 'YOUR_API_SECRET')

def get_binance_prices(request):
        # Define a callback function to handle WebSocket messages
        def handle_message(msg):
                # Process the message (in this example, we're just printing it)
                print(msg)

        # Create a BinanceSocketManager instance
        bm = BinanceSocketManager(client)

        # Subscribe to live price updates for a specific symbol
        conn_key = bm.start_symbol_ticker_socket('BTCUSDT', handle_message)

        # Start the WebSocket
        bm.start()

        # Return a JSON response (you may want to customize this)
        return JsonResponse({'status': 'WebSocket started'})


def get_coingecko_prices(request):
        # Specify the cryptocurrency you want to fetch prices for
        cryptocurrency = 'bitcoin'

        # Make a request to CoinGecko API to fetch current prices
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={cryptocurrency}&vs_currencies=usd'
        response = requests.get(url)

        if response.status_code == 200:
                data = response.json()
                # Extract the current price from the response
                current_price = data[cryptocurrency]['usd']
                return JsonResponse({'status': 'success', 'current_price': current_price})
        else:
                return JsonResponse({'status': 'error', 'message': 'Failed to fetch prices from CoinGecko'})"""


def fetch_coingecko_prices(request):
        # Cryptocurrency symbol (e.g., bitcoin)
        symbol = request.GET.get('symbol', 'bitcoin')

        # Make a request to CoinGecko API to fetch current prices
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd'
        response = requests.get(url)

        if response.status_code == 200:
                data = response.json()
                # Extract the current price from the response
                current_price = data.get(symbol, {}).get('usd')
                return JsonResponse({'status': 'success', 'current_price': current_price})
        else:
                return JsonResponse({'status': 'error', 'message': 'Failed to fetch prices from CoinGecko'})


class DeleteAlertView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        alert_id = request.GET.get('alert_id', None)
        #return JsonResponse({'page': alert_id})
        if alert_id:
            try:
                alert = PriceAlert.objects.get(id=int(alert_id), user=request.user)
            except:
                return Response({"message": "Alert Id Not Found"}, status=status.HTTP_400_BAD_REQUEST)
            alert.is_deleted = True
            alert.save()
            return Response({"message": "Alert Deleted!"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid Parameters"}, status=status.HTTP_400_BAD_REQUEST)



class FetchAlertsView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated] #[IsAuthenticated. AllowAny]

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        start = (int(page)-1)*10
        end = int(page) * 10
        data = cache.get('alert_'+ str(request.user.id), None)
        if data:
            data = data[start:end]
            return Response(json.dumps(data))
        else:
            #return JsonResponse({'page': page})
            #here we can use paginator
            alerts = PriceAlert.objects.filter(
                user=request.user, 
                is_deleted=False
                ).order_by('-created_at')[start:end]
            serializer = PriceAlertSerializer(alerts, many=True)
            # if not exist in cache update in cache
            #update_alerts_in_cache_for_user(request.user)
            return Response(serializer.data)

class FilterFetchAlertsView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated] #[IsAuthenticated. AllowAny]

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        direction = request.GET.get('direction', None)
        is_triggered = request.GET.get('is_triggered', None)
        start = (int(page)-1)*10
        end = int(page) * 10
        #fetch from cache and apply filter here
        alerts = PriceAlert.objects.filter(
            user=request.user, 
            is_deleted=False
            ).order_by('-created_at')
        if direction is not None:
            alerts = alerts.filter(direction=int(direction))
        if is_triggered:
            alerts = alerts.filter(is_triggered = True)

        #return JsonResponse({'page': page})
        serialze_alerts = alerts[start:end]
        serializer = PriceAlertSerializer(serialze_alerts, many=True)
        return Response(serializer.data)


class CreateAlertView(APIView):
        renderer_classes = [JSONRenderer]
        permission_classes = [IsAuthenticated] #[IsAuthenticated.  AllowAny]
        serializer_class = RegistrationSerializer

        def get(self, request, *args, **kwargs):
            return render(request, 'create_alert.html')
            
                #data = {'message': 'Hello, world!'}
                #return Response(data)

        def post(self, request, *args, **kwargs):
            #serializer = self.get_serializer(data=request.data)
            serializer = PriceAlertSerializer(data=request.data)
            
            #data = serializers.serialize('json', request.data)
            #return HttpResponse(data, content_type='application/json')

            #ToDo: check if requesting user and user in request are same
            if serializer.is_valid():
                serializer.save()
                update_alerts_in_cache_for_user(request.user)
                #return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response({
                    "RequestId": str(uuid.uuid4()), 
                    "Message": "Alert created successfully!!", 
                    "alert": serializer.data
                    },
                    status=status.HTTP_200_OK)


            #return Response(request.user, status=status.HTTP_400_BAD_REQUEST)
            return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)




