# Generated by Django 4.2.4 on 2024-01-22 11:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("business_model", "0006_bmquestion_sub_question_to"),
    ]

    operations = [
        migrations.AddField(
            model_name="equitydata",
            name="equity_community_amount",
            field=models.FloatField(
                default=0, verbose_name="Amount of equity the community would be able to mobilize (Million NGN)"
            ),
        ),
        migrations.AddField(
            model_name="equitydata",
            name="equity_developer_amount",
            field=models.FloatField(
                default=0, verbose_name="Amount of equity the project developer would be able to mobilize (Million NGN)"
            ),
        ),
        migrations.AlterField(
            model_name="businessmodel",
            name="model_name",
            field=models.CharField(
                choices=[
                    ("isolated_operator_led", "Isolated Mini-grid Company-led"),
                    ("isolated_cooperative_led", "Isolated Community-led"),
                    ("interconnected_operator_led", "Interconnected Mini-grid Company-led"),
                    ("interconnected_cooperative_led", "Interconnected Community-led"),
                ],
                max_length=60,
                null=True,
            ),
        ),
    ]