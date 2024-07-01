from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if obj.__class__.__name__ == 'Lesson':
                course = obj.course
                return course.author == request.user.email
            return obj.author == request.user.email
        return False
    

class IsStudent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.__class__.__name__ == 'Course':
            return obj.is_student(request.user.email)
        if obj.__class__.__name__ == 'Lesson':
            course = obj.course
            return course.is_student(request.user.email)
        return False
        

class IsAuthorOrStudent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if obj.__class__.__name__ == 'Lesson':
                course = obj.course
                if course.author == request.user.email:
                    return True
            if obj.author == request.user.email:
                return True
            if request.method in permissions.SAFE_METHODS:
                if obj.__class__.__name__ == 'Course':
                    return obj.is_student(request.user.email)
                if obj.__class__.__name__ == 'Lesson':
                    course = obj.course
                    return course.is_student(request.user.email)
            return False
        return False