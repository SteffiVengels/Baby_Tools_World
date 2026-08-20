from django.core.exceptions import ValidationError
from django.test import TestCase

from btw_app.utils import log_execution
from products.models import Category, Product, Tag


class TagTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_tag_name = "Sale"

    @log_execution
    def test_successful_tag_creation(self):
        # Test the successful creation of a tag
        tag = Tag.objects.create(name=self.test_tag_name)
        tag.full_clean()
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.first().name, self.test_tag_name)
        # Ensure created_at and updated_at are set automatically
        self.assertIsNotNone(Tag.objects.first().created_at)
        self.assertIsNotNone(Tag.objects.first().updated_at)

    @log_execution
    def test_failure_tag_creation_with_duplicate_name(self):
        # Test that two tags cannot share the same name (unique constraint)
        Tag.objects.create(name=self.test_tag_name)
        with self.assertRaises(ValidationError) as ctx:
            duplicate = Tag(name=self.test_tag_name)
            duplicate.full_clean()
            duplicate.save()
        self.assertIn("name", ctx.exception.message_dict)
        self.assertEqual(Tag.objects.count(), 1)

    @log_execution
    def test_failure_tag_creation_without_name(self):
        # Test that a tag cannot be created without a name
        with self.assertRaises(ValidationError) as ctx:
            tag = Tag()
            tag.full_clean()
            tag.save()
        self.assertEqual(ctx.exception.message_dict, {"name": ["This field cannot be blank."]})
        self.assertEqual(Tag.objects.count(), 0)

    @log_execution
    def test_product_can_have_multiple_tags(self):
        # Test the ManyToMany relation: a product can have several tags
        category = Category.objects.create(name="Toys", slug="toys")
        product = Product.objects.create(name="Wooden Sword", price="22.99", category=category)
        tag_sale = Tag.objects.create(name="Sale")
        tag_wood = Tag.objects.create(name="Wooden")
        product.tags.add(tag_sale, tag_wood)
        self.assertEqual(product.tags.count(), 2)
        self.assertIn(tag_sale, product.tags.all())
        self.assertIn(tag_wood, product.tags.all())

    @log_execution
    def test_tag_string_representation(self):
        # Test the string representation of a tag
        tag = Tag.objects.create(name=self.test_tag_name)
        self.assertEqual(str(tag), self.test_tag_name)
        