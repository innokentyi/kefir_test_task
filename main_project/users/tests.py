import datetime

from django.test import TestCase, Client, runner
from django.contrib.auth.models import User
import json
from .models import MyUser, City


def authentication_settings(testcase_class: TestCase):
    """
    this will be used in many test to send authorized request
    """
    MyUser.objects.create(email='admin@mail.ru', password='password', birthday='2020-08-08', first_name='mario',
                          last_name='super', other_name='some_other')
    testcase_class.client.cookies['userid'] = MyUser.objects.all()[0].id


class LoginTest(TestCase):
    def test_no_login_and_pass(self):
        """
        if no login and password in session params, 422 error should be returned as response with corresponding data
        """
        response = self.client.post('/users/login', content_type='application/json')
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.reason_phrase, 'Validation Error')
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['detail'][0]['loc'][0], "LoginView.post")
        self.assertEqual(content['detail'][0]['msg']['login'], "This field is required")
        self.assertEqual(content['detail'][0]['msg']['password'], "This field is required")
        self.assertEqual(content['detail'][0]['type'], "UserValidationError")

    def test_no_login(self):
        """
        if no login in session params, 422 error should be returned as response with corresponding error data
        """
        response = self.client.post('/users/login', content_type='application/json', data={'password': 'password'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.reason_phrase, 'Validation Error')
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['detail'][0]['loc'][0], "LoginView.post")
        self.assertEqual(content['detail'][0]['msg']['login'], "This field is required")
        self.assertEqual(content['detail'][0]['type'], "UserValidationError")

    def test_no_pass(self):
        """
        if no password in session params, 422 error should be returned as response with corresponding error data
        """
        response = self.client.post('/users/login', content_type='application/json', data={'login': 'login'})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.reason_phrase, 'Validation Error')
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['detail'][0]['loc'][0], "LoginView.post")
        self.assertEqual(content['detail'][0]['msg']['password'], "This field is required")
        self.assertEqual(content['detail'][0]['type'], "UserValidationError")

    def test_no_such_user(self):
        """
        if no user with login specified exists, 400 error should be returned as response with corresponding error data
        """
        response = self.client.post('/users/login', content_type='application/json',
                                    data={'login': 'login', 'password': 'password'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason_phrase, 'Bad Request')
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['code'], 1)
        self.assertEqual(content['message'], "User with such login doesn't exist")

    def test_invalid_pass(self):
        """
        if invalid password for user specified, 400 error should be returned with corresponding data
        """
        MyUser.objects.create(email='opa@mail.ru', password='123', birthday='2020-08-08')

        response = self.client.post('/users/login', content_type='application/json',
                                    data={'login': 'opa@mail.ru', 'password': 'password'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.reason_phrase, 'Bad Request')
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['code'], 2)
        self.assertEqual(content['message'], "Incorrect password for such user")

    def test_get_request_not_allowed(self):
        """
        there should be only post request to path /users/login
        """
        response = self.client.get('/users/login')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.reason_phrase, 'Method Not Allowed')

    def test_successful_login(self):
        """
        if login and password correct we will have user id as our cookie and 200 response with corresponding data
        """
        MyUser.objects.create(email='admin@mail.ru', password='password', birthday='2020-08-08', first_name='mario',
                              last_name='super', other_name='some_other')
        self.assertNotIn('userid', self.client.cookies)
        response = self.client.post('/users/login', {'login': 'admin@mail.ru', 'password': 'password', 'lifetime': 3},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(content['first_name'], 'mario')
        self.assertEqual(content['last_name'], 'super')
        self.assertEqual(content['other_name'], 'some_other')
        self.assertEqual(content['email'], 'admin@mail.ru')
        self.assertEqual(content['birthday'], '2020-08-08')
        self.assertEqual(content['phone'], '')
        self.assertFalse(content['is_admin'])

        self.assertIn('userid', self.client.cookies)


class LogoutTest(TestCase):
    """
    cookie will be expired after logout
    """

    def test_logout(self):
        authentication_settings(self)

        self.assertTrue('userid' in self.client.cookies)  # was logged in
        response = self.client.get('/users/logout')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(datetime.datetime.strptime(self.client.cookies['userid']['expires'], '%a, %d %b %Y %H:%M:%S %Z')
                        < datetime.datetime.now())  # cookies became expired


class UsersListTest(TestCase):
    def test_post_request_not_allowed(self):
        """
        there should be only get request to path /users/users
        """
        response = self.client.post('/users/users')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.reason_phrase, 'Method Not Allowed')

    def test_unauthorized(self):
        """
        if no cookie set with correct user there should be returned 401
        """
        response = self.client.get('/users/users')
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 4)
        self.assertEqual(content['msg'], 'no cookie to recognise session was specified')

        MyUser.objects.create(email='admin@mail.ru', password='password', birthday='2020-08-08', first_name='mario',
                              last_name='super', other_name='some_other')
        self.client.cookies['userid'] = '2'  # unexisting
        response = self.client.get('/users/users')
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 5)
        self.assertEqual(content['msg'], 'user with such cookie bounding doesn\'t exist')

    def test_no_page_and_size(self):
        """
        if page or size not specified in request, 422 error and corresponding message
        """
        authentication_settings(self)

        response = self.client.get('/users/users')
        self.assertEqual(response.status_code, 422)
        content = json.loads(response.content)
        self.assertEqual(content['detail'][0]['loc'][0], 'UsersList.get')
        self.assertEqual(content['detail'][0]['msg'], 'no page or size parameter in request')
        self.assertEqual(content['detail'][0]['type'], 'PageParamsValidation')

    def test_not_enouth_users(self):
        authentication_settings(self)

        MyUser.objects.create(email='2@mail.ru', birthday='2020-12-12')
        MyUser.objects.create(email='3@mail.ru', birthday='2020-12-12')

        response = self.client.get('/users/users?page=2&size=3')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 3)
        self.assertEqual(content['message'], 'no such page')

    def test_successful_request(self):
        authentication_settings(self)

        MyUser.objects.create(email='2@mail.ru', birthday='2020-12-12')
        MyUser.objects.create(email='3@mail.ru', password='password', birthday='2020-08-08', first_name='mario',
                              last_name='super')

        response = self.client.get('/users/users?page=2&size=2')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)['data']
        meta = json.loads(response.content)['meta']
        self.assertEqual(content[0]['id'], 3)
        self.assertEqual(content[0]['email'], '3@mail.ru')
        self.assertEqual(content[0]['first_name'], 'mario')
        self.assertEqual(content[0]['last_name'], 'super')
        self.assertEqual(meta['pagination']['total'], 1)
        self.assertEqual(meta['pagination']['page'], 2)
        self.assertEqual(meta['pagination']['size'], 2)


class UsersCurrent(TestCase):
    def test_unauthorized(self):
        response = self.client.get('/users/current')
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 4)
        self.assertEqual(content['msg'], 'no cookie to recognise session was specified')

        MyUser.objects.create(email='admin@mail.ru', password='password', birthday='2020-08-08', first_name='mario',
                              last_name='super', other_name='some_other')
        self.client.cookies['userid'] = '2'  # unexisting
        response = self.client.get('/users/current')
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 5)
        self.assertEqual(content['msg'], 'user with such cookie bounding doesn\'t exist')

    def test_success(self):
        authentication_settings(self)
        response = self.client.get('/users/current')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['first_name'], 'mario')
        self.assertEqual(content['last_name'], 'super')
        self.assertEqual(content['other_name'], 'some_other')
        self.assertEqual(content['email'], 'admin@mail.ru')
        self.assertEqual(content['phone'], '')
        self.assertEqual(content['birthday'], '2020-08-08')
        self.assertFalse(content['is_admin'])


class User(TestCase):
    def test_unauthorized(self):
        response = self.client.patch('/users/users/1')
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 4)
        self.assertEqual(content['msg'], 'no cookie to recognise session was specified')

        MyUser.objects.create(email='admin@mail.ru', password='password', birthday='2020-08-08', first_name='mario',
                              last_name='super', other_name='some_other')
        self.client.cookies['userid'] = '2'  # unexisting
        response = self.client.patch('/users/users/1')
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 5)
        self.assertEqual(content['msg'], 'user with such cookie bounding doesn\'t exist')

    def test_no_user_with_such_id(self):
        authentication_settings(self)

        response = self.client.patch('/users/users/2')
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 8)
        self.assertEqual(content['message'], 'User with such id doesn\'t exist')

    def test_user_cannot_modify_others(self):
        authentication_settings(self)
        MyUser.objects.create(email='3@mail.ru', birthday='2020-12-12')

        response = self.client.patch('/users/users/2')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 7)
        self.assertEqual(content['message'], 'This user cannot modify user with id 2if this user admin, he must use '
                                             'private mode')

    def test_validation_params_error(self):
        authentication_settings(self)

        response = self.client.patch('/users/users/1', data={'first_name': 'Luigi'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['id'], 1)
        self.assertEqual(content['first_name'], 'Luigi')
        self.assertEqual(content['last_name'], 'super')
        self.assertEqual(content['other_name'], 'some_other')
        self.assertEqual(content['email'], 'admin@mail.ru')
        self.assertEqual(content['phone'], '')
        self.assertEqual(content['birthday'], '2020-08-08')

        self.assertEqual(MyUser.objects.get(id=1).first_name, 'Luigi')


class PrivateUserList(TestCase):
    def test_unauthorized(self):
        response = self.client.get('/users/private/users')
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 4)
        self.assertEqual(content['msg'], 'no cookie to recognise session was specified')

        MyUser.objects.create(email='admin@mail.ru', password='password', birthday='2020-08-08', first_name='mario',
                              last_name='super', other_name='some_other')
        self.client.cookies['userid'] = '2'  # unexisting
        response = self.client.get('/users/private/users')
        self.assertEqual(response.status_code, 401)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 5)
        self.assertEqual(content['msg'], 'user with such cookie bounding doesn\'t exist')

    def test_forbidden(self):
        authentication_settings(self)
        response = self.client.get('/users/private/users')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['code'], 10)
        self.assertEqual(json.loads(response.content)['msg'], 'only admins can access this info')

    def test_get_no_page_or_size(self):
        """
        if page or size not specified in request, 422 error and corresponding message
        """
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        response = self.client.get('/users/private/users')
        self.assertEqual(response.status_code, 422)
        content = json.loads(response.content)
        self.assertEqual(content['detail'][0]['loc'][0], 'PrivateUserList.get')
        self.assertEqual(content['detail'][0]['msg'], 'no page or size parameter in request')
        self.assertEqual(content['detail'][0]['type'], 'PageParamsValidation')

    def test_get_not_enough_users(self):
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        MyUser.objects.create(email='2@mail.ru', birthday='2020-12-12')
        MyUser.objects.create(email='3@mail.ru', birthday='2020-12-12')

        response = self.client.get('/users/users?page=2&size=3')
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 3)
        self.assertEqual(content['message'], 'no such page')

    def test_successful_get(self):
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        response = self.client.get('/users/users?page=1&size=3')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)['data']
        meta = json.loads(response.content)['meta']
        self.assertEqual(content[0]['id'], 1)
        self.assertEqual(content[0]['email'], 'admin@mail.ru')
        self.assertEqual(content[0]['first_name'], 'mario')
        self.assertEqual(content[0]['last_name'], 'super')
        self.assertEqual(meta['pagination']['total'], 1)
        self.assertEqual(meta['pagination']['page'], 1)
        self.assertEqual(meta['pagination']['size'], 3)

    def test_create_user_validation_error(self):
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        response = self.client.post('/users/private/users', data={"first_name": 'f', "last_name": 'l', "email": 'e',
                                                                  "is_admin": True, }, content_type='application/json')
        self.assertEqual(response.status_code, 422)
        content = json.loads(response.content)['detail'][0]
        self.assertEqual(content['loc'][0], 'PrivateUserList.post')
        self.assertEqual(content['msg']['email'][0], "Enter a valid email address.")
        self.assertEqual(content['msg']['password'][0], "This field is required.")

        self.assertEqual(len(MyUser.objects.all()), 1)  # new one didn't create

    def test_create_user_success(self):
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        response = self.client.post('/users/private/users',
                                    data={"first_name": 'f', "last_name": 'l', "email": 'e@m.ru',
                                          "is_admin": True, 'password': 123}, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        content = json.loads(response.content)
        self.assertEqual(content['id'], 2)
        self.assertEqual(content['first_name'], 'f')
        self.assertEqual(content['last_name'], 'l')
        self.assertEqual(content['other_name'], '')
        self.assertEqual(content['email'], 'e@m.ru')
        self.assertEqual(content['phone'], '')
        self.assertEqual(content['birthday'], None)
        self.assertEqual(content['is_admin'], True)
        self.assertEqual(content['city'], None)
        self.assertEqual(content['additional_info'], '')

        self.assertEqual(len(MyUser.objects.all()), 2)  # new one created


class PrivateUser(TestCase):
    """
    we won't write test for unauthorized and forbidden because the same code is executing,
    and also we will try only for get no user test
    """

    def test_no_such_user(self):
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        response = self.client.get('/users/private/users/2')
        self.assertEqual(response.status_code, 404)
        content = json.loads(response.content)
        self.assertEqual(content['code'], 8)
        self.assertEqual(content['message'], 'User with such id doesn\'t exist')

    def test_get_successful(self):
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        response = self.client.get('/users/private/users/1')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['id'], 1)
        self.assertEqual(content['first_name'], 'mario')
        self.assertEqual(content['last_name'], 'super')
        self.assertEqual(content['other_name'], 'some_other')
        self.assertEqual(content['email'], 'admin@mail.ru')
        self.assertEqual(content['phone'], '')
        self.assertEqual(content['birthday'], '2020-08-08')
        self.assertEqual(content['is_admin'], True)
        self.assertEqual(content['city'], None)
        self.assertEqual(content['additional_info'], '')

    def test_delete_successful(self):
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        response = self.client.delete('/users/private/users/1')
        self.assertEqual(response.status_code, 204)
        content = response._reason_phrase
        self.assertEqual(content, 'Successful Response')
        self.assertEqual(len(MyUser.objects.all()), 0)

    def test_patch_successful(self):
        authentication_settings(self)
        user = MyUser.objects.all()[0]
        user.is_admin = True
        user.save()

        response = self.client.patch('/users/private/users/1', data={'first_name': 'Luigi'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['id'], 1)
        self.assertEqual(content['first_name'], 'Luigi')
        self.assertEqual(content['last_name'], 'super')
        self.assertEqual(content['other_name'], 'some_other')
        self.assertEqual(content['email'], 'admin@mail.ru')
        self.assertEqual(content['phone'], '')
        self.assertEqual(content['birthday'], '2020-08-08')
        self.assertEqual(content['is_admin'], True)
        self.assertEqual(content['city'], None)
        self.assertEqual(content['additional_info'], '')

        self.assertEqual(MyUser.objects.get(id=1).first_name, 'Luigi')
