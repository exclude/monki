from django.test import TestCase

from monki.boards.tests import factories
from monki.boards.models import Board, Category


class BoardTestCase(TestCase):

    def test_str(self):
        board = factories.BoardFactory.build(name='Lorem Ipsum', directory='li')

        self.assertEqual(board.__str__(), '/li/ - Lorem Ipsum')

    def test_order(self):
        for i in range(5):
            boards = factories.BoardFactory(order=i)

        boards = Board.objects.all()

        self.assertListEqual([b.order for b in boards], [0, 1, 2, 3, 4])

    def test_get_absolute_url(self):
        board = factories.BoardFactory.build(directory='li')

        self.assertEqual(board.get_absolute_url(), '/board/li/')

    def test_last_post_when_board_is_empty(self):
        empty_board = factories.BoardFactory()

        self.assertIsNone(empty_board.last_post)

    def test_last_post(self):
        post = factories.PostFactory()

        self.assertEqual(post.board.last_post, post.created_at)


class CategoryTestCase(TestCase):

    def test_str(self):
        category = factories.CategoryFactory.build(name='Lorem Ipsum')

        self.assertEqual(category.__str__(), 'Lorem Ipsum')

    def test_order(self):
        for i in range(5):
            factories.CategoryFactory(order=i)

        categories = Category.objects.all()

        self.assertListEqual([c.order for c in categories], [0, 1, 2, 3, 4])


class PostTestCase(TestCase):

    def test_str(self):
        post = factories.PostFactory.build(pk=1)

        self.assertEqual(post.__str__(), 'No. 1')
