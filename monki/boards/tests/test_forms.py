from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from monki.boards.forms import PostForm

from . import factories


class PostFormTestCase(TestCase):

    def setUp(self):
        self.board = factories.BoardFactory()
        self.thread = factories.PostFactory()

    def test_file_should_be_required_for_new_thread(self):
        form = PostForm(data={
            'board': self.board.pk
        })

        self.assertFalse(form.is_valid())
        self.assertIn('New thread requires a file.', form.errors['__all__'])

    def test_file_or_message_should_be_required_for_reply(self):
        form = PostForm(data={
            'board': self.board.pk,
            'parent': self.thread.pk,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('You should provide at least a file or a message.', form.errors['__all__'])

    def test_should_be_able_to_create_threads_with_jpeg(self):
        form = PostForm(
            data={
                'board': self.board.pk,
            },
            files={
                'file': SimpleUploadedFile('test.jpg', b'content', 'image/jpeg')
            }
        )

        self.assertTrue(form.is_valid())

    def test_should_be_able_to_create_threads_with_png(self):
        form = PostForm(
            data={
                'board': self.board.pk,
            },
            files={
                'file': SimpleUploadedFile('test.png', b'content', 'image/png')
            }
        )

        self.assertTrue(form.is_valid())

        def test_should_be_able_to_create_threads_with_gif(self):
            form = PostForm(
                data={
                    'board': self.board.pk,
                },
                files={
                    'file': SimpleUploadedFile('test.gif', b'content', 'image/gif')
                }
            )

            self.assertTrue(form.is_valid())

    def test_should_be_able_to_create_threads_with_mp4(self):
        form = PostForm(
            data={
                'board': self.board.pk,
            },
            files={
                'file': SimpleUploadedFile('test.mp4', b'content', 'video/mp4')
            }
        )

        self.assertTrue(form.is_valid())

    def test_should_be_able_to_create_threads_with_webm(self):
        form = PostForm(
            data={
                'board': self.board.pk,
            },
            files={
                'file': SimpleUploadedFile('test.webm', b'content', 'video/webm')
            }
        )

        self.assertTrue(form.is_valid())

    def test_should_not_be_able_to_create_threads_with_unknow_file_type(self):
        form = PostForm(
            data={
                'board': self.board.pk,
            },
            files={
                'file': SimpleUploadedFile('test.py', b'content', 'text/x-python')
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('text/x-python is not a valid file.', form.errors['file'])

    def test_should_be_able_to_reply_threads(self):
        form = PostForm(data={
            'board': self.board.pk,
            'parent': self.thread.pk,
            'message': 'Lorem Ipsum',
        })

        self.assertTrue(form.is_valid())
