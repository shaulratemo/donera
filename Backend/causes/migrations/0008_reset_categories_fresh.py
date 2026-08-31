# Generated migration: Reset category table with fresh IDs starting at 0

from django.db import migrations, connection

def reset_and_seed_categories(apps, schema_editor):
    """
    Reset the causes_category table by:
    1. Truncating the table and resetting the auto_increment sequence to 0
    2. Seeding the 14 standard categories with fresh IDs 0-13
    """
    # Reset sequence and clear table
    if connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "causes_category" RESTART IDENTITY CASCADE;')
    else:
        # Fallback for other databases
        Category = apps.get_model('causes', 'Category')
        Category.objects.all().delete()
    
    Category = apps.get_model('causes', 'Category')
    
    # The 14 standard categories
    categories = [
        'Health',
        'Education',
        'Water & Sanitation',
        'Food Security',
        'Livelihood',
        'Disaster Relief',
        'Community Development',
        'Child Welfare & Protection',
        'Environmental Conservation',
        "Women & Girls' Empowerment",
        'Disability Support & Inclusion',
        'Human Rights & Advocacy',
        'Sports & Culture',
        'Other',
    ]
    
    # Create categories with auto-generated IDs starting from 0
    for name in categories:
        slug = name.lower().replace(' ', '-').replace("'", '')
        Category.objects.create(name=name, slug=slug)

def reverse_reset(apps, schema_editor):
    """Reverse migration: delete all categories"""
    Category = apps.get_model('causes', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('causes', '0007_seed_default_categories'),
    ]

    operations = [
        migrations.RunPython(reset_and_seed_categories, reverse_reset),
    ]
