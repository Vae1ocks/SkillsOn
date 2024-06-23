from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model


def user_create(email='test@test.com', password='testpassword45', first_name=None, last_name=None):
    categories_liked = [{'title': 'cat1'}, {'title': 'cat2'}, {'title': 'cat3'}, {'title': 'cat4'}],
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        categories_liked=categories_liked
    )


class TestUser(APITestCase):
    def test_user_create(self):
        url = reverse('users:user_create')
        data = {
            'email': 'test@gmail.com',
            'first_name': '1stName',
            'last_name': 'lstName',
            'about_self': 'about_self',
            'categories_liked': [{'title': 'cat1'}, {'title': 'cat2'},
                                {'title': 'cat3'}, {'title': 'cat4'}],
            'password': 'testpassword123'
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_user_password_reset(self):
        email = 'test@test.com'
        user = user_create(email=email)
        password = 'passwordfortest'

        url = reverse('users:user_password_reset')
        data = {
            'email': email,
            'new_password': password
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        
        user = get_user_model().objects.get(email=email)

        self.assertTrue(user.check_password(password))