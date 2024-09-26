from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = "courses"

router = DefaultRouter()
router.register(r"", views.CourseViewSet, basename="course")


urlpatterns = [
    path("category-list/", views.CategoryListView.as_view(), name="categories_list"),
    path("validate_user_preferences/", views.ValidateUserPreferencesView.as_view()),
    path("overview/", views.CourseOverviewList.as_view(), name="overview"),
    path("", include(router.urls)),
    path(
        "user-courses/list/",
        views.UserCourseListView.as_view(),
        name="user_courses_list",
    ),
    path(
        "<slug:slug>/<int:pk>/",
        views.CourseViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="course_detail",
    ),
    path(
        "<slug:slug>/<int:pk>/comment/create/",
        views.CourseCommentCreateView.as_view(),
        name="course_comment_create",
    ),
    path(
        "course-comment/<int:pk>/update/",
        views.CourseCommentUpdateView.as_view(),
        name="course_comment_update",
    ),
    path(
        "course-comment/<int:pk>/delete/",
        views.CourseCommentDestroyView.as_view(),
        name="course_comment_delete",
    ),
    path("lesson/create/", views.LessonCreateView.as_view(), name="lesson_create"),
    path(
        "lesson/<slug:slug>/<int:pk>/",
        views.LessonViews.as_view(),
        name="lesson_detail_views",
    ),
    path(
        "lesson/<slug:slug>/<int:pk>/comment/create/",
        views.LessonCommentCreateView.as_view(),
        name="lesson_comment_create",
    ),
    path(
        "lesson-comment/<int:pk>/update/",
        views.LessonCommentUpdateView.as_view(),
        name="lesson_comment_update",
    ),
    path(
        "lesson-comment/<int:pk>/delete/",
        views.LessonCommentDestroyView.as_view(),
        name="lesson_comment_delete",
    ),
]
