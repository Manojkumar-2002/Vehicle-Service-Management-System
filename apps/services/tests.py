from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from .models import Component, Vehicle, ServiceOrder, Issue
from .models.payment import Payment
from apps.services.constants.enums import OrderStatus, ServiceType


class BaseTest(TestCase):
    """Base class with common setup for all tests."""

    @classmethod
    def setUpTestData(cls):
        # Create groups
        cls.user_group, _ = Group.objects.get_or_create(name='user')
        cls.ops_group, _ = Group.objects.get_or_create(name='operations')

        # Create users
        cls.regular_user = User.objects.create_user('regular', 'regular@test.com', 'password123')
        cls.regular_user.groups.add(cls.user_group)

        cls.ops_user = User.objects.create_user('ops', 'ops@test.com', 'password123')
        cls.ops_user.groups.add(cls.ops_group)

        # Create a component
        cls.component = Component.objects.create(
            name='Brake Pad',
            repair_price=50.00,
            purchase_price=120.00
        )
        cls.component2 = Component.objects.create(
            name='Oil Filter',
            repair_price=15.00,
            purchase_price=35.00
        )

        # Create a vehicle
        cls.vehicle = Vehicle.objects.create(
            vin='1HGCM82633A004352',
            make='Honda',
            model='Civic',
            owner_name='John Doe',
            contact_number='1234567890'
        )

    def setUp(self):
        self.client = APIClient()

    def _get_token(self, username='regular', password='password123'):
        """Helper to get JWT token for a user."""
        resp = self.client.post('/api/auth/login/', {
            'username': username,
            'password': password
        }, format='json')
        return resp.data.get('data', {}).get('access') or resp.data.get('access')

    def _auth_client(self, username='regular'):
        """Authenticate the client with JWT."""
        token = self._get_token(username)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


# ── Auth Tests ──────────────────────────────────────────────────────────────

class AuthTests(BaseTest):

    def test_register_user(self):
        """Users can register with a role."""
        resp = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'StrongPass1!',
            'password2': 'StrongPass1!',
            'role': 'user'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data['success'])
        self.assertIn('access', resp.data['data'])
        self.assertIn('refresh', resp.data['data'])
        # Verify user was added to the correct group
        user = User.objects.get(username='newuser')
        self.assertTrue(user.groups.filter(name='user').exists())

    def test_register_operations(self):
        """Users can register with operations role."""
        resp = self.client.post('/api/auth/register/', {
            'username': 'newops',
            'email': 'ops@test.com',
            'password': 'StrongPass1!',
            'password2': 'StrongPass1!',
            'role': 'operations'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newops')
        self.assertTrue(user.groups.filter(name='operations').exists())

    def test_register_password_mismatch(self):
        """Registration fails on password mismatch."""
        resp = self.client.post('/api/auth/register/', {
            'username': 'baduser',
            'email': 'bad@test.com',
            'password': 'StrongPass1!',
            'password2': 'DifferentPass1!',
            'role': 'user'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Valid credentials return JWT tokens."""
        resp = self.client.post('/api/auth/login/', {
            'username': 'regular',
            'password': 'password123'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])
        self.assertIn('access', resp.data['data'])
        self.assertIn('refresh', resp.data['data'])

    def test_login_failure(self):
        """Invalid credentials return 401."""
        resp = self.client.post('/api/auth/login/', {
            'username': 'regular',
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_access_blocked(self):
        """Unauthenticated requests are blocked."""
        resp = self.client.get('/api/vehicles/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# ── Role-Based Access Tests ─────────────────────────────────────────────────

class RoleBasedAccessTests(BaseTest):

    def test_regular_user_cannot_create_component(self):
        """Regular users can only read components, not create/update/delete."""
        self._auth_client('regular')
        resp = self.client.post('/api/components/', {
            'name': 'New Part',
            'repair_price': 25.00,
            'purchase_price': 60.00
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_read_components(self):
        """Regular users can view components list."""
        self._auth_client('regular')
        resp = self.client.get('/api/components/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])
        self.assertGreaterEqual(len(resp.data['data']), 1)

    def test_ops_user_can_create_component(self):
        """Operations users can create components."""
        self._auth_client('ops')
        resp = self.client.post('/api/components/', {
            'name': 'New Part',
            'repair_price': 25.00,
            'purchase_price': 60.00
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data['success'])

    def test_ops_user_can_update_component(self):
        """Operations users can update component pricing."""
        self._auth_client('ops')
        resp = self.client.patch(f'/api/components/{self.component.id}/', {
            'repair_price': 75.00
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.component.refresh_from_db()
        self.assertEqual(self.component.repair_price, Decimal('75.00'))


# ── Vehicle Tests ───────────────────────────────────────────────────────────

class VehicleTests(BaseTest):

    def test_create_vehicle(self):
        """Authenticated user can register a vehicle."""
        self._auth_client('regular')
        resp = self.client.post('/api/vehicles/', {
            'vin': 'WBA3A5C5XDF123456',
            'make': 'BMW',
            'model': '3 Series',
            'owner_name': 'Jane Smith',
            'contact_number': '9876543210'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_vehicles(self):
        """Authenticated user can list vehicles."""
        self._auth_client('regular')
        resp = self.client.get('/api/vehicles/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


# ── Service Order Tests ─────────────────────────────────────────────────────

class ServiceOrderTests(BaseTest):

    def test_create_service_order(self):
        """Authenticated user can create a service order."""
        self._auth_client('regular')
        resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Oil change and brake check'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', resp.data['data'])

    def test_add_issue_to_order(self):
        """User can add an issue with a component to an order."""
        self._auth_client('regular')
        order_resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Fix brakes'
        }, format='json')
        order_id = order_resp.data['data']['id']

        resp = self.client.post('/api/issues/', {
            'service_order': order_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data['success'])
        # Price should auto-set from component repair_price
        self.assertEqual(Decimal(str(resp.data['data']['price'])), self.component.repair_price)

    def test_total_price_calculation(self):
        """System calculates correct total price from issues."""
        self._auth_client('regular')
        order_resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Multiple fixes'
        }, format='json')
        order_id = order_resp.data['data']['id']

        # Add first issue (repair)
        self.client.post('/api/issues/', {
            'service_order': order_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')
        # Add second issue (replace)
        self.client.post('/api/issues/', {
            'service_order': order_id,
            'component': self.component2.id,
            'issue_type': ServiceType.REPLACE
        }, format='json')

        order_resp = self.client.get(f'/api/orders/{order_id}/')
        expected_total = float(self.component.repair_price + self.component2.purchase_price)
        self.assertEqual(float(order_resp.data['data']['total_price']), expected_total)


# ── Payment Tests ───────────────────────────────────────────────────────────

class PaymentTests(BaseTest):

    def test_payment_success(self):
        """Valid payment creates a Payment record and marks order as paid."""
        self._auth_client('regular')
        # Create an order with an issue
        order_resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Test payment'
        }, format='json')
        order_id = order_resp.data['data']['id']

        self.client.post('/api/issues/', {
            'service_order': order_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')

        # Pay exactly the total
        resp = self.client.post(f'/api/orders/{order_id}/pay/', {
            'amount_paid': float(self.component.repair_price)
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])
        self.assertEqual(resp.data['data']['status'], 'paid')
        self.assertIn('transaction_id', resp.data['data'])
        self.assertIn('paid_at', resp.data['data'])

        # Verify payment record exists
        self.assertTrue(Payment.objects.filter(order_id=order_id).exists())

        # Verify order is marked paid
        order = ServiceOrder.objects.get(id=order_id)
        self.assertEqual(order.status, OrderStatus.PAID)

    def test_payment_amount_mismatch(self):
        """Payment with wrong amount is rejected."""
        self._auth_client('regular')
        order_resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Test mismatch'
        }, format='json')
        order_id = order_resp.data['data']['id']

        self.client.post('/api/issues/', {
            'service_order': order_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')

        resp = self.client.post(f'/api/orders/{order_id}/pay/', {
            'amount_paid': 1.00  # Wrong amount
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', str(resp.data).lower())

    def test_double_payment_rejected(self):
        """Paying an already-paid order is rejected."""
        self._auth_client('regular')
        order_resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Test double'
        }, format='json')
        order_id = order_resp.data['data']['id']

        self.client.post('/api/issues/', {
            'service_order': order_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')

        # First payment - success
        self.client.post(f'/api/orders/{order_id}/pay/', {
            'amount_paid': float(self.component.repair_price)
        }, format='json')

        # Second payment - rejected
        resp = self.client.post(f'/api/orders/{order_id}/pay/', {
            'amount_paid': float(self.component.repair_price)
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


# ── Component Model Tests ──────────────────────────────────────────────────

class ComponentModelTests(BaseTest):

    def test_component_repair_price_positive(self):
        """Component must have non-negative repair price (validated via full_clean)."""
        comp = Component(
            name='Bad Part',
            repair_price=-10.00,
            purchase_price=20.00
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            comp.full_clean()


# ── Payment Model Tests ────────────────────────────────────────────────────

class PaymentModelTests(BaseTest):

    def test_transaction_id_auto_generated(self):
        """Payment auto-generates a transaction ID."""
        order = ServiceOrder.objects.create(vehicle=self.vehicle, description='Test')
        payment = Payment.objects.create(order=order, amount=Decimal('50.00'))
        self.assertIsNotNone(payment.transaction_id)
        self.assertTrue(payment.transaction_id.startswith('PAY-'))

    def test_payment_str(self):
        """Payment __str__ returns a readable string."""
        order = ServiceOrder.objects.create(vehicle=self.vehicle, description='Test')
        payment = Payment.objects.create(order=order, amount=Decimal('50.00'))
        expected = f"Payment {payment.transaction_id} - 50.00 ({OrderStatus.PAID})"
        self.assertEqual(str(payment), expected)


# ── Data Scoping Tests ─────────────────────────────────────────────────────

class DataScopingTests(BaseTest):

    def test_user_sees_only_own_vehicles(self):
        """Regular user only sees vehicles they created."""
        self._auth_client('regular')
        self.client.post('/api/vehicles/', {
            'vin': 'REG1234567890',
            'make': 'Toyota',
            'model': 'Corolla',
            'owner_name': 'Regular Owned',
            'contact_number': '1111111111'
        }, format='json')

        self._auth_client('ops')
        self.client.post('/api/vehicles/', {
            'vin': 'OPS1234567890',
            'make': 'Ford',
            'model': 'Focus',
            'owner_name': 'Ops Owned',
            'contact_number': '2222222222'
        }, format='json')

        self._auth_client('regular')
        resp = self.client.get('/api/vehicles/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        vins = [v['vin'] for v in resp.data['data']]
        self.assertIn('REG1234567890', vins)
        self.assertNotIn('OPS1234567890', vins)

    def test_ops_sees_all_vehicles(self):
        """Operations user sees all vehicles."""
        self._auth_client('regular')
        self.client.post('/api/vehicles/', {
            'vin': 'REG1111111111',
            'make': 'Honda',
            'model': 'Accord',
            'owner_name': 'Regular',
            'contact_number': '3333333333'
        }, format='json')

        self._auth_client('ops')
        self.client.post('/api/vehicles/', {
            'vin': 'OPS2222222222',
            'make': 'Chevy',
            'model': 'Malibu',
            'owner_name': 'Ops',
            'contact_number': '4444444444'
        }, format='json')

        self._auth_client('ops')
        resp = self.client.get('/api/vehicles/')
        vins = [v['vin'] for v in resp.data['data']]
        self.assertIn('REG1111111111', vins)
        self.assertIn('OPS2222222222', vins)

    def test_user_cannot_pay_another_users_order(self):
        """Regular user cannot pay for an order created by another user."""
        self._auth_client('ops')
        order_resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Ops order'
        }, format='json')
        ops_order_id = order_resp.data['data']['id']

        self.client.post('/api/issues/', {
            'service_order': ops_order_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')

        self._auth_client('regular')
        resp = self.client.post(f'/api/orders/{ops_order_id}/pay/', {
            'amount_paid': float(self.component.repair_price)
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_ops_can_pay_any_order(self):
        """Operations user can pay for any user's order."""
        self._auth_client('regular')
        order_resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Regular order'
        }, format='json')
        reg_order_id = order_resp.data['data']['id']

        self.client.post('/api/issues/', {
            'service_order': reg_order_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')

        self._auth_client('ops')
        resp = self.client.post(f'/api/orders/{reg_order_id}/pay/', {
            'amount_paid': float(self.component.repair_price)
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_user_sees_only_own_issues(self):
        """Regular user only sees issues on their own orders."""
        self._auth_client('regular')
        reg_order = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Regular order'
        }, format='json')
        reg_id = reg_order.data['data']['id']
        self.client.post('/api/issues/', {
            'service_order': reg_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')

        self._auth_client('ops')
        ops_order = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Ops order'
        }, format='json')
        ops_id = ops_order.data['data']['id']
        self.client.post('/api/issues/', {
            'service_order': ops_id,
            'component': self.component2.id,
            'issue_type': ServiceType.REPLACE
        }, format='json')

        self._auth_client('regular')
        resp = self.client.get('/api/issues/')
        order_ids = [i['service_order'] for i in resp.data['data']]
        self.assertIn(reg_id, order_ids)
        self.assertNotIn(ops_id, order_ids)

    def test_user_cannot_add_issue_to_other_order(self):
        """Regular user cannot add an issue to another user's order."""
        self._auth_client('ops')
        order_resp = self.client.post('/api/orders/', {
            'vehicle': self.vehicle.id,
            'description': 'Ops order'
        }, format='json')
        ops_order_id = order_resp.data['data']['id']

        self._auth_client('regular')
        resp = self.client.post('/api/issues/', {
            'service_order': ops_order_id,
            'component': self.component.id,
            'issue_type': ServiceType.REPAIR
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)