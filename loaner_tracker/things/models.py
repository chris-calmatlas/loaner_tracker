from unittest import case

from django.db import models, transaction
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils import timezone
    
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, default="Unnamed Category", unique=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


    def save(self, *args, **kwargs):
        # If this instance is being set as default
        if self.is_default:
            # Use a transaction to ensure atomicity
            with transaction.atomic():
                # Update all existing categories to False
                # Exclude the current instance if it's being updated (to avoid unnecessary DB hits)
                # If it's a new object (pk is None), we update everything
                if self.pk:
                    Category.objects.exclude(pk=self.pk).update(is_default=False)
                else:
                    Category.objects.update(is_default=False)
        
        # Now save the current instance
        super().save(*args, **kwargs)

    
    def __str__(self):
        return (self.name if self.name else "Unnamed Category")

def get_default_category():
    default_category = Category.objects.get_or_create(is_default=True)
    return default_category[0].id

class Thing(models.Model):
    id = models.AutoField(primary_key=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, blank=True, null=True, default=get_default_category)
    status = models.CharField(max_length=20, default="available",
                              choices=[
                                  ("available", "Available"),
                                  ("assigned", "Assigned"),
                                  ("missing", "Missing")
                                  ])

    #Optional
    size = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    description = models.CharField(max_length=100, blank=True, default=category.name)
    assigned_to = models.CharField(max_length=100, blank=True, default="")
    damaged = models.BooleanField(default=False, blank=True)

    # Read Only Fields
    last_assigned_to = models.CharField(max_length=100, blank=True, default="")
    assigned_date = models.DateTimeField(blank=True, null=True)
    returned_date = models.DateTimeField(blank=True, null=True)
    missing_date = models.DateTimeField(blank=True, null=True)
    damaged_date = models.DateTimeField(blank=True, null=True)
    fixed_date = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.category.name

        # Now save the current instance
        super().save(*args, **kwargs)

    def __str__(self):
        return (self.category.name + "," +
                (self.barcode if self.barcode else "") + "," +  
                (self.description) + "," +
                ("Size: " + self.size if self.size else "") + "," + 
                ("Assigned to: " + self.assigned_to if self.assigned_to else "Not Assigned"))

@receiver(pre_save, sender=Thing)
def update_readonly_fields(sender, instance, **kwargs):
    if instance.pk:
        original_instance = Thing.objects.filter(pk=instance.pk).first()
        match instance.status:
            case "available":
                # If previously assigned, update last_assigned_to
                if original_instance.assigned_to:
                    instance.last_assigned_to = original_instance.assigned_to

            case "assigned":
                # Set the last assigned and returned/assigned dates
                if instance.assigned_to != original_instance.assigned_to:
                    if original_instance.assigned_to:
                        # return the thing first
                        instance.last_assigned_to = original_instance.assigned_to
                        instance.returned_date = timezone.now()
                        
            case "missing":
                # If previously assigned, update last_assigned_to
                if original_instance.assigned_to:
                    instance.last_assigned_to = original_instance.assigned_to

@receiver(pre_save, sender=Thing)
def set_status_state(sender,instance, **kwargs):
    match instance.status:
        case "available":
            # Cannot be assigned or missing if available
            instance.missing_date = None
            instance.assigned_to = ""
            instance.returned_date = timezone.now()

        case "assigned":
            # If assigned_to is blank, change status to available and re-save
            if instance.assigned_to == "":
                instance.status = "available"
                instance.save()
            else:
                instance.assigned_date = timezone.now()

        case "missing":
            # Cannot be assigned
            instance.assigned_to = ""
            instance.missing_date = timezone.now()

@receiver(pre_save, sender=Thing)
def validate_damage(sender, instance, **kwargs):
    if instance.pk:
        original_instance = Thing.objects.filter(pk=instance.pk).first()
        if instance.damaged != original_instance.damaged:
            if instance.damaged:
                instance.damaged_date = timezone.now()
            else:
                instance.fixed_date = timezone.now()

@receiver(post_save, sender=Thing)
def set_barcode_after_save(sender, instance, created, **kwargs):
    if not instance.barcode:
        instance.barcode = str(instance.id)
        instance.save()
