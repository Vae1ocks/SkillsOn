from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
import responses


def user_create(email='test@test.com', password='testpassword45', first_name=None, last_name=None):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )


class Auth_ServiceTest(APITestCase):
    def test_registration(self):
        from django.core.mail import outbox
        url = reverse('authentication:registration_user_data')
        data = {
            'email': 'test@test.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        session = self.client.session
        self.assertIn('confirmation_code', session)
        self.assertIn('registration_data', session)
        self.assertEqual(session['registration_data']['email'], data['email'])
        self.assertEqual(session['registration_data']['password'], data['password'])
        self.assertEqual(len(outbox), 1)
        message = outbox[0]
        confirmation_code = int(message.body[-6:])
        self.assertEqual(session['confirmation_code'], confirmation_code)

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
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        
        session = self.client.session

        self.assertIn('is_email_confirmed', session)
        self.assertTrue(session['is_email_confirmed'])
        self.assertNotIn('confirmation_code', session)

    @responses.activate
    def test_registration_categories_choice_get(self):
        responses.add(responses.GET, 'http://127.0.0.1:8002/category-list/',
                      json=[{'title': '1st category'},
                            {'title': '2nd category'},
                            {'title': '3rd category'},
                            {'title': '4th category'}
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
        self.assertEqual(response.json()[0], {'title': '1st category'})

    @responses.activate
    def test_registration_categories_choice_post(self):
        responses.add(responses.POST, 'http://127.0.0.1:8001/user_create',
                      status=status.HTTP_201_CREATED)
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

        categories_liked_data = [{'title': '1st category'},
                                 {'title': '2nd category'},
                                 {'title': '3rd category'},
                                 {'title': '4th category'}
        ]
        url = reverse('authentication:registration_category_choice')
        response = self.client.post(url, categories_liked_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_categories_choice_post_forbidden(self):
        categories_liked_data = [{'title': '1st category'},
                                 {'title': '2nd category'},
                                 {'title': '3rd category'},
                                 {'title': '4th category'}
        ]
        url = reverse('authentication:registration_category_choice')
        response = self.client.post(url, categories_liked_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login(self):
        user = user_create(email='test@test.com', password='testpassword')
        
        url = reverse('authentication:login')
        data = {
            'email': 'test@test.com',
            'password': 'testpassword'
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)