"""
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory.fuzzy import FuzzyInteger, FuzzyDate
from service.models import Wishlist, WishlistItem


class WishlistFactory(factory.Factory):
    """Creates fake Wishlists"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Wishlist

    id = factory.Sequence(lambda n: n)
    customer_id = FuzzyInteger(0, 255)  # random customer id
    wishlist_name = factory.Faker("name")  # random wishlist name
    created_date = FuzzyDate(date(2008, 1, 1))  # random date from _ to today


class WishlistItemFactory(factory.Factory):
    """Creates fake WishlistItems"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = WishlistItem

    id = factory.Sequence(lambda n: n)
    wishlist_id = FuzzyInteger(0, 1000)
    product_id = FuzzyInteger(0, 255)
    product_name = factory.Faker("name")
    product_price = factory.Faker(
        "pyfloat", left_digits=2, right_digits=2, positive=True
    )
    quantity = FuzzyInteger(0, 99)
    created_date = FuzzyDate(date(2008, 1, 1))
