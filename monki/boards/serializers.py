from rest_framework import serializers

from monki.boards.models import (
    Board,
    Category,
    Image,
    Post,
    Video,
)


class FileSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField()

    class Meta:
        fields = [
            'original_filename',
            'heigth',
            'width',
            'size',
            'file',
            'thumbnail',
        ]


class ImageSerializer(FileSerializer):
    thumbnail = serializers.ImageField()

    class Meta(FileSerializer.Meta):
        model = Image


class VideoSerializer(FileSerializer):
    thumbnail = serializers.ImageField()

    class Meta(FileSerializer.Meta):
        model = Video
        fields = FileSerializer.Meta.fields + ['image',]


class FileObjectRelatedField(serializers.RelatedField):

    def to_representation(self, obj):
        if isinstance(obj, Image):
            serializer = ImageSerializer(obj)
        elif isinstance(obj, Video):
            serializer = VideoSerializer(obj)
        else:
            raise TypeError('Unexpected type of file object')

        return serializer.data


class BoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = [
            'directory',
            'name',
            'last_post',
        ]


class CategorySerializer(serializers.ModelSerializer):
    boards = BoardSerializer(many=True)

    class Meta:
        model = Category
        fields = [
            'name',
            'boards',
        ]


class PostSerializer(serializers.ModelSerializer):
    parent = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='post-detail',
    )

    file = FileObjectRelatedField(
        read_only=True,
        source='content_object'
    )

    message = serializers.ReadOnlyField(
        source='message_html',
    )

    class Meta:
        model = Post
        fields = [
            'pk',
            'name',
            'tripcode',
            'subject',
            'message',
            'stickied',
            'locked',
            'created_at',
            'bumped_at',
            'board',
            'parent',
            'file'
        ]


class ThreadListSerializer(serializers.ListSerializer):

    def to_representation(self, data):

        return super().to_representation(data)


class ThreadSerializer(serializers.ModelSerializer):
    file = FileObjectRelatedField(
        read_only=True,
        source='content_object'
    )

    replies = PostSerializer(many=True)

    message = serializers.ReadOnlyField(
        source='message_html',
    )

    class Meta:
        model = Post
        list_serializer_class = ThreadListSerializer
        fields = [
            'pk',
            'name',
            'tripcode',
            'subject',
            'message',
            'stickied',
            'locked',
            'created_at',
            'bumped_at',
            'board',
            'parent',
            'file',
            'replies',
        ]
