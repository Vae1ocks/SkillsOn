from rest_framework import serializers
from django.utils.text import slugify
from unidecode import unidecode
from django.apps import apps
from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['title']


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
        fields = ['id', 'author_name', 'body', 'created', 'lesson']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['author'] = user.id
        validated_data['author_name'] = f'{user.first_name} {user.last_name[0]}.'
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('lesson', None)
        return super().update(instance, validated_data)


class LessonSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)
    comments = LessonCommentSerializer(many=True, read_only=True)

    class Meta:
        model = models.Lesson
        fields = ['course', 'title', 'draft', 'contents', 'comments']

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
        fields = ['id', 'body', 'created', 'course']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['author'] = user.id
        validated_data['author_name'] = f'{user.first_name} {user.last_name[0]}.'
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('course', None)
        return super().update(instance, validated_data)


class CourseSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = models.Course
        fields = ['title', 'author', 'author_name', 'category', 'price',
                  'students_count']
        
    def get_students_count(self, obj):
        return len(obj.students)


class CourseDetailSerializer(serializers.ModelSerializer):
    students_count = serializers.SerializerMethodField()
    comments = CourseCommentSerializer(many=True, read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = models.Course
        fields = ['id', 'title', 'author', 'author_name', 'price', 'students_count',
                  'description', 'created', 'lessons', 'comments']

    def get_students_count(self, obj):
        return len(obj.students)
    

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['author', 'title', 'category', 'description',
                  'draft', 'moderated', 'price']
        
    def create(self, validated_data):
        slug = slugify(unidecode(validated_data['title']))
        user = self.context.get('request').user
        author_name = f'{user.first_name} {user.last_name[0]}.'
        return models.Course.objects.create(**validated_data, slug=slug,
                                            author_name=author_name)