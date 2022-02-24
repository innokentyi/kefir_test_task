from django.http.request import HttpRequest
from django.http.response import JsonResponse
from .models import MyUser


def try_authorization(request: HttpRequest):
    """
    we will try to return corresponding user by id in cookie
    if not success we will return JsonResponse to return in caller-function
    """
    if 'userid' not in request.COOKIES:
        return JsonResponse(status=401,
                            data={'code': 4, 'msg': 'no cookie to recognise session was specified'},
                            reason='Unauthorized')
    try:
        user = MyUser.objects.get(id=request.COOKIES['userid'])
        return user
    except MyUser.DoesNotExist:
        return JsonResponse(status=401,
                            data={'code': 5, 'msg': 'user with such cookie bounding doesn\'t exist'},
                            reason='Unauthorized')
