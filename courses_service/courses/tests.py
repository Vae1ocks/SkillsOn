from unicodedata import category

from rest_framework.test import APITestCase, override_settings
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from .models import (
    Category,
    Course,
    Lesson,
    Text,
    Image,
    File,
    URL,
    CourseComment,
    LessonComment,
)
from . import serializers
from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import responses


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication"
        )
    }
)
class TestCourses(APITestCase):
    def category_create(self, title="TestCategory"):
        return Category.objects.create(title=title, slug=slugify(title))

    def course_create(
        self,
        category,
        author=1,
        title="TestCourse",
        price=Decimal(0),
        description="Test desc for course",
        draft=False,
        moderated=True,
        students=[],
    ):
        return Course.objects.create(
            author=author,
            title=title,
            category=category,
            slug=slugify(title),
            price=price,
            description=description,
            draft=draft,
            moderated=moderated,
            students=students,
        )

    def setup(self, author=1, cat_title="TestCategory", course_title="TestCourse"):
        category = self.category_create(title=cat_title)
        course = self.course_create(
            category=category, author=author, title=course_title
        )
        return course

    def create_user(
        self,
        username="test_user",
        email="test@test.com",
        password="testpassword",
        first_name="Test",
        last_name="User",
    ):
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        return User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
        )

    @responses.activate
    def test_courses_overview(self):
        user = self.create_user()
        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)
        category1 = self.category_create(title="1st cat")
        category2 = self.category_create(title="2nd cat")
        category3 = self.category_create(title="3rd cat")

        responses.add(
            responses.GET,
            f"http://testserver/users/user/{user.id}/personal-preferences/",
            json=[
                {"id": category3.id, "title": category3.title},
                {"id": category2.id, "title": category2.title},
            ],
        )

        course1 = self.course_create(category=category1, students=[])
        course2 = self.course_create(
            title="TestCourse2",
            category=category2,
            price=Decimal(100),
            students=[1, 2, 3, 4, 5],
        )
        course3 = self.course_create(
            title="TestCourse3", category=category3, price=Decimal(100), students=[1, 2]
        )

        url = reverse("courses:overview")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 4)
        self.assertEqual(
            data["most_popular"][0], serializers.CourseSerializer(course2).data
        )
        self.assertIn(category1.title, data)
        self.assertIn(category2.title, data)
        self.assertIn(category3.title, data)
        self.assertEqual(data[category1.title], [])
        self.assertEqual(data[category2.title], [])
        self.assertEqual(data[category3.title], [])

    def test_user_courses_list(self):
        user = self.create_user()
        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)
        course = self.setup(author=user.id)
        course.students.append(user.id)
        course.save()
        url = reverse("courses:user_courses_list")

        response = self.client.get(url)
        response.user = user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(
            data[0],
            serializers.UserCourseSerializer(
                course, context={"request": response}
            ).data,
        )
        self.assertTrue(data[0]["is_owner"])

    # def test_courses_list_pagination(self):
    #     user = self.create_user()
    #     is_authenticated = self.client.login(
    #         username=self.username, password=self.password
    #     )
    #     self.assertTrue(is_authenticated)
    #     category = self.category_create()
    #
    #     for i in range(11):
    #         course = self.course_create(category=category, author=user.id)
    #         course.students.append(user.id)
    #         course.save()
    #     url = reverse("courses:user_courses_list")
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     data = response.json()
    #     url = data["next"]
    #     self.assertIsNotNone(url)
    #     self.assertEqual(data["count"], 11)
    #     self.assertIsNone(data["previous"])
    #     self.assertEqual(len(data["results"]), 10)
    #
    #     response = self.client.get(url)
    #     data = response.json()
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(data["count"], 11)
    #     self.assertIsNotNone(data["previous"])
    #     self.assertEqual(len(data["results"]), 1)
    #     self.assertIsNone(data["next"])

    @responses.activate
    def test_course_create(self):
        category = self.category_create()
        user = self.create_user()
        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)

        responses.add(
            responses.GET,
            f"http://testserver/users/user/{user.id}/personal-info/",
            json={
                "first_name": "FirstName",
                "last_name": "LastName",
                "profile_picture": None,
            },
        )

        data = {
            "author": user.id,
            "title": "test_course",
            "category": category.title,
            "description": "some description",
            "draft": True,
            "price": 100,
        }
        url = reverse("courses:course-list")

        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course = Course.objects.first()
        self.assertEqual(
            Category.objects.get(title=data["category"]).id, course.category.id
        )
        self.assertEqual(course.author_name, "FirstName L.")
        self.assertEqual(course.author, data["author"])
        self.assertTrue(course.draft)
        self.assertFalse(course.moderated)

    def test_course_detail(self):
        course = self.setup()
        url = reverse("courses:course_detail", args=(course.slug, course.id))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(), serializers.CourseDetailSerializer(course).data
        )

    def test_course_partial_update(self):
        user = self.create_user()
        course = self.setup(author=user.id)

        is_authenticated = self.client.login(
            username=self.username, email="test@test.com", password=self.password
        )
        self.assertTrue(is_authenticated)

        url = reverse("courses:course_detail", args=(course.slug, course.id))
        data = {"title": "12345"}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        course = Course.objects.get(title=data["title"])
        response = self.client.get(url)
        self.assertEqual(
            response.json(), serializers.CourseDetailSerializer(course).data
        )

    def test_course_delete(self):
        user = self.create_user()
        course = self.setup(author=user.id)

        is_authenticated = self.client.login(
            username=self.username, email="test@test.com", password=self.password
        )
        self.assertTrue(is_authenticated)

        url = reverse("courses:course_detail", args=(course.slug, course.id))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.exists())

    @responses.activate
    def test_courses_search(self):
        user = self.create_user()
        self.client.login(username=self.username, password=self.password)
        category = self.category_create(title="Category")
        category1 = self.category_create(title="1st cat")
        category2 = self.category_create(title="2nd cat")
        category3 = self.category_create(title="3rd cat")
        course1 = self.course_create(category=category, title="First course")
        course2 = self.course_create(category=category1, title="Almost first course")
        course3 = self.course_create(category=category2, title="Third course")
        course4 = self.course_create(category=category2, title="Fourth course")
        course5 = self.course_create(category=category3, title="Fifth course")

        url = reverse("courses:course-list")
        response = self.client.get(
            url,
            data={
                "title": "FIRST",
                "category": f"{category1.title.upper()}, {category.title}",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data[0], serializers.CourseSerializer(course1).data)
        self.assertEqual(data[1], serializers.CourseSerializer(course2).data)

    @responses.activate
    def test_course_comment_create(self):
        user = self.create_user()
        course = self.setup(author=user.id)

        responses.add(
            responses.GET,
            f"http://testserver/users/user/{user.id}/personal-info/",
            json={
                "first_name": "FirstName",
                "last_name": "LastName",
                "profile_picture": None,
            },
        )

        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)

        data = {"body": "course comment", "course": course.id, "rating": 5}
        url = reverse("courses:course_comment_create", args=(course.slug, course.id))

        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = CourseComment.objects.first()
        self.assertEqual(comment.body, data["body"])
        self.assertEqual(comment.author, user.id)
        self.assertEqual(comment.course, Course.objects.get(id=data["course"]))
        course.refresh_from_db()
        self.assertEqual(course.rating, 5)

    def test_course_comment_update(self):
        user = self.create_user()
        course = self.setup(author=user.id)
        course2 = self.setup(cat_title="New category", course_title="Scnd course")
        comment = CourseComment.objects.create(
            author=user.id, body="comment", rating=5, course=course
        )

        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)

        course.refresh_from_db()
        self.assertEqual(course.rating, 5)

        data = {"body": "new body", "course": course2.pk, "rating": 1}
        url = reverse("courses:course_comment_update", args=(comment.id,))

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = CourseComment.objects.first()
        course.refresh_from_db()
        self.assertEqual(course.rating, 1)
        self.assertEqual(comment.course, course)
        self.assertEqual(comment.body, data["body"])

    def test_course_partial_update(self):
        user = self.create_user()
        course = self.setup(author=user.id)
        comment = CourseComment.objects.create(
            author=user.id, body="comment", rating=5, course=course
        )

        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)

        data = {"body": "new body"}
        url = reverse("courses:course_comment_update", args=(comment.id,))

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = CourseComment.objects.first()
        self.assertEqual(comment.course, course)
        self.assertEqual(comment.body, data["body"])

    def test_course_comment_destroy(self):
        user = self.create_user()
        course = self.setup(author=user.id)
        comment = CourseComment.objects.create(
            author=user.id, body="comment", rating=5, course=course
        )

        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)

        url = reverse("courses:course_comment_delete", args=(comment.id,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseComment.objects.exists())

    def create_lesson(self):
        user = self.create_user()
        self.user = user
        course = self.setup(author=user.id)
        self.client.login(
            username=self.username, email="test@test.com", password=self.password
        )

        data = {
            "course": course.id,
            "title": "Test Lesson",
            "contents": [
                {
                    "content_type": "text",
                    "item": {
                        "body": "Test text",
                    },
                },
                {"content_type": "image", "item": {"image": "/path/to/test_image.jpg"}},
                {"content_type": "file", "item": {"file": "/path/to/test_file.pdf"}},
                {"content_type": "url", "item": {"url": "http://example.com/test_url"}},
            ],
        }
        url = reverse("courses:lesson_create")
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return course, data

    def test_lesson_create(self):
        course, data = self.create_lesson()

        self.client.login(
            username=self.username, email="test@test.com", password=self.password
        )
        url = reverse("courses:course_detail", args=(course.slug, course.id))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lessons_data = response.json()["lessons"]
        self.assertIsNotNone(lessons_data)
        for lesson_data in lessons_data:
            self.assertEqual(lesson_data["course"], data["course"])
            self.assertEqual(lesson_data["title"], data["title"])
            for content, exp_content in zip(lesson_data["contents"], data["contents"]):
                self.assertEqual(content["content_type"], exp_content["content_type"])
                for key in exp_content["item"]:
                    if "/courses/media/" in content["item_data"][key]:
                        self.assertEqual(
                            content["item_data"][key][len("/courses/media") :],
                            exp_content["item"][key],
                        )
                    else:
                        self.assertEqual(
                            content["item_data"][key], exp_content["item"][key]
                        )

        url = reverse("courses:course_detail", args=(course.slug, course.id))

        response = self.client.get(url)

    def test_lesson_update(self):
        course, data = self.create_lesson()
        data["title"] = "New Test Title"
        data["contents"] = [
            {"content_type": "text", "item": {"body": "Test text", "id": 1}},
            {"content_type": "text", "item": {"body": "Test text num 2"}},
            {"content_type": "image", "item": {"image": "/new_path/to/test_image"}},
            {"content_type": "file", "item": {"file": "/new_path/to/test_file"}},
            {
                "content_type": "url",
                "item": {"url": "http://example.com:8000/new_test_url"},
            },
        ]
        lesson = Lesson.objects.latest("id")
        url = reverse("courses:lesson_detail_views", args=(lesson.slug, lesson.id))

        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        r_data = response.json()
        self.assertEqual(r_data["course"], course.id)
        self.assertEqual(r_data["title"], data["title"])
        contents = r_data["contents"]

        for content, exp_content in zip(contents, data["contents"]):
            self.assertEqual(content["content_type"], exp_content["content_type"])
            for key in exp_content["item"]:
                if not isinstance(content["item_data"][key], (int, float, complex)):
                    if "/courses/media/" in content["item_data"][key]:
                        self.assertEqual(
                            content["item_data"][key][len("/courses/media/") - 1 :],
                            exp_content["item"][key],
                        )
                    else:
                        self.assertEqual(
                            content["item_data"][key], exp_content["item"][key]
                        )
                else:
                    self.assertEqual(
                        content["item_data"][key], exp_content["item"][key]
                    )

    @responses.activate
    def test_lesson_comment_create(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()

        responses.add(
            responses.GET,
            f"http://testserver/users/user/{self.user.id}/personal-info/",
            json={
                "first_name": "FirstName",
                "last_name": "LastName",
                "profile_picture": None,
            },
        )

        self.client.login(
            username=self.username, email="test@test.com", password=self.password
        )
        url = reverse("courses:lesson_comment_create", args=(lesson.slug, lesson.id))

        data = {"body": "lesson comment", "lesson": lesson.pk}
        url = reverse("courses:lesson_comment_create", args=(lesson.slug, lesson.id))

        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = LessonComment.objects.first()
        self.assertEqual(comment.body, data["body"])
        self.assertEqual(comment.author, self.user.id)
        self.assertEqual(comment.lesson, Lesson.objects.get(id=data["lesson"]))

    def test_lesson_comment_update(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()
        comment = LessonComment.objects.create(
            author=self.user.id, body="comment", lesson=lesson
        )

        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)

        data = {"body": "new body", "lesson": lesson.pk}
        url = reverse("courses:lesson_comment_update", args=(comment.id,))

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = LessonComment.objects.first()
        self.assertEqual(comment.lesson, lesson)
        self.assertEqual(comment.body, data["body"])

    def test_lesson_comment_partial_update(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()
        comment = LessonComment.objects.create(
            author=self.user.id, body="comment", lesson=lesson
        )

        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)

        data = {"body": "new body"}
        url = reverse("courses:lesson_comment_update", args=(comment.id,))

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = LessonComment.objects.first()
        self.assertEqual(comment.lesson, lesson)
        self.assertEqual(comment.body, data["body"])

    def test_lesson_comment_destroy(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()
        comment = LessonComment.objects.create(
            author=self.user.id, body="comment", lesson=lesson
        )

        is_authenticated = self.client.login(
            username=self.username, password=self.password
        )
        self.assertTrue(is_authenticated)

        url = reverse("courses:lesson_comment_delete", args=(comment.id,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LessonComment.objects.exists())

    def test_lesson_reply_comment_create(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()
        comment = LessonComment.objects.create(
            author=self.user.id, body="comment", lesson=lesson
        )
        reply_comment = LessonComment.objects.create(
            author=self.user.id,
            body="reply_to_comment",
            lesson=lesson,
            reply_to=comment,
        )
        lesson_serializer = serializers.LessonSerializer(lesson).data
        comment_serializer = serializers.LessonCommentSerializer(comment).data

        self.assertEqual(len(lesson_serializer["comments"]), 1)
        self.assertEqual(lesson_serializer["comments"][0]["id"], comment.id)

        self.assertEqual(len(comment_serializer["reply_comments"]), 1)
        self.assertEqual(
            comment_serializer["reply_comments"][0]["id"], reply_comment.id
        )

    @responses.activate
    def test_lesson_reply_comment_view_create(self):
        course, data = self.create_lesson()
        lesson = Lesson.objects.first()
        comment = LessonComment.objects.create(
            author=self.user.id, body="comment", lesson=lesson
        )

        responses.add(
            responses.GET,
            f"http://testserver/users/user/{self.user.id}/personal-info/",
            json={
                "first_name": "FirstName",
                "last_name": "LastName",
                "profile_picture": None,
            },
        )

        self.client.login(
            username=self.username, email="test@test.com", password=self.password
        )
        url = reverse("courses:lesson_comment_create", args=(lesson.slug, lesson.id))

        data = {
            "body": "lesson reply comment",
            "lesson": lesson.pk,
            "reply_to": comment.id,
        }
        url = reverse("courses:lesson_comment_create", args=(lesson.slug, lesson.id))

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reply_comment = LessonComment.objects.latest("id")
        r_serializer = serializers.LessonCommentSerializer(reply_comment).data
        comment.refresh_from_db()
        c_serializer = serializers.LessonCommentSerializer(comment).data
        self.assertEqual(len(c_serializer["reply_comments"]), 1)
        self.assertEqual(c_serializer["reply_comments"][0]["id"], reply_comment.id)
        self.assertIsNone(r_serializer["reply_comments"])
