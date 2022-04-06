import factory
import random
from factory.django import DjangoModelFactory
from django.db.models import signals
from Users.models import User
from Users.models import Role

roles = ['Developer', 'Admin', 'User']
emails = ['gmail.com', 'yahoo.com', 'hotmail.com', 'bing.com']

@factory.django.mute_signals(signals.post_save)
class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role

    assigned_role= random.choice(roles)

    user = factory.SubFactory('app.factories.UserFactory', profile=None)

@factory.django.mute_signals(signals.post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.LazyAttribute(lambda o: o.first_name)
    # email = factory.LazyAttribute(lambda o: '%s@example.com' % o.first_name)
    email = factory.LazyAttribute(lambda o: f'%s@{random.choice(emails)}' % o.first_name)

    profile = factory.RelatedFactory(RoleFactory, factory_related_name='user')


for x in range(0, 20):
    u = UserFactory()