"""
Django models for the JASMIN services app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from picklefield.fields import PickledObjectField


class Metadatum(models.Model):
    """
    Model that allows the association of arbitrary data of any pickle-able
    type with any model instance.

    This is achieved by using the generic foreign key from the
    ``django.contrib.contenttypes`` module.
    """
    class Meta:
        verbose_name_plural = 'metadata'

    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    #: The metadata key
    key = models.CharField(max_length = 200)
    #: The pickled value for the datum
    value = PickledObjectField(null = True)

    def clean(self):
        # The key must be unique for the object
        if self.content_type and self.object_id and self.key:
            q = self.__class__.objects  \
                    .filter(content_type = self.content_type,
                            object_id = self.object_id,
                            key = self.key)
            if self.pk:
                q = q.exclude(pk = self.pk)
            if q.exists():
                raise ValidationError({
                    'key' : 'Key must be unique for object'
                })


class HasMetadata(models.Model):
    """
    Abstract base model for all models that need access to attached metadata.
    """
    class Meta:
        abstract = True

    metadata = GenericRelation(Metadatum, content_type_field = 'content_type',
                                          object_id_field = 'object_id')

    def copy_metadata_to(self, obj):
        """
        Finds all metadata entries associated with this object and copies them
        onto the given object.
        """
        # We can still attach metadata to obj, even if it doesn't inherit from
        # HasMetadata. However, we can't rely on it having a metadata property...
        ctype = ContentType.objects.get_for_model(obj)
        for datum in self.metadata.all():
            # If obj already has the metadata, overwrite it
            # Otherwise, create a new object
            try:
                new = Metadatum.objects  \
                               .get(content_type = ctype,
                                    object_id = obj.pk, key = datum.key)
            except Metadatum.DoesNotExist:
                new = Metadatum(content_object = obj, key = datum.key)
            new.value = datum.value
            new.save()
