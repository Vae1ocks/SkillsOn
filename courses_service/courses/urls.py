from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # path('list/', views.CoursesTitleOnlyListView.as_view(), name='courses_titles_list'),
    path('category-list/', views.CategoryListView.as_view(), name='categories_list'),
    path('list', views.CoursesListView.as_view(), name='courses_list'),
    path('<int:pk>', views.CourseDetailView.as_view(), name='course_detail'),
]