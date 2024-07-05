from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch


class TestUser(APITestCase):
    def user_create(self, email='test@test.com', password='testpassword45',
                    first_name='Test', last_name='User'):
        self.categories_liked = [{'title': 'cat1'}, {'title': 'cat2'},
                                 {'title': 'cat3'}, {'title': 'cat4'}],
        self.email = email
        self.password = password
        return get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            categories_liked=self.categories_liked
        )
    @patch('users.tasks.user_personal_info_updated_event.delay')
    def test_user_personal_info_update(self, mock_send_confirmation_code):
        user = self.user_create()
        data = {
            'first_name': 'New Name',
            'last_name': 'For User',
            'about_self': 'Something about self'
        }
        url = reverse('users:personal_info_update')
        is_authenticated = self.client.login(username=self.email, password=self.password)
        self.assertTrue(is_authenticated)

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        mock_send_confirmation_code.assert_called_once()
        user.refresh_from_db()
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])
        self.assertEqual(user.about_self, data['about_self'])

    @patch('users.tasks.send_confirmation_code.delay')
    def test_user_email_update_confirmate_old_email(self, mock_send_confirmation_code):
        user = self.user_create()
        is_authenticated = self.client.login(username=self.email, password=self.password)
        self.assertTrue(is_authenticated)
        url = reverse('users:email_update_confirmation_old_email')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_confirmation_code.assert_called_once()

        session = self.client.session
        session['confirmation_code'] = 111111
        session.save()
        url = reverse('users:email_update_confirmation_old_email')
        data = {'code': 111111}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('users.tasks.send_confirmation_code.delay')
    def test_user_email_update_set_new_email(self, mock_send_confirmation_code):
        user = self.user_create()
        self.client.login(username=self.email, password=self.password)
        session = self.client.session
        session['email_confirmated'] = True
        session.save()
        data = {'email': 'newemail@new.com'}
        url = reverse('users:email_update_set_new_email')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_confirmation_code.assert_called_once()
        user.refresh_from_db()
        self.assertNotEqual(user.email, data['email'])

    @patch('users.tasks.user_email_updated_event.delay')
    def test_user_email_confirmate_new_email(self, mock_user_email_updated_event):
        user = self.user_create()
        self.client.login(username=self.email, password=self.password)
        session = self.client.session
        session['confirmation_code'] = 111111
        session.save()
        url = reverse('users:email_update_confirmation_new_email')
        data = {
            'email':'new_email@new.com',
            'code': 111111
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_user_email_updated_event.assert_called_once()
        user.refresh_from_db()
        self.assertEqual(user.email, data['email'])

    @patch('users.tasks.user_password_updated_event.delay')
    def test_user_password_change(self, mock_user_password_updated_event):
        user = self.user_create()
        self.client.login(username=self.email, password=self.password)
        data = {
            'old_password': self.password,
            'new_password': 'newpassword1337'
        }
        url = reverse('users:password_update')

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_user_password_updated_event.assert_called_once()
        user.refresh_from_db()
        self.assertTrue(user.check_password(data['new_password']))