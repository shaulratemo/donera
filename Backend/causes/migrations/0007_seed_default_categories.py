from django.db import migrations
from django.utils.text import slugify


DEFAULT_CATEGORIES = [
    "Health",
    "Education",
    "Water & Sanitation",
    "Food Security",
    "Livelihood",
    "Disaster Relief",
    "Community Development",
    "Child Welfare & Protection",
    "Environmental Conservation",
    "Women & Girls' Empowerment",
    "Disability Support & Inclusion",
    "Human Rights & Advocacy",
    "Sports & Culture",
    "Other",
]


def seed_default_categories(apps, schema_editor):
    Category = apps.get_model("causes", "Category")

    for name in DEFAULT_CATEGORIES:
        category = Category.objects.filter(name=name).first()
        if category:
            if not category.slug:
                base_slug = slugify(name)
                candidate_slug = base_slug
                index = 1
                while Category.objects.filter(slug=candidate_slug).exclude(pk=category.pk).exists():
                    candidate_slug = f"{base_slug}-{index}"
                    index += 1
                category.slug = candidate_slug
                category.save(update_fields=["slug"])
            continue

        base_slug = slugify(name)
        candidate_slug = base_slug
        index = 1
        while Category.objects.filter(slug=candidate_slug).exists():
            candidate_slug = f"{base_slug}-{index}"
            index += 1

        Category.objects.create(name=name, slug=candidate_slug)


class Migration(migrations.Migration):

    dependencies = [
        ("causes", "0006_alter_cause_category"),
    ]

    operations = [
        migrations.RunPython(seed_default_categories, migrations.RunPython.noop),
    ]
