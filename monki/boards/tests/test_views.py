from django.test import TestCase, override_settings

from monki.boards.tests import factories


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class BoardViewTestCase(TestCase):

    def setUp(self):
        self.board = factories.BoardFactory(name='TestCase', directory='t')

    def test_should_be_able_to_access_board_index(self):
        response = self.client.get('/board/t/')

        self.assertEqual(response.status_code, 200)

    def test_should_be_able_to_access_thread(self):
        thread = factories.PostFactory(board=self.board)
        response = self.client.get(thread.get_absolute_url())

        self.assertEqual(response.status_code, 200)

    def test_should_be_NOT_able_to_access_a_reply_as_thread(self):
        reply = factories.ReplyFactory(board=self.board)
        response = self.client.get('/board/t/thread/{}/'.format(reply.pk))

        self.assertEqual(response.status_code, 404)
