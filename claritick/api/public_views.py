from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from brake.decorators import ratelimit
from api.accesslog import login_success, login_error
from api.serializers import (
    LoginSerializer,
    UserSerializer
)


class LoginView(APIView):
    permission_classes = (AllowAny, )

    @staticmethod
    @ratelimit(rate='5/min')
    def login_ratelimit(request):
        if getattr(request, 'limited', False):
            return Response({}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    @staticmethod
    @ratelimit(rate='10/min')
    def autologin_ratelimit(request):
        if getattr(request, 'limited', False):
            return Response({}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    def _get_logindata(self, request, errors=[]):
        logindata = {
            'isLogged': False,
            'active': False,
            'user': {},
            'errors': errors,
            'setsessionexpiry': False,
        }
        if request.user.is_authenticated():
            logindata["isLogged"] = True
            logindata["active"] = True
            logindata["user"] = UserSerializer(request.user).data
            logindata["sessionid"] = request.session.session_key
        return logindata

    def get(self, request):
        """Login using sessions / cookies"""
        resp_status = status.HTTP_401_UNAUTHORIZED
        resp_data = {}
        ratelimit = self.autologin_ratelimit(request)
        if ratelimit is not None:
            return ratelimit
        resp_data = self._get_logindata(request)
        if request.user.is_authenticated():
            resp_status = status.HTTP_200_OK
            login_success(request)
        else:
            logout(request)
        return Response(resp_data, status=resp_status)

    def post(self, request, format=None):
        errors = []
        resp_status = status.HTTP_400_BAD_REQUEST
        # We re-authenticate if the user is already logged-in, but
        # re-submit the form
        if (not request.user.is_authenticated() or
                request.DATA.get("username")):
            if request.DATA.get("username") and request.DATA.get("password"):
                ratelimit = self.login_ratelimit(request)
                if ratelimit is not None:
                    return ratelimit
            serializer = LoginSerializer(data=request.DATA)
            if serializer.is_valid():
                user = authenticate(username=serializer.data['username'],
                                    password=serializer.data['password'])
                resp_status = status.HTTP_401_UNAUTHORIZED
                if user and user.is_active:
                    login(request, user)
            else:
                errors = serializer.errors
        # Yes login should have modified our "user" we recheck with a if
        logindata = self._get_logindata(request, errors)
        if request.user.is_authenticated():
            resp_status = status.HTTP_200_OK
            login_success(request)
            logindata["setsessionexpiry"] = True
        else:
            login_error(request, username=serializer.data['username'])
        return Response(logindata, status=resp_status)


class LogoutView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, format=None):
        logout(request)
        return Response({}, status=status.HTTP_200_OK)
