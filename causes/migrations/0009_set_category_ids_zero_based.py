# Generated migration: Set category IDs explicitly to 0-13

from django.db import migrations, connection

def set_category_ids_explicitly(apps, schema_editor):
    """
    Set category IDs explicitly to 0-13 by:
    1. Truncating the table
    2. Inserting categories with explicit IDs 0-13
    3. Resetting the sequence to 14
    """
    if connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "causes_category" RESTART IDENTITY CASCADE;')
            
            # Insert categories with explicit IDs
            insert_sql = '''
                INSERT INTO causes_category (id, name, slug) VALUES
                (0, 'Health', 'health'),
                (1, 'Education', 'education'),
                (2, 'Water & Sanitation', 'water-sanitation'),
                (3, 'Food Security', 'food-security'),
                (4, 'Livelihood', 'livelihood'),
                (5, 'Disaster Relief', 'disaster-relief'),
                (6, 'Community Development', 'community-development'),
                (7, 'Child Welfare & Protection', 'child-welfare-protection'),
                (8, 'Environmental Conservation', 'environmental-conservation'),
                (9, 'Women & Girls'' Empowerment', 'women-girls-empowerment'),
                (10, 'Disability Support & Inclusion', 'disability-support-inclusion'),
                (11, 'Human Rights & Advocacy', 'human-rights-advocacy'),
                (12, 'Sports & Culture', 'sports-culture'),
                (13, 'Other', 'other');
            '''
            cursor.execute(insert_sql)
            
            # Set the sequence to start at 14 for future inserts
            cursor.execute('SELECT setval(\'causes_category_id_seq\', 14);')
    else:
        # For SQLite or other databases
        Category = apps.get_model('causes', 'Category')
        Category.objects.all().delete()
        
        categories_data = [
            (0, 'Health', 'health'),
            (1, 'Education', 'education'),
            (2, 'Water & Sanitation', 'water-sanitation'),
            (3, 'Food Security', 'food-security'),
            (4, 'Livelihood', 'livelihood'),
            (5, 'Disaster Relief', 'disaster-relief'),
            (6, 'Community Development', 'community-development'),
            (7, 'Child Welfare & Protection', 'child-welfare-protection'),
            (8, 'Environmental Conservation', 'environmental-conservation'),
            (9, "Women & Girls' Empowerment", 'women-girls-empowerment'),
            (10, 'Disability Support & Inclusion', 'disability-support-inclusion'),
            (11, 'Human Rights & Advocacy', 'human-rights-advocacy'),
            (12, 'Sports & Culture', 'sports-culture'),
            (13, 'Other', 'other'),
        ]
        
        for id_val, name, slug in categories_data:
            Category.objects.create(id=id_val, name=name, slug=slug)

def reverse_reset(apps, schema_editor):
    """Reverse migration: delete all categories"""
    Category = apps.get_model('causes', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('causes', '0008_reset_categories_fresh'),
    ]

    operations = [
        migrations.RunPython(set_category_ids_explicitly, reverse_reset),
    ]
