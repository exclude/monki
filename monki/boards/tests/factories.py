import factory

from monki.boards import models as m


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')

    class Meta:
        model = m.Category
        django_get_or_create = ('name',)


class BoardFactory(factory.django.DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    name = factory.Faker('name')

    class Meta:
        model = m.Board
        django_get_or_create = ('directory',)

    @factory.lazy_attribute
    def directory(self):
        name = factory.Faker('pystr', max_chars=8).generate(extra_kwargs={})

        return name.lower()


class PostFactory(factory.django.DjangoModelFactory):
    board = factory.SubFactory(BoardFactory)

    ip_address = factory.Faker('ipv4')
    user_agent = factory.Faker('user_agent')
    cid = factory.Faker('pystr', max_chars=12)

    class Meta:
        model = m.Post


class ReplyFactory(PostFactory):
    parent = factory.SubFactory(PostFactory)
