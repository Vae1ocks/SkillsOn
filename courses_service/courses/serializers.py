from rest_framework import serializers
from django.utils.text import slugify
from unidecode import unidecode
from django.apps import apps
from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'title']


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Text
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = '__all__'


class URLSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.URL
        fields = '__all__'


class ContentSerializer(serializers.ModelSerializer):
    item = serializers.JSONField(write_only=True)
    item_data = serializers.SerializerMethodField(read_only=True)
    content_type = serializers.SlugRelatedField(
        queryset=models.ContentType.objects.all(),
        slug_field='model',
    )

    class Meta:
        model = models.Content
        fields = ['content_type', 'item', 'item_data']

    def get_item_data(self, obj):
        if obj.content_type.model == 'text':
            return TextSerializer(obj.item).data
        if obj.content_type.model == 'image':
            return ImageSerializer(obj.item).data
        if obj.content_type.model == 'file':
            return FileSerializer(obj.item).data
        if obj.content_type.model == 'url':
            return URLSerializer(obj.item).data
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation
    
    def to_internal_value(self, data):
        content_type = data.get('content_type')
        item_data = data.get('item')

        if not item_data:
            raise serializers.ValidationError("Item data is required.")
        
        item_id = item_data.get('id')

        item = None
        
        if content_type == 'text':
            if item_id:
                item = models.Text.objects.filter(id=item_id).first()
                if item:
                    for attr, value in item_data.items():
                        setattr(item, attr, value)    
                    item.save()
                else:
                    item = models.Text.objects.create(**item_data)
            else:
                item = models.Text.objects.create(**item_data)

        elif content_type == 'image':
            if item_id:
                item = models.Image.objects.filter(id=item_id).first()
                if item:
                    for attr, value in item_data.items():
                        setattr(item, attr, value)
                    item.save()
                else:
                    item = models.Image.objects.create(**item_data)
            else:
                item = models.Image.objects.create(**item_data)

        elif content_type == 'file':
            if item_id:
                item = models.File.objects.filter(id=item_id).first()
                if item:
                    for attr, value in item_data.items():
                        setattr(item, attr, value)
                    item.save()
                else:
                    item = models.File.objects.create(**item_data)
            else:
                item = models.File.objects.create(**item_data)
        elif content_type == 'url':
            if item_id:
                item = models.URL.objects.filter(id=item_id).first()
                if item:
                    for attr, value in item_data.items():
                        setattr(item, attr, value)
                    item.save()
                else:
                    item = models.URL.objects.create(**item_data)
            else:
                item = models.URL.objects.create(**item_data)
        else:
            raise serializers.ValidationError("Invalid content type.")
        
        content_type_model = models.ContentType.objects.get(model=content_type)
        validated_data = {
            'content_type': content_type_model,
            'obj_id': item.id,
        }
        return validated_data

    def create(self, validated_data, lesson):
        content = models.Content.objects.create(**validated_data, lesson=lesson)
        return content

    def update(self, instance, validated_data):
        content_type = validated_data.get('content_type')
        item_data = validated_data.get('item')

        if content_type and item_data:
            if content_type.model == 'text':
                models.Text.objects.filter(id=instance.obj_id).update(**item_data)
            elif content_type.model == 'image':
                models.Image.objects.filter(id=instance.obj_id).update(**item_data)
            elif content_type.model == 'file':
                models.File.objects.filter(id=instance.obj_id).update(**item_data)
            elif content_type.model == 'url':
                models.URL.objects.filter(id=instance.obj_id).update(**item_data)
        
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


class LessonCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LessonComment
        fields = ['id', 'author_name', 'author_image', 'body', 'created', 'lesson']

    def create(self, validated_data):
        request = self.context.get('request')
        first_name = self.context.get('first_name')
        last_name = self.context.get('last_name')
        author_image = self.context.get('author_image')
        user = request.user
        validated_data['author'] = user.id
        validated_data['author_name'] = f'{first_name} {last_name[0]}.'
        validated_data['author_image'] = author_image
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('lesson', None)
        return super().update(instance, validated_data)


class LessonSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)
    comments = LessonCommentSerializer(many=True, read_only=True)
    user_seen = serializers.SerializerMethodField()

    class Meta:
        model = models.Lesson
        fields = ['course', 'title', 'draft', 'contents', 'comments', 'user_seen']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('called_from_course') is not True:
            self.fields.pop('user_seen')
    
    def get_user_seen(self, obj):
        request = self.context.get('request')
        if request and request.user.id in obj.users_seen:
            return True
        return False
    
    def create(self, validated_data):
        contents_data = validated_data.pop('contents')
        slug = slugify(unidecode(validated_data.get('title')))
        lesson = models.Lesson.objects.create(**validated_data, slug=slug)
        for content_data in contents_data:
            ContentSerializer.create(ContentSerializer(), validated_data=content_data, lesson=lesson)
        return lesson

    def update(self, instance, validated_data):
        contents_data = validated_data.pop('contents', [])
        instance = super().update(instance, validated_data)

        obj_ids = [(content_data['obj_id'], content_data['content_type'])
                       for content_data in contents_data
                       if content_data.get('obj_id')]

        '''
        если пользователь не передал нам в contents_data id какого-то объекта content,
        который уже связан с instance, следовательно, он его стёр в режиме
        редактирования --> нужно удалить данный content_obj
        '''
        for content in instance.contents.all():
            if (content.obj_id, content.content_type) not in obj_ids:
                content.delete()

        for content_data in contents_data:
            obj_id = content_data.get('obj_id')
            content_type = content_data.get('content_type')
            if obj_id:
                content_obj = models.Content.objects.filter(lesson=instance, obj_id=obj_id,
                                                         content_type=content_type).first()
                if content_obj:
                    ContentSerializer.update(ContentSerializer(), instance=content_obj,
                                            validated_data=content_data)
                else:
                    ContentSerializer.create(ContentSerializer(), validated_data=content_data, lesson=instance)
            else:
                ContentSerializer.create(ContentSerializer(), validated_data=content_data, lesson=instance)
        return instance


class CourseCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseComment
        fields = ['id', 'author_name', 'author_image', 'rating', 'body', 'created', 'course']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        first_name = self.context.get('first_name')
        last_name = self.context.get('last_name')
        author_image = self.context.get('author_image')
        validated_data['author'] = user.id
        validated_data['author_name'] = f'{first_name} {last_name[0]}.'
        validated_data['author_image'] = author_image
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('course', None)
        return super().update(instance, validated_data)
    
    def validate_rating(self, value):
        if self.instance:
            if value is None:
                return self.instance.rating
            return value
        else:
            if value is None:
                raise serializers.ValidationError('Рейтинг не предоставлен')
            return value


class CourseSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = models.Course
        fields = ['id', 'title', 'level', 'author', 'author_name', 'author_image',
                  'category', 'price', 'students_count']
    
    def get_students_count(self, obj):
        return len(obj.students)
    

class UserCourseSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()
    lessons_seen = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'title', 'author', 'author_name', 'author_image', 'category',
                  'price', 'level', 'students_count', 'lessons_seen', 'is_owner']
        
    def get_lessons_seen(self, obj):
        lessons_seen = 0
        all_lessons = obj.lessons.count()
        user_id = self.context['request'].user.id
        if user_id not in obj.students or user_id == obj.author:
            return 'N/A'
        if all_lessons == 0:
            return '0%'
        for lesson in obj.lessons.all():
            if user_id in lesson.users_seen:
                lessons_seen += 1
        return f'{int((lessons_seen / all_lessons) * 100)}%'
    
    def get_students_count(self, obj):
        return len(obj.students)
    
    def get_is_owner(self, obj):
        return True if self.context['request'].user.id == obj.author else False


class CourseDetailSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()
    comments = CourseCommentSerializer(many=True, read_only=True)
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = ['id', 'title', 'author', 'author_name', 'author_image', 'price', 'students_count',
                  'description', 'level', 'created', 'lessons', 'comments']
        
    def get_lessons(self, obj):
        context = self.context.copy()
        context['called_from_course'] = True
        return LessonSerializer(obj.lessons.all(), many=True,
                                context=context, read_only=True).data

    def get_students_count(self, obj):
        return len(obj.students)
    

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['author', 'title', 'category', 'description',
                  'draft', 'moderated', 'price', 'level']
        
    def create(self, validated_data):
        slug = slugify(unidecode(validated_data['title']))
        user = self.context.get('request').user
        first_name = self.context.get('first_name')
        last_name = self.context.get('last_name')
        author_image = self.context.get('author_image')
        author_name = f'{first_name} {last_name[0]}.'
        return models.Course.objects.create(**validated_data, slug=slug,
                                            author_name=author_name, author_image=author_image)