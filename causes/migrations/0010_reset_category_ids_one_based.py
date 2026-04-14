from django.db import migrations


CANONICAL_CATEGORIES = [
    ("Health", "health"),
    ("Education", "education"),
    ("Water & Sanitation", "water-sanitation"),
    ("Food Security", "food-security"),
    ("Livelihood", "livelihood"),
    ("Disaster Relief", "disaster-relief"),
    ("Community Development", "community-development"),
    ("Child Welfare & Protection", "child-welfare-protection"),
    ("Environmental Conservation", "environmental-conservation"),
    ("Women & Girls' Empowerment", "women-girls-empowerment"),
    ("Disability Support & Inclusion", "disability-support-inclusion"),
    ("Human Rights & Advocacy", "human-rights-advocacy"),
    ("Sports & Culture", "sports-culture"),
    ("Other", "other"),
]


def reset_categories_to_one_based(apps, schema_editor):
    Cause = apps.get_model("causes", "Cause")
    Category = apps.get_model("causes", "Category")

    # Preserve current cause-to-category relation by slug before deleting categories.
    cause_slug_links = list(
        Cause.objects.exclude(category__isnull=True).values_list("id", "category__slug")
    )

    Category.objects.all().delete()

    # Reset auto-increment so the first recreated category gets ID 1.
    with schema_editor.connection.cursor() as cursor:
        if schema_editor.connection.vendor == "postgresql":
            cursor.execute("SELECT pg_get_serial_sequence('causes_category', 'id')")
            sequence_name = cursor.fetchone()[0]
            if sequence_name:
                cursor.execute("SELECT setval(%s, 1, false)", [sequence_name])
        elif schema_editor.connection.vendor == "sqlite":
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'causes_category'")

    slug_to_category_id = {}
    for name, slug in CANONICAL_CATEGORIES:
        category = Category.objects.create(name=name, slug=slug)
        slug_to_category_id[slug] = category.id

    for cause_id, slug in cause_slug_links:
        new_category_id = slug_to_category_id.get(slug)
        if new_category_id is not None:
            Cause.objects.filter(id=cause_id).update(category_id=new_category_id)


class Migration(migrations.Migration):

    dependencies = [
        ("causes", "0009_set_category_ids_zero_based"),
    ]

    operations = [
        migrations.RunPython(reset_categories_to_one_based, migrations.RunPython.noop),
    ]
