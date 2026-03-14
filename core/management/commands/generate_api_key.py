from django.core.management.base import BaseCommand

from organizations.models import APIKey
from accounts.models import User


class Command(BaseCommand):
    help = 'Generate API key for demo user'

    def handle(self, *args, **options):
        user = User.objects.filter(email='demo@saaspos.com').first()
        if not user:
            self.stdout.write(self.style.ERROR('Demo user not found. Run seed_demo first.'))
            return
        
        if not user.organization:
            self.stdout.write(self.style.ERROR('Demo user has no organization. Run seed_demo first.'))
            return
        
        # Create API key
        api_key, created = APIKey.objects.get_or_create(
            organization=user.organization,
            name='Demo API Key',
            defaults={'is_active': True}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'API key created for {user.organization.name}'))
        else:
            self.stdout.write(f'API key already exists for {user.organization.name}')
        
        self.stdout.write('')
        self.stdout.write('API Key: ' + api_key.key)
        self.stdout.write('')
        self.stdout.write('Use this key in your API requests:')
        self.stdout.write('  Headers: X-API-Key: ' + api_key.key)
        self.stdout.write('')
        self.stdout.write('Example curl command:')
        self.stdout.write(f'''  curl -X POST http://127.0.0.1:8000/api/products/add/ \\
    -H "Content-Type: application/json" \\
    -H "X-API-Key: {api_key.key}" \\
    -d '{{"name": "New Product", "price": 9.99, "category": "Test"}}' ''')
