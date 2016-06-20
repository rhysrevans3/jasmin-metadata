"""
Module containing classes for integration of metadata with the Django admin site.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from functools import partial

from django.contrib import admin
from django.contrib.admin.helpers import AdminForm
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django import forms
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.admin.options import IS_POPUP_VAR
from django.template.response import SimpleTemplateResponse
from django.contrib import messages
from django.utils.html import escape

from polymorphic.admin import (
    PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
)

from .models import *


class FieldChoiceForm(forms.Form):
    """
    Use a select widget for the choice of field type instead of radio inputs.
    """
    ct_id = forms.ChoiceField(label = 'Field type', widget = forms.Select)


@admin.register(Field)
class FieldAdmin(PolymorphicParentModelAdmin):
    base_model = Field
    child_models = []
    add_type_form = FieldChoiceForm

    list_display = ('name', 'form')
    list_filter = ('form', )

    @classmethod
    def register_field_type(cls, model, model_admin = None):
        if not model_admin:
            model_admin = type(
                model._meta.model_name + 'Admin',
                (FieldChildAdmin, ),
                { 'base_model' : model }
            )
        cls.child_models.append((model, model_admin))


class FieldChildAdmin(PolymorphicChildModelAdmin):
    # The field on objects in this admin that we want to redirect to
    redirect_to_field = 'form'

    def response_post_save_add(self, request, obj):
        redirect_to = getattr(obj, self.redirect_to_field, None)
        if not redirect_to:
            return super().response_post_save_add(request, obj)
        else:
            return redirect(
                'admin:{}_{}_change'.format(
                    redirect_to._meta.app_label, redirect_to._meta.model_name
                ),
                redirect_to.pk
            )

    def response_post_save_change(self, request, obj):
        redirect_to = getattr(obj, self.redirect_to_field, None)
        if not redirect_to:
            return super().response_post_save_change(request, obj)
        else:
            return redirect(
                'admin:{}_{}_change'.format(
                    redirect_to._meta.app_label, redirect_to._meta.model_name
                ),
                redirect_to.pk
            )

    def delete_model(self, request, obj):
        # HACK
        # Before we delete the object, store the object we want to redirect to on
        # the request for later
        redirect_to = getattr(obj, self.redirect_to_field, None)
        request._redirect_to_obj_ = redirect_to
        return super().delete_model(request, obj)

    def response_delete(self, request, obj_display, obj_id):
        ## COPIED FROM django/contrib/admin/options.py
        if IS_POPUP_VAR in request.POST:
            return SimpleTemplateResponse('admin/popup_response.html', {
                'action': 'delete',
                'value': escape(obj_id),
            })

        self.message_user(request,
            _('The %(name)s "%(obj)s" was deleted successfully.') % {
                'name': force_text(opts.verbose_name),
                'obj': force_text(obj_display),
            }, messages.SUCCESS)
        # END COPIED SECTION

        redirect_to = getattr(request, '_redirect_to_obj_', None)
        if not redirect_to:
            return super().response_delete(request, obj_display, obj_id)
        else:
            return redirect(
                'admin:{}_{}_change'.format(
                    redirect_to._meta.app_label, redirect_to._meta.model_name
                ),
                redirect_to.pk
            )

class UserChoiceInline(admin.TabularInline):
    model = UserChoice
    prepopulated_fields = { 'display' : ('value', ) }

class ChoiceFieldAdmin(FieldChildAdmin):
    base_model = ChoiceField
    inlines = (UserChoiceInline, )

class MultipleChoiceFieldAdmin(FieldChildAdmin):
    base_model = MultipleChoiceField
    inlines = (UserChoiceInline, )


FieldAdmin.register_field_type(BooleanField)
FieldAdmin.register_field_type(SingleLineTextField)
FieldAdmin.register_field_type(MultiLineTextField)
FieldAdmin.register_field_type(EmailField)
FieldAdmin.register_field_type(IPv4Field)
FieldAdmin.register_field_type(RegexField)
FieldAdmin.register_field_type(SlugField)
FieldAdmin.register_field_type(URLField)
FieldAdmin.register_field_type(IntegerField)
FieldAdmin.register_field_type(FloatField)
FieldAdmin.register_field_type(ChoiceField, ChoiceFieldAdmin)
FieldAdmin.register_field_type(MultipleChoiceField, MultipleChoiceFieldAdmin)
FieldAdmin.register_field_type(DateField)
FieldAdmin.register_field_type(DateTimeField)
FieldAdmin.register_field_type(TimeField)


class FieldInline(admin.TabularInline):
    template = 'admin/polymorphic_inline_tabular.html'
    extra = 0
    model = Field
    fields = ('name', 'field_info', 'required', 'position', )
    readonly_fields = ('name', 'field_info', 'required')
    formfield_overrides = {
        models.TextField : {
            'widget' : forms.Textarea(attrs = { 'rows' : 3 }),
        },
    }

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    inlines = (FieldInline, )
    list_display = ('name', 'n_fields')

    def n_fields(self, obj):
        return obj.fields.count()
    n_fields.short_description = '# fields'


def _linkedform_factory(admin, request, obj_form_class):
    """
    Returns a subclass of the given ModelForm class that links an instance of
    :py:class:`~.forms.MetadataForm` when appropriate.

    Note that this **does not** put the fields from the metadata form into the
    model form (as they get rejected by the admin code), but it does tie the
    validity of the model form to the validity of the metadata form.
    """
    def new_init(self, data = None, files = None, **kwargs):
        instance = kwargs.get('instance', None)
        obj_form_class.__init__(self, data, files, **kwargs)
        # If there is no instance given, defer initialisation of the metadata_form
        if not instance:
            return
        # If there is no metadata form class for the object, return
        metadata_form_class = admin.get_metadata_form_class(request, instance)
        if metadata_form_class is None:
            return None
        if data:
            self.metadata_form = metadata_form_class(data = data)
        else:
            # Find any existing metadata for the object and use it to update initial
            content_type = ContentType.objects.get_for_model(instance)
            metadata = Metadatum.objects  \
                                .filter(content_type = content_type,
                                        object_id = instance.pk)
            self.metadata_form = metadata_form_class(initial = {
                d.key : d.value for d in metadata.all()
            })

    def new_is_valid(self):
        # If the parent is not valid, make no attempt to present metadata
        parent_valid = obj_form_class.is_valid(self)
        if not parent_valid:
            return False
        # If there is already a metadata form, validate it as well
        if hasattr(self, 'metadata_form'):
            return self.metadata_form.is_valid()
        # If there is no metadata form, see if we need to create one based on the
        # object about to be saved
        obj = self.save(commit = False)
        metadata_form_class = admin.get_metadata_form_class(request, obj)
        if metadata_form_class is None:
            return True
        self.metadata_form = metadata_form_class(data = request.POST)
        return self.metadata_form.is_valid()

    return type(obj_form_class)(obj_form_class.__name__, (obj_form_class, ), {
        'Meta' : type('Meta', (getattr(obj_form_class, 'Meta', object), ), {}),
        'formfield_callback' : partial(admin.formfield_for_dbfield, request = request),
        '__init__' : new_init,
        'is_valid' : new_is_valid,
    })


class HasMetadataModelAdmin(admin.ModelAdmin):
    """
    ``ModelAdmin`` for use with models that may have metadata attached.
    """
    #: The metadata form class to use
    #: Must inherit from :py:class:`~.models.MetadataForm`
    metadata_form_class = None

    change_form_template = 'admin/change_form_metadata.html'

    def get_metadata_form_class(self, request, obj = None):
        """
        Returns the metadata form to use for the given object. It can be assumed
        that the object has been previously saved.

        The returned form must inherit from :py:class:`~.forms.MetadataForm`.
        """
        return self.metadata_form_class

    def get_form(self, request, obj = None, **kwargs):
        """
        Modifies the parent method to returns a form that has a metadata form linked.
        The form is only considered valid if the metadata form is also valid.
        """
        return _linkedform_factory(self, request, super().get_form(request, obj, **kwargs))

    def save_model(self, request, obj, form, change):
        """
        Modifies the parent method to also save any metadata.
        """
        super().save_model(request, obj, form, change)
        if hasattr(form, 'metadata_form'):
            form.metadata_form.save(obj)

    def render_change_form(self, request, context,
                           add = False, change = False, form_url = '', obj = None):
        # Inject things for the metadata form into the context
        form = context['adminform'].form
        if hasattr(form, 'metadata_form'):
            context['metadata_form'] = AdminForm(
                form.metadata_form,
                # Put all the fields in one fieldset
                [('Metadata', { 'fields' : list(form.metadata_form.fields.keys()) })],
                # No pre-populated fields
                {},
            )
            context['errors'].extend(form.metadata_form.errors.values())
        return super().render_change_form(request, context, add, change, form_url, obj)
