# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-02 12:04
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import picklefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Short name for the field (as used in code)', max_length=50, validators=[django.core.validators.RegexValidator(message='Must be usable as a Python variable name', regex='^[a-zA-Z_][a-zA-Z0-9_]*$')])),
                ('label', models.CharField(help_text='Label for the field (displayed to the user)', max_length=250)),
                ('required', models.BooleanField(default=True, help_text='Is the field required?')),
                ('help_text', models.TextField(blank=True, help_text='Help text for the field')),
                ('position', models.PositiveIntegerField(default=0, help_text='Defines the order in which fields appear in the form. Fields are ordered in ascending order by this number, then alphabetically by name within that.')),
            ],
            options={
                'ordering': ('position', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A name for the form, to identify it in listings', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Metadatum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=250)),
                ('key', models.CharField(max_length=200)),
                ('value', picklefield.fields.PickledObjectField(editable=False, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'metadata',
            },
        ),
        migrations.CreateModel(
            name='UserChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(help_text='The value that the choice represents', max_length=250, unique=True)),
                ('display', models.CharField(help_text='How the value will be displayed to the user', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='BooleanField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.Field')),
            ],
            options={
                'verbose_name': 'Boolean field',
            },
            bases=('jasmin_metadata.field',),
        ),
        migrations.CreateModel(
            name='ChoiceFieldBase',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.Field')),
            ],
            options={
                'abstract': False,
            },
            bases=('jasmin_metadata.field',),
        ),
        migrations.CreateModel(
            name='DateField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.Field')),
            ],
            options={
                'verbose_name': 'Date field',
            },
            bases=('jasmin_metadata.field',),
        ),
        migrations.CreateModel(
            name='DateTimeField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.Field')),
            ],
            options={
                'verbose_name': 'Date-time field',
            },
            bases=('jasmin_metadata.field',),
        ),
        migrations.CreateModel(
            name='FloatField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.Field')),
                ('min_value', models.FloatField(blank=True, help_text='Minimum value allowed for input, or blank for no minimum', null=True, verbose_name='Minimum value')),
                ('max_value', models.FloatField(blank=True, help_text='Maximum value allowed for input, or blank for no maximum', null=True, verbose_name='Maximum value')),
            ],
            options={
                'verbose_name': 'Float field',
            },
            bases=('jasmin_metadata.field',),
        ),
        migrations.CreateModel(
            name='IntegerField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.Field')),
                ('min_value', models.IntegerField(blank=True, help_text='Minimum value allowed for input, or blank for no minimum', null=True, verbose_name='Minimum value')),
                ('max_value', models.IntegerField(blank=True, help_text='Maximum value allowed for input, or blank for no maximum', null=True, verbose_name='Maximum value')),
            ],
            options={
                'verbose_name': 'Integer field',
            },
            bases=('jasmin_metadata.field',),
        ),
        migrations.CreateModel(
            name='TextFieldBase',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.Field')),
                ('min_length', models.PositiveIntegerField(blank=True, help_text='Minimum length allowed for input, or blank for no minimum', null=True, verbose_name='Minimum length')),
                ('max_length', models.PositiveIntegerField(blank=True, help_text='Maximum length allowed for input, or blank for no maximum', null=True, verbose_name='Maximum length')),
            ],
            options={
                'abstract': False,
            },
            bases=('jasmin_metadata.field',),
        ),
        migrations.CreateModel(
            name='TimeField',
            fields=[
                ('field_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.Field')),
            ],
            options={
                'verbose_name': 'Time field',
            },
            bases=('jasmin_metadata.field',),
        ),
        migrations.AddField(
            model_name='field',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', related_query_name='field', to='jasmin_metadata.Form'),
        ),
        migrations.AddField(
            model_name='field',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_jasmin_metadata.field_set+', to='contenttypes.ContentType'),
        ),
        migrations.CreateModel(
            name='ChoiceField',
            fields=[
                ('choicefieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.ChoiceFieldBase')),
            ],
            options={
                'verbose_name': 'Choice field',
            },
            bases=('jasmin_metadata.choicefieldbase',),
        ),
        migrations.CreateModel(
            name='EmailField',
            fields=[
                ('textfieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.TextFieldBase')),
            ],
            options={
                'verbose_name': 'Email field',
            },
            bases=('jasmin_metadata.textfieldbase',),
        ),
        migrations.CreateModel(
            name='IPv4Field',
            fields=[
                ('textfieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.TextFieldBase')),
            ],
            options={
                'verbose_name': 'IPv4 address field',
            },
            bases=('jasmin_metadata.textfieldbase',),
        ),
        migrations.CreateModel(
            name='MultiLineTextField',
            fields=[
                ('textfieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.TextFieldBase')),
            ],
            options={
                'verbose_name': 'Multi-line text field',
            },
            bases=('jasmin_metadata.textfieldbase',),
        ),
        migrations.CreateModel(
            name='MultipleChoiceField',
            fields=[
                ('choicefieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.ChoiceFieldBase')),
            ],
            options={
                'verbose_name': 'Multiple choice field',
            },
            bases=('jasmin_metadata.choicefieldbase',),
        ),
        migrations.CreateModel(
            name='RegexField',
            fields=[
                ('textfieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.TextFieldBase')),
                ('regex', models.CharField(help_text='The Python-formatted regular expression to match', max_length=250)),
                ('error_message', models.CharField(default='Not a valid value.', help_text='The error message returned to the user if the supplied value fails the regex', max_length=250)),
            ],
            options={
                'verbose_name': 'Regex field',
            },
            bases=('jasmin_metadata.textfieldbase',),
        ),
        migrations.CreateModel(
            name='SingleLineTextField',
            fields=[
                ('textfieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.TextFieldBase')),
            ],
            options={
                'verbose_name': 'Single-line text field',
            },
            bases=('jasmin_metadata.textfieldbase',),
        ),
        migrations.CreateModel(
            name='SlugField',
            fields=[
                ('textfieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.TextFieldBase')),
            ],
            options={
                'verbose_name': 'Slug field',
            },
            bases=('jasmin_metadata.textfieldbase',),
        ),
        migrations.CreateModel(
            name='URLField',
            fields=[
                ('textfieldbase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='jasmin_metadata.TextFieldBase')),
            ],
            options={
                'verbose_name': 'URL field',
            },
            bases=('jasmin_metadata.textfieldbase',),
        ),
        migrations.AlterUniqueTogether(
            name='metadatum',
            unique_together=set([('content_type', 'object_id', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='field',
            unique_together=set([('form', 'name')]),
        ),
        migrations.AddField(
            model_name='choicefieldbase',
            name='choices',
            field=models.ManyToManyField(to='jasmin_metadata.UserChoice'),
        ),
    ]
