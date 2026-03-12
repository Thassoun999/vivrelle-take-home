# rentals/tests/test_regression.py

from django.test import TestCase
from rentals.models import User, Item, BorrowedItem
from rentals.services import borrow_item, return_item, change_user_plan, get_eligible_upgrades, get_eligible_downgrades, can_fit_plan

Tier = Item.Tier
Plan = User.Plan

class RentalRegressionTests(TestCase):
    def setUp(self):
        # Create test items
        self.premier_item = Item.objects.create(id="item-101", name="Premier Bag", tier=Tier.PREMIER.value)
        self.classique_item = Item.objects.create(id="item-102", name="Classique Bag", tier=Tier.CLASSIQUE.value)
        self.couture_item = Item.objects.create(id="item-103", name="Couture Bag", tier=Tier.COUTURE.value)

        # Create test users
        self.premier_user = User.objects.create(id="user-101", name="Premier User", email="premier@example.com", plan=Plan.PREMIER.value)
        self.classique_user = User.objects.create(id="user-102", name="Classique User", email="classique@example.com", plan=Plan.CLASSIQUE.value)
        self.couture_plus_user = User.objects.create(id="user-103", name="Couture Plus", email="coutureplus@example.com", plan=Plan.COUTURE_PLUS.value)

    # ----------------------
    # Borrowing tests
    # ----------------------
    def test_borrow_valid_items(self):
        borrow = borrow_item(self.premier_user, self.premier_item)
        self.assertEqual(borrow.item.id, self.premier_item.id)
        borrow = borrow_item(self.classique_user, self.classique_item)
        self.assertEqual(borrow.item.id, self.classique_item.id)
        borrow = borrow_item(self.couture_plus_user, self.couture_item)
        self.assertEqual(borrow.item.id, self.couture_item.id)

    def test_borrow_invalid_item(self):
        # Premier user cannot borrow classique
        with self.assertRaises(Exception) as e:
            borrow_item(self.premier_user, self.classique_item)
        self.assertIn("cannot borrow", str(e.exception))

    def test_couture_plus_limits(self):
        # Borrow 2 items, only 1 couture allowed
        borrow_item(self.couture_plus_user, self.classique_item)
        borrow_item(self.couture_plus_user, self.couture_item)

        another_couture = Item.objects.create(id="item-104", name="Couture Bag 2", tier=Tier.COUTURE.value)
        with self.assertRaises(Exception) as e:
            borrow_item(self.couture_plus_user, another_couture)
        self.assertIn("maximum number of borrowed items", str(e.exception))

    # ----------------------
    # Return item tests
    # ----------------------
    def test_return_item(self):
        borrow = borrow_item(self.premier_user, self.premier_item)
        self.assertTrue(borrow.is_active())
        return_item(borrow)
        self.assertFalse(borrow.is_active())

    # ----------------------
    # Plan upgrade/downgrade eligibility tests
    # ----------------------
    def test_eligible_upgrades_and_downgrades(self):
        borrow_item(self.premier_user, self.premier_item)

        upgrades = get_eligible_upgrades(self.premier_user)
        downgrades = get_eligible_downgrades(self.premier_user)

        # Premier user can upgrade to classique
        self.assertIn(Plan.CLASSIQUE.value, upgrades)
        # Cannot downgrade below premier
        self.assertEqual(downgrades, [])

        # Couture Plus user can downgrade to lower plans if items fit
        borrow_item(self.couture_plus_user, self.couture_item)
        downgrades = get_eligible_downgrades(self.couture_plus_user)
        self.assertIn(Plan.COUTURE.value, downgrades)
        self.assertNotIn(Plan.CLASSIQUE.value, downgrades)

        # Couture Plus user can't downgrade to lwoer plans with 2+ items
        borrow_item(self.couture_plus_user, self.classique_item)
        downgrades = get_eligible_downgrades(self.couture_plus_user)
        self.assertEqual(downgrades, [])


    # ----------------------
    # Change user plan tests
    # ----------------------
    def test_change_plan_valid(self):
        borrow_item(self.premier_user, self.premier_item)
        user = change_user_plan(self.premier_user, Plan.CLASSIQUE.value)
        self.assertEqual(user.plan, Plan.CLASSIQUE.value)

    def test_change_plan_invalid(self):
        borrow_item(self.classique_user, self.classique_item)
        with self.assertRaises(Exception) as e:
            change_user_plan(self.classique_user, Plan.PREMIER.value)
        self.assertIn("Cannot change plan", str(e.exception))