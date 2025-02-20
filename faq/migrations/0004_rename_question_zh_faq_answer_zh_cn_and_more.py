# Generated by Django 5.1.5 on 2025-02-01 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0003_faq_answer_de_faq_answer_es_faq_answer_fr_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='faq',
            old_name='question_zh',
            new_name='answer_zh_cn',
        ),
        migrations.RemoveField(
            model_name='faq',
            name='answer_zh',
        ),
        migrations.AddField(
            model_name='faq',
            name='question_zh_cn',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='faq',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer_de',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer_es',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer_fr',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='faq',
            name='answer_hi',
            field=models.TextField(blank=True, null=True),
        ),
    ]
