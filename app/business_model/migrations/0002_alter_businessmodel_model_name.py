# Generated by Django 4.2.4 on 2023-10-11 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("business_model", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="businessmodel",
            name="model_name",
            field=models.CharField(
                choices=[
                    ("isolated_operator_led", "Isolated operator led"),
                    ("isolated_cooperative_led", "Isolated cooperative led"),
                    ("interconnected_operator_led", "Interconnected operator led"),
                    ("interconnected_spv_led", "Interconnected spv led"),
                    ("interconnected_cooperative_led", "Interconnected cooperative led"),
                    ("interconnected_collaborative_spv_led", "Interconnected collaborative spv led"),
                ],
                max_length=60,
                null=True,
            ),
        )
    ]