from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.http import JsonResponse
from .models import MyUser, City
import json
from .schemas import *
from .serialisers import LoginModelSerializer, PrivateCreateUserModelSerializer, PrivateUpdateUserModelSerializer, \
    UpdateUserModelSerializer
from .utils import try_authorization


class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginModel,
        tags=['auth'],
        operation_id='login_login_post',
        operation_summary='Вход в систему',
        operation_description='После успешного входа в систему необходимо установить Cookies для пользователя',
        responses={400: openapi.Response('Bad Request', ErrorResponseModel),
                   422: openapi.Response('Validation Error', HTTPValidationError),
                   200: openapi.Response('Successful Response', CurrentUserResponseModel)}
    )
    def post(self, request):
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['LoginView.post'],
                                                  'msg': 'incorrect data format. application/json expected',
                                                  'type': 'ParamsParseError'}]},
                                reason='Validation Error')

        ser = LoginModelSerializer(data=body)
        flag = ser.is_valid()
        if not ser.is_valid():
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['LoginView.post'],
                                                  'msg': ser.errors,
                                                  'type': 'UserValidationError'}]},
                                reason='Validation Error')

        try:
            user = ser.get_instance()
        except MyUser.DoesNotExist:
            return JsonResponse(status=400, data={'code': 1, 'message': 'User with such login doesn\'t exist'},
                                reason='Bad Request')

        if not user.check_password(
                ser.validated_data['password']):  # todo: realise whether it needs to be in serializer
            return JsonResponse(status=400, data={'code': 2, 'message': 'Incorrect password for such user'},
                                reason='Bad Request')

        response = JsonResponse(data=user.get_current_user_response_model(), status=200, reason='Successful Response')

        cookie_expires = 300
        response.set_cookie('userid', str(user.id), max_age=cookie_expires)

        return response


class LogoutView(APIView):
    @swagger_auto_schema(
        tags=['auth'],
        operation_id='logout_logout_get',
        operation_summary='Выход из системы',
        operation_description='При успешном выходе необходимо удалить установленные Cookies',
        responses={200: openapi.Response('Successful Response')}
    )
    def get(self, request):
        response = JsonResponse(status=200, data={}, reason='Successful Response')
        response.delete_cookie('userid')

        return response


class UserList(APIView):
    @swagger_auto_schema(
        tags=['user'],
        manual_parameters=[
            openapi.Parameter(name='page', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter(name='size', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
        ],
        operation_id='users_users_get',
        operation_summary='Постраничное получение кратких данных обо всех пользователях',
        operation_description='Здесь находится вся информация, доступная пользователю о других пользователях',
        responses={
            200: openapi.Response('Successful Response', UsersListResponseModel),
            401: openapi.Response('Unauthorized', openapi.Schema(title='Response 401 Private Users Private Users Get',
                                                                 type=openapi.TYPE_STRING)),
            400: openapi.Response('Bad Request', ErrorResponseModel),
            422: openapi.Response('Validation Error', HTTPValidationError)
        }
    )
    def get(self, request):
        user = try_authorization(request)  # JsonResponse will return, when can't get user
        if type(user) is JsonResponse:
            return user

        if 'page' not in request.GET or 'size' not in request.GET:
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['UsersList.get'],
                                                  'msg': 'no page or size parameter in request',
                                                  'type': 'PageParamsValidation'}]},
                                reason='Validation Error')

        page = int(request.GET['page'])
        size = int(request.GET['size'])

        users = MyUser.objects.all()
        if len(users) <= (page - 1) * size:
            return JsonResponse(status=400, data={'code': 3, 'message': 'no such page'},
                                reason='Bad Request')

        users = users[(page - 1) * size: page * size]

        return JsonResponse(
            data={
                'data': [user.get_short_user_model() for user in users],
                'meta': {
                    'pagination': {
                        'total': len(users),
                        'page': page,
                        'size': size
                    },
                }
            },
            status=200,
            reason='Successful Response')


class PrivateUserList(APIView):
    @swagger_auto_schema(
        tags=['admin'],
        manual_parameters=[
            openapi.Parameter(name='page', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
            openapi.Parameter(name='size', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY),
        ],
        operation_id='private_users_private_users_get',
        operation_summary='Постраничное получение кратких данных обо всех пользователях',
        operation_description='Здесь находится вся информация, доступная пользователю о других пользователях',

        responses={

            200: openapi.Response('Successful Response', PrivateUsersListResponseModel),
            400: openapi.Response('Bad Request', ErrorResponseModel),
            401: openapi.Response('Unauthorized', openapi.Schema(title='Response 401 Private Users Private Users Get',
                                                                 type=openapi.TYPE_STRING)),
            403: openapi.Response('Unauthorized', openapi.Schema(title='Response 403 Private Users Private Users Get',
                                                                 type=openapi.TYPE_STRING)),
            422: openapi.Response('Validation Error', HTTPValidationError),
        }
    )
    def get(self, request):
        user = try_authorization(request)  # JsonResponse will return, when can't get user
        if type(user) is JsonResponse:
            return user

        if not user.is_admin:
            return JsonResponse(status=403,
                                data={'code': 10, 'msg': 'only admins can access this info'},
                                reason='Forbidden')

        if 'page' not in request.GET or 'size' not in request.GET:
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['PrivateUserList.get'],
                                                  'msg': 'no page or size parameter in request',
                                                  'type': 'PageParamsValidation'}]},
                                reason='Validation Error')

        page = int(request.GET['page'])
        size = int(request.GET['size'])

        users = MyUser.objects.all()
        if len(users) <= (page - 1) * size:
            return JsonResponse(status=400, data={'code': 3, 'message': 'no such page'},
                                reason='Bad Request')

        users = users[(page - 1) * size: page * size]

        return JsonResponse(
            data={
                'data': [user.get_short_user_model() for user in users],
                'meta': {
                    'pagination': {
                        'total': len(users),
                        'page': page,
                        'size': size
                    },
                    'hint': {
                        'city': [{
                            'id': city.id,
                            'name': city.name
                        } for city in City.objects.all()
                        ]
                    }
                }
            },
            status=200,
            reason='Successful Response')

    @swagger_auto_schema(
        request_body=PrivateCreateUserModel,
        tags=['admin'],
        operation_id='private_create_users_private_users_post',
        operation_summary='Создание пользователя',
        operation_description='Здесь возможно занести в базу нового пользователя с минимальной информацией о нем',
        responses={
            201: openapi.Response('Successful Response', PrivateDetailUserResponseModel),
            400: openapi.Response('Bad Request', ErrorResponseModel),
            401: openapi.Response('Unauthorized',
                                  openapi.Schema(title='Response 401 Private Create Users Private Users Post',
                                                 type=openapi.TYPE_STRING)),
            403: openapi.Response('Unauthorized',
                                  openapi.Schema(title='Response 403 Private Create Users Private Users Post',
                                                 type=openapi.TYPE_STRING)),
            422: openapi.Response('Validation Error', HTTPValidationError),
        }
    )
    def post(self, request):
        user = try_authorization(request)  # JsonResponse will return, when can't get user
        if type(user) is JsonResponse:
            return user

        if not user.is_admin:
            return JsonResponse(status=403,
                                data={'code': 10, 'msg': 'only admins can access this info'},
                                reason='Forbidden')
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['PrivateUserList.post'],
                                                  'msg': 'incorrect data format. application/json expected',
                                                  'type': 'ParamsParseError'}]},
                                reason='Validation Error')

        ser = PrivateCreateUserModelSerializer(data=body)
        if not ser.is_valid():
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['PrivateUserList.post'],
                                                  'msg': ser.errors,
                                                  'type': 'UserValidationError'}]},
                                reason='Validation Error')

        user = ser.save()

        return JsonResponse(data=user.get_privateDetailUserResponseModel(), status=201, reason='Successful Response')


class PrivateUser(APIView):
    @swagger_auto_schema(
        tags=['admin'],
        operation_summary='Детальное получение информации о пользователе',
        operation_id='private_get_user_private_users__pk__get',
        operation_description='Здесь администратор может увидеть всю существующую пользовательскую информацию',
        responses={200: openapi.Response('Successful Response', PrivateDetailUserResponseModel),
                   400: openapi.Response('Bad Request', ErrorResponseModel),
                   401: openapi.Response('Unauthorized',
                                         openapi.Schema(title='Response 401 Private Get User Private Users  Pk  Get',
                                                        type=openapi.TYPE_STRING)),
                   403: openapi.Response('Forbidden',
                                         openapi.Schema(title='Response 403 Private Get User Private Users  Pk  Get',
                                                        type=openapi.TYPE_STRING)),
                   404: openapi.Response('Not Found',
                                         openapi.Schema(title='Response 404 Private Get User Private Users  Pk  Get',
                                                        type=openapi.TYPE_STRING)),
                   422: openapi.Response('Validation Error', HTTPValidationError)
                   }
    )
    def get(self, request, pk):
        user = try_authorization(request)  # JsonResponse will return, when can't get user
        if type(user) is JsonResponse:
            return user

        if not user.is_admin:
            return JsonResponse(status=403,
                                data={'code': 10, 'msg': 'only admins can access this info'},
                                reason='Forbidden')

        user = MyUser.objects.filter(id=pk)
        if len(user) == 0:
            return JsonResponse(status=404, data={'code': 8, 'message': 'User with such id doesn\'t exist'},
                                reason='Not Found')

        return JsonResponse(data=user[0].get_privateDetailUserResponseModel(), status=200, reason='Successful Response')

    @swagger_auto_schema(
        tags=['admin'],
        operation_summary='Удаление пользователя',
        operation_id='private_delete_user_private_users__pk__delete',
        operation_description='Удаление пользователя',
        responses={204: openapi.Response('Successful Response'),
                   401: openapi.Response('Unauthorized',
                                         openapi.Schema(title='Response 401 Private Delete User Private Users  Pk  '
                                                              'Delete   ',
                                                        type=openapi.TYPE_STRING)),
                   403: openapi.Response('Forbidden',
                                         openapi.Schema(title='Response 403 Private Delete User Private Users  Pk  '
                                                              'Delete',
                                                        type=openapi.TYPE_STRING)),
                   422: openapi.Response('Validation Error', HTTPValidationError)
                   }
    )
    def delete(self, request, pk):
        user = try_authorization(request)  # JsonResponse will return, when can't get user
        if type(user) is JsonResponse:
            return user

        if not user.is_admin:
            return JsonResponse(status=403,
                                data={'code': 10, 'msg': 'only admins can access this info'},
                                reason='Forbidden')

        user = MyUser.objects.filter(id=pk)
        if len(user) == 0:
            return JsonResponse(status=404, data={'code': 8, 'message': 'User with such id doesn\'t exist'},
                                reason='Not Found')

        user.delete()

        return JsonResponse(status=204, reason='Successful Response', data={})

    @swagger_auto_schema(
        tags=['admin'],
        operation_summary='Изменение информации о пользователе',
        operation_id='private_patch_user_private_users__pk__patch',
        operation_description='Здесь администратор может изменить любую информацию о пользователе',
        request_body=PrivateUpdateUserModel,
        responses={200: openapi.Response('Successful Response'),
                   400: openapi.Response('Bad Request', ErrorResponseModel),
                   401: openapi.Response('Unauthorized',
                                         openapi.Schema(title='Response 401 Private Patch User Private Users  Pk  Patch',
                                                        type=openapi.TYPE_STRING)),
                   403: openapi.Response('Forbidden',
                                         openapi.Schema(title='Response 403 Private Patch User Private Users  Pk  Patch',
                                                        type=openapi.TYPE_STRING)),
                   404: openapi.Response('Not Found',
                                         openapi.Schema(title='Response 404 Private Patch User Private Users  Pk  Patch',
                                                        type=openapi.TYPE_STRING)),
                   422: openapi.Response('Validation Error', HTTPValidationError)
                   }
    )
    def patch(self, request, pk):
        user = try_authorization(request)  # JsonResponse will return, when can't get user
        if type(user) is JsonResponse:
            return user

        if not user.is_admin:
            return JsonResponse(status=403,
                                data={'code': 10, 'msg': 'only admins can access this info'},
                                reason='Forbidden')

        user = MyUser.objects.filter(id=pk)
        if len(user) == 0:
            return JsonResponse(status=404, data={'code': 8, 'message': 'User with such id doesn\'t exist'},
                                reason='Not Found')

        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['PrivateUser.patch'],
                                                  'msg': 'incorrect data format. application/json expected',
                                                  'type': 'ParamsParseError'}]},
                                reason='Validation Error')

        ser = PrivateUpdateUserModelSerializer(data=body)
        if not ser.is_valid():
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['LoginView.post'],
                                                  'msg': ser.errors,
                                                  'type': 'UserValidationError'}]},
                                reason='Validation Error')

        user.update(**ser.validated_data)
        user[0].save()

        return JsonResponse(data=user[0].get_privateDetailUserResponseModel(), status=200, reason='Successful Response')


class User(APIView):
    @swagger_auto_schema(
        tags=['user'],
        operation_summary='Изменение данных пользователя',
        operation_id='edit_user_users__pk__patch',
        operation_description='Здесь пользователь имеет возможность изменить свои данные',
        request_body=UpdateUserModel,
        responses={200: openapi.Response('Successful Response', UpdateUserResponseModel),
                   400: openapi.Response('Bad Request', ErrorResponseModel),
                   401: openapi.Response('Unauthorized',
                                         openapi.Schema(title='Response 401 Private Users Private Users Get',
                                                        type=openapi.TYPE_STRING)),
                   404: openapi.Response('Not Found',
                                         openapi.Schema(title='Response 404 Edit User Users  Pk  Patch',
                                                        type=openapi.TYPE_STRING)),
                   422: openapi.Response('Validation Error', HTTPValidationError)
                   }
    )
    def patch(self, request, pk):
        auth_user = try_authorization(request)  # JsonResponse will return, when can't get user
        if type(auth_user) is JsonResponse:
            return auth_user

        users = MyUser.objects.filter(pk=pk)
        if len(users) == 0:
            return JsonResponse(status=404, data={'code': 8, 'message': 'User with such id doesn\'t exist'},
                                reason='Not Found')

        if auth_user.id != pk:
            return JsonResponse(status=400,
                                data={'code': 7, 'message': f'This user cannot modify user with id {pk}'
                                                            f'if this user admin, he must use private mode'},
                                reason='Bad Request')

        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['User.patch'],
                                                  'msg': 'incorrect data format. application/json expected',
                                                  'type': 'ParamsParseError'}]},
                                reason='Validation Error')

        ser = UpdateUserModelSerializer(data=body)
        if not ser.is_valid():
            return JsonResponse(status=422,
                                data={'detail': [{'loc': ['LoginView.post'],
                                                  'msg': ser.errors,
                                                  'type': 'UserValidationError'}]},
                                reason='Validation Error')

        users.update(**ser.validated_data)
        users[0].save()

        data = users[0].get_privateDetailUserResponseModel()
        del data['is_admin']
        del data['city']
        del data['additional_info']

        return JsonResponse(data=data, status=200, reason='Successful Response')


class CurrentUser(APIView):
    @swagger_auto_schema(
        tags=['user'],
        operation_summary='Получение данных о текущем пользователе',
        operation_id='current_user_users_current_get',
        operation_description='Здесь находится вся информация, доступная пользователю о самом себе,\n        '
                              'а так же информация является ли он администратором',
        responses={200: openapi.Response('Successful Response', CurrentUserResponseModel),
                   401: openapi.Response('Unauthorized', openapi.Schema(title='Response 401 Current User Users '
                                                                              'Current Get',
                                                                        type=openapi.TYPE_STRING)),
                   400: openapi.Response('Bad Request', ErrorResponseModel)}
    )
    def get(self, request):
        user = try_authorization(request)  # JsonResponse will return, when can't get user
        if type(user) is JsonResponse:
            return user

        response = JsonResponse(data=user.get_current_user_response_model(), status=200, reason='Successful Response')

        return response
