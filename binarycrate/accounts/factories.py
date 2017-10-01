import factory


class UserFactory(factory.django.DjangoModelFactory):

    email = factory.Sequence(lambda n: '{}@users.example.com'.format(n))

    class Meta(object):
        django_get_or_create = ['email']
        model = 'accounts.User'
