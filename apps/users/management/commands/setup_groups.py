from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates the default user and operations groups with proper permissions'

    def handle(self, *args, **options):
        # Create groups
        user_group, _ = Group.objects.get_or_create(name='user')
        ops_group, _ = Group.objects.get_or_create(name='operations')

        self.stdout.write(self.style.SUCCESS('Groups created/verified: user, operations'))

        # Create a default admin user if none exists
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created: admin / admin123'))

        self.stdout.write(self.style.SUCCESS('Setup complete. Use the register endpoint to create users with roles.'))