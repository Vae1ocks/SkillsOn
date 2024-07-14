from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import Chat, Message
from decimal import Decimal
import json


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
    '''
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
    '''
    def test_chat_create(self):
        user = self.user_create()
        user2 = self.user_create(email='testemail@test.com')
        self.client.login(username=self.email, password=self.password)
        url = reverse('users:chat_list')
        data = {'users': [user.id, user2.id]}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_chat_list(self):
        user = self.user_create()
        user2 = self.user_create(email='testemail@test.com')
        self.client.login(username=self.email, password=self.password)
        url = reverse('users:chat_list')
        chat = Chat.objects.create()
        chat.users.set([user, user2])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        users_detail = content[0]['user_detail']
        self.assertEqual(len(users_detail), 2)
        self.assertEqual(users_detail[0]['id'], user.id)
        self.assertEqual(users_detail[1]['id'], user2.id)
        self.assertEqual(users_detail[0]['first_name'], user.first_name)
        self.assertEqual(users_detail[1]['first_name'], user2.first_name)
        self.assertEqual(users_detail[0]['last_name'], user.last_name)
        self.assertEqual(users_detail[1]['last_name'], user2.last_name)
        self.assertEqual(users_detail[0]['profile_picture'], user.profile_picture)
        self.assertEqual(users_detail[1]['profile_picture'], user2.profile_picture)

    def test_chat_retrieve(self):
        user = self.user_create()
        user2 = self.user_create(email='testemail@test.com')
        self.client.login(username=self.email, password=self.password)
        chat = Chat.objects.create()
        url = reverse('users:chat_retrieve', args=(chat.id, ))
        chat.users.set([user, user2])
        message = Message.objects.create(author=user, text='dddddd', chat=chat)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        self.assertIn('messages', content)
        self.assertEqual(content['messages'][0]['text'], message.text)
        self.assertEqual(content['messages'][0]['author'], message.author.id)
        self.assertEqual(content['messages'][0]['chat'], message.chat.id)

    def test_user_list(self):
        user = self.user_create()
        user2 = self.user_create(email='testemail@test.com')
        self.client.login(username=self.email, password=self.password)
        url = reverse('users:user_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)
        fields = ['id', 'first_name', 'last_name', 'profile_picture']
        for field in fields:
            self.assertIn(field, content[0])

    def test_user_detail(self):
        user = self.user_create()
        self.client.login(username=self.email, password=self.password)
        url = reverse('users:user_detail', args=[user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        fields = ['first_name', 'last_name',
                  'profile_picture', 'about_self', 'categories_liked',
                  'payouts', 'balance']
        for field in fields:
            self.assertIn(field, content)
        self.assertEqual(Decimal(content['balance']), 0)
        