from django.db import models


class OrganizationMixin(models.Model):
    """Abstract model to add organization field to any model"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)s_organization'
    )
    
    class Meta:
        abstract = True
