from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
import responses
import json


def user_create(email='test@test.com', password='testpassword45',
                first_name='First Name', last_name='Last Name'):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )


class AuthServiceTest(APITestCase):
    
    @patch('authentication.tasks.send_confiramtion_code.delay')
    def test_registration(self, mock_send_confiramtion_code):
        url = reverse('authentication:registration_user_data')
        data = {
            'email': 'test@test.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'Test',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session = self.client.session
        self.assertIn('confirmation_code', session)
        self.assertIn('registration_data', session)
        self.assertEqual(session['registration_data']['email'], data['email'])
        self.assertEqual(session['registration_data']['password'], data['password'])
        self.assertEqual(session['registration_data']['first_name'], data['first_name'])
        self.assertEqual(session['registration_data']['last_name'], data['last_name'])
        mock_send_confiramtion_code.assert_called_once()

    def test_registration_confirmation_code(self):
        session = self.client.session
        session['confirmation_code'] = 111111
        session.save()

        url = reverse('authentication:registration_email_confirmation')
        invalid_data = {'code': 555555}
        valid_data = {'code': 111111}

        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        session = self.client.session

        self.assertIn('is_email_confirmed', session)
        self.assertTrue(session['is_email_confirmed'])
        self.assertNotIn('confirmation_code', session)

    @responses.activate
    def test_registration_categories_choice_get(self):
        responses.add(responses.GET, 'http://testserver/courses/category-list/',
                      json=[{
                                'id': 1,
                                'title': '1st category'
                            },
                            {
                                'id': 2,
                                'title': '2nd category'
                            },
                            {
                                'id': 3,
                                'title': '3rd category'
                            },
                            {
                                'id': 4,
                                'title': '4th category'
                            }
                        ])
        
        session = self.client.session
        session['is_email_confirmed'] = True
        reg_data = {
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'Test',
            'password': '29048fhweivu'
        }
        session['registration_data'] = reg_data
        session.save()

        url = reverse('authentication:registration_category_choice')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 4)
        self.assertEqual(response.json()[0], {'id': 1, 'title': '1st category'})

    @patch('authentication.views.current_app.send_task')
    def test_registration_categories_choice_post(self, mock_send_task):
        reg_data = {
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'Test',
            'password': '29048fhweivu'
        }
        session = self.client.session
        session['is_email_confirmed'] = True
        session['registration_data'] = reg_data
        session.save()

        categories_liked_data = [{
                                     'id': 1,
                                     'title': '1st category'
                                 },
                                 {
                                     'id': 2,
                                     'title': '2nd category'
                                 },
                                 {
                                     'id': 3,
                                     'title': '3rd category'
                                 },
                                 {
                                     'id': 4,
                                     'title': '4th category'
                                 }
        ]
        url = reverse('authentication:registration_category_choice')
        response = self.client.post(url, categories_liked_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        full_reg_data = {**reg_data, 'categories_liked': []}
        for category in categories_liked_data:
            full_reg_data['categories_liked'].append(category)
        mock_send_task.assert_called_with(
            'user_service.create_user',
            kwargs={**full_reg_data},
            queue='user_service_queue'
        )

    def test_registration_categories_choice_post_forbidden(self):
        categories_liked_data = [{
                                     'id': 1,
                                     'title': '1st category'
                                 },
                                 {
                                     'id': 2,
                                     'title': '2nd category'
                                 },
                                 {
                                     'id': 3,
                                     'title': '3rd category'
                                 },
                                 {
                                     'id': 4,
                                     'title': '4th category'
                                 }
        ]
        url = reverse('authentication:registration_category_choice')
        response = self.client.post(url, categories_liked_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_categories_choice_post_invalid_data(self):
        reg_data = {
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'Test',
            'password': '29048fhweivu'
        }
        session = self.client.session
        session['is_email_confirmed'] = True
        session['registration_data'] = reg_data
        session.save()

        categories_liked_data = [{
                                     'id': 1,
                                     'title': '1st category'
                                 },
                                 {
                                     'id': 2,
                                 },
                                 {
                                     'title': '3rd category'
                                 },
                                 {
                                     'id': 4,
                                 }
        ]
        url = reverse('authentication:registration_category_choice')
        response = self.client.post(
            url, categories_liked_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_categories_choice_post_less_3_values(self):

        reg_data = {
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'Test',
            'password': '29048fhweivu'
        }
        session = self.client.session
        session['is_email_confirmed'] = True
        session['registration_data'] = reg_data
        session.save()

        categories_liked_data = [
            {
                'id': 1,
                'title': '1st category'
            },
        ]
        url = reverse('authentication:registration_category_choice')
        response = self.client.post(
            url, categories_liked_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        user = user_create(email='test@test.com', password='testpassword')
        
        url = reverse('authentication:token_obtain_pair')
        data = {
            'email': 'test@test.com',
            'password': 'testpassword'
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertIn('refresh', content)
        self.assertIn('access', content)


class TestPasswordReset(APITestCase):
    def test_password_reset_input_email(self):
        from django.core.mail import outbox
        email = 'fidjsan@gmail.com'
        user = user_create(email=email)
        url = reverse('authentication:password_reset')
        data = {'email': email}

        response = self.client.post(url, data=data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(outbox), 1)
        session = self.client.session
        self.assertIn('confirmation_code', session)
        message = outbox[0]
        confirmation_code = int(message.body[-6:])
        self.assertEqual(session['confirmation_code'], confirmation_code)

    def test_password_reset_confirm_email(self):
        session = self.client.session
        confirmation_code = 111111
        session['confirmation_code'] = confirmation_code
        session.save()

        url = reverse('authentication:password_reset_confirmation')
        data = {'code': confirmation_code}

        session = self.client.session

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(session['is_email_confirmed'])
        self.assertNotIn('confirmation_code', session)

    @patch('authentication.views.current_app.send_task')
    def test_password_reset_set_new_password(self, mock_send_task):
        email = 'iowhvbd@gmail.com'
        user = user_create(email=email)

        password = 'u3gh9843e'
        data = {'password': password}
        url = reverse('authentication:password_reset_new_password')

        session = self.client.session
        session['email'] = email
        session['is_email_confirmed'] = True
        session.save()
        
        response = self.client.post(url, data=data, format='json')
        session = self.client.session

        user = get_user_model().objects.get(email=email)
        
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('is_email_confirmed', session)
        self.assertNotIn('email', session)
        self.assertTrue(user.check_password(password))
        mock_send_task.assert_called_with(
            'user_service.update_reset_password',
            kwargs={
                'email': email,
                'new_password': password
            }, queue='user_service_queue'
        )
