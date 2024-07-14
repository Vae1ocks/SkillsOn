from rest_framework.test import APITestCase, override_settings
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from .models import Category, Course, Lesson, Text, Image, File, URL, CourseComment, LessonComment
from . import serializers
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.contrib.auth import get_user_model


def category_create(title='TestCategory'):
    return Category.objects.create(title=title, slug=slugify(title))


def course_create(category, author=1,
                  title='TestCourse',
                  price=Decimal(0), description='Test desc for course',
                  draft=False, moderated=True, students=[]):
    
    return Course.objects.create(author=author, title=title, category=category,
                                 slug=slugify(title), price=price, description=description,
                                 draft=draft,moderated=moderated, students=students)


def setup(author=1, cat_title='TestCategory', course_title='TestCourse'):
    category = category_create(title=cat_title)
    course = course_create(category=category, author=author, title=course_title)
    return course

@override_settings(REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication'
    )
})
class TestCourses(APITestCase):
    
    def create_user(self, username='test_user',
                    email='test@test.com',
                    password='testpassword',
                    first_name='Test',
                    last_name='User'):
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        return User.objects.create_user(username=self.username, email=self.email,
                                        password=self.password, first_name=self.first_name,
                                        last_name=self.last_name)

    def test_courses_list(self):
        category = category_create()
        course1 = course_create(category=category)
        course2 = course_create(title='TestCourse2',
                                category=category, price=Decimal(100), students=[1,2,3,4,5])
        course3 = course_create(title='TestCourse3',
                                category=category, price=Decimal(100), students=[1,2])

        url = reverse('courses:course-list')
        user = get_user_model().objects.create(username='Test', password='tesetsdttw2')
        response = self.client.get(url)
        response.user = user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(response.json()[0], serializers.CourseSerializer(
            course2, context={'request': response}).data)
        self.assertEqual(response.json()[1], serializers.CourseSerializer(
            course3, context={'request': response}).data)
        self.assertEqual(response.json()[2], serializers.CourseSerializer(
            course1, context={'request': response}).data)

    def test_course_create(self):
        category = category_create()
        user = self.create_user()
        is_authenticated = self.client.login(username=self.username, password=self.password)
        self.assertTrue(is_authenticated)

        data = {
            'author': user.id,
            'title' : 'test_course',
            'category': category.title,
            'description': 'some description',
            'draft': True,
            'price': 100
        }
        url = reverse('courses:course-list')

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course = Course.objects.first()
        self.assertEqual(Category.objects.get(title=data['category']).id, course.category.id)
        self.assertEqual(course.author_name, f'{user.first_name} {user.last_name[0]}.')
        self.assertEqual(course.author, data['author'])
        self.assertTrue(course.draft)
        self.assertFalse(course.moderated)


    def test_course_detail(self):
        course = setup()
        url = reverse('courses:course_detail', args=(course.slug, course.id))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serializers.CourseDetailSerializer(course).data)
    
    def test_course_partial_update(self):
        user = self.create_user()
        course = setup(author=user.id)
        
        is_authenticated = self.client.login(username=self.username, email='test@test.com', password=self.password)
        self.assertTrue(is_authenticated)

        url = reverse('courses:course_detail', args=(course.slug, course.id))
        data = {'title': '12345'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        course = Course.objects.get(title=data['title'])
        response = self.client.get(url)
        self.assertEqual(response.json(), serializers.CourseDetailSerializer(course).data)

    def test_course_delete(self):
        user = self.create_user()
        course = setup(author=user.id)
        
        is_authenticated = self.client.login(username=self.username, email='test@test.com', password=self.password)
        self.assertTrue(is_authenticated)

        url = reverse('courses:course_detail', args=(course.slug, course.id))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.exists())

    def test_course_comment_create(self):
        user = self.create_user()
        course = setup(author=user.id)

        is_authenticated = self.client.login(username=self.username, password=self.password)
        self.assertTrue(is_authenticated)

        data = {
            'body': 'course comment',
            'course': 1
        }
        url = reverse('courses:course_comment_create', args=(course.slug, course.id))

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = CourseComment.objects.first()
        self.assertEqual(comment.body, data['body'])
        self.assertEqual(comment.author, user.id)
        self.assertEqual(comment.course, Course.objects.get(id=data['course']))

    def test_course_comment_update(self):
        user = self.create_user()
        course = setup(author=user.id)
        course2 = setup(cat_title='New category', course_title='Scnd course')
        comment = CourseComment.objects.create(author=user.id, body='comment',
                                               course=course)
        
        is_authenticated = self.client.login(username=self.username, password=self.password)
        self.assertTrue(is_authenticated)

        data = {'body': 'new body', 'course': course2.pk}
        url = reverse('courses:course_comment_update', args=(comment.id, ))

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = CourseComment.objects.first()
        self.assertEqual(comment.course, course)
        self.assertEqual(comment.body, data['body'])

    def test_course_partial_update(self):
        user = self.create_user()
        course = setup(author=user.id)
        comment = CourseComment.objects.create(author=user.id, body='comment',
                                               course=course)
        
        is_authenticated = self.client.login(username=self.username, password=self.password)
        self.assertTrue(is_authenticated)

        data = {'body': 'new body'}
        url = reverse('courses:course_comment_update', args=(comment.id, ))

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = CourseComment.objects.first()
        self.assertEqual(comment.course, course)
        self.assertEqual(comment.body, data['body'])

    def test_course_comment_destroy(self):
        user = self.create_user()
        course = setup(author=user.id)
        comment = CourseComment.objects.create(author=user.id, body='comment',
                                               course=course)
        
        is_authenticated = self.client.login(username=self.username, password=self.password)
        self.assertTrue(is_authenticated)

        url = reverse('courses:course_comment_delete', args=(comment.id, ))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseComment.objects.exists())

    def create_lesson(self):
        user = self.create_user()
        self.user = user
        course = setup(author=user.id)
        self.client.login(username=self.username, email='test@test.com', password=self.password)
        
        data = {
            'course': course.id,
            'title': 'Test Lesson',
            'contents': [
                {
                    'content_type': 'text',
                    'item': {
                        'body': 'Test text',
                    }
                },
                {
                    'content_type': 'image',
                    'item': {
                        'image': '/path/to/test_image.jpg'
                    }
                },
                {
                    'content_type': 'file',
                    'item': {
                        'file': '/path/to/test_file.pdf'
                    }
                },
                {
                    'content_type': 'url',
                    'item': {
                        'url': 'http://example.com/test_url'
                    }
                }
            ]
        }
        url = reverse('courses:lesson_create')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return course, data

    def test_lesson_create(self):
        course, data = self.create_lesson()

        self.client.login(username=self.username, email='test@test.com', password=self.password)
        url = reverse('courses:course_detail', args=(course.slug, course.id))
        
        response = self.client.get(url) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lessons_data = response.json()['lessons']
        self.assertIsNotNone(lessons_data)
        for lesson_data in lessons_data:
            self.assertEqual(lesson_data['course'], data['course'])
            self.assertEqual(lesson_data['title'], data['title'])
            for content, exp_content in zip(lesson_data['contents'], data['contents']):
                self.assertEqual(content['content_type'], exp_content['content_type'])
                for key in exp_content['item']:
                    self.assertEqual(content['item_data'][key], exp_content['item'][key])

        url = reverse('courses:course_detail', args=(course.slug, course.id))

        response = self.client.get(url)

    def test_lesson_update(self):
        course, data = self.create_lesson()
        data['title'] = 'New Test Title'
        data['contents'] = [
            {
                'content_type': 'text',
                'item': {
                    'body': 'Test text',
                    'id': 1
                }
            },
            {
                'content_type': 'text',
                'item': {
                    'body': 'Test text num 2'
                }
            },
            {
                'content_type': 'image',
                'item': {
                    'image': '/new_path/to/test_image'
                }
            },
            {
                'content_type': 'file',
                'item': {
                    'file': '/new_path/to/test_file'
                }
            },
            {
                'content_type': 'url',
                'item': {
                    'url': 'http://example.com:8000/new_test_url'
                }
            }
        ]
        lesson = Lesson.objects.latest('id')
        url = reverse('courses:lesson_detail_views', args=(lesson.slug, lesson.id))
        
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        r_data = response.json()
        self.assertEqual(r_data['course'], course.id)
        self.assertEqual(r_data['title'], data['title'])
        contents = r_data['contents']

        for content, exp_content in zip(contents, data['contents']):
            self.assertEqual(content['content_type'], exp_content['content_type'])
            for key in exp_content['item']:
                self.assertEqual(content['item_data'][key], exp_content['item'][key])

    def test_lesson_comment_create(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()

        self.client.login(username=self.username, email='test@test.com', password=self.password)
        url = reverse('courses:lesson_comment_create', args=(lesson.slug, lesson.id))

        data = {
            'body': 'lesson comment',
            'lesson': lesson.pk
        }
        url = reverse('courses:lesson_comment_create', args=(lesson.slug, lesson.id))

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = LessonComment.objects.first()
        self.assertEqual(comment.body, data['body'])
        self.assertEqual(comment.author, self.user.id)
        self.assertEqual(comment.lesson, Lesson.objects.get(id=data['lesson']))

    def test_lesson_comment_update(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()
        comment = LessonComment.objects.create(author=self.user.id, body='comment',
                                               lesson=lesson)
     
        is_authenticated = self.client.login(username=self.username, password=self.password)
        self.assertTrue(is_authenticated)

        data = {
            'body': 'new body',
            'lesson': lesson.pk
            }
        url = reverse('courses:lesson_comment_update', args=(comment.id, ))

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = LessonComment.objects.first()
        self.assertEqual(comment.lesson, lesson)
        self.assertEqual(comment.body, data['body'])

    def test_lesson_comment_partial_update(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()
        comment = LessonComment.objects.create(author=self.user.id, body='comment',
                                               lesson=lesson)
     
        is_authenticated = self.client.login(username=self.username, password=self.password)
        self.assertTrue(is_authenticated)

        data = {'body': 'new body'}
        url = reverse('courses:lesson_comment_update', args=(comment.id, ))

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = LessonComment.objects.first()
        self.assertEqual(comment.lesson, lesson)
        self.assertEqual(comment.body, data['body'])

    def test_lesson_comment_destroy(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()
        comment = LessonComment.objects.create(author=self.user.id, body='comment',
                                               lesson=lesson)
     
        is_authenticated = self.client.login(username=self.username, password=self.password)
        self.assertTrue(is_authenticated)

        url = reverse('courses:lesson_comment_delete', args=(comment.id, ))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LessonComment.objects.exists())