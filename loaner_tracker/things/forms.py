from django import forms
from .models import Category, Thing
from .admin import ThingAdmin

# Create or update a thing
class ThingForm(forms.ModelForm): 
    class Meta:
        model = Thing
        fields = ThingAdmin.list_display + ThingAdmin.list_extra
        exclude = ThingAdmin.readonly_fields

# Create or update a thing
class ThingFormRO(forms.ModelForm): 
    class Meta:
        model = Thing
        fields = ThingAdmin.readonly_fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable specific fields if an instance exists (edit mode)
        if self.instance and self.instance.pk:
            for field in self.fields:
                self.fields[field].disabled = True
                self.fields[field].required = False