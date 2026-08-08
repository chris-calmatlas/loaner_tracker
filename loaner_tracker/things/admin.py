from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from .models import Thing, Category

class ThingAdmin(admin.ModelAdmin):
    readonly_fields = ('assigned_date', 'returned_date', 'missing_date', 'last_assigned_to', 'damaged_date', 'fixed_date')
    list_display = ('category', 'barcode', 'status', 'assigned_to')
    list_extra = ('description', 'size', 'damaged', 'notes')
    list_filter = ('category', 'status', 'damaged')
    # search_fields = ('barcode', 'name', 'assigned_to')
    
    fieldsets = [
        ( None, { "fields": list_display }),
        ( "Extra", { "fields": list_extra }),
        ( "Dates", { "fields": readonly_fields })]

class CategoryAdmin(admin.ModelAdmin):
    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        
        if obj and obj.is_default:
            messages.error(request, "Cannot delete the default category. Set another category as default before deleting this one.")
            # Clear any potential success messages that might have been queued
            messages.get_messages(request).used = set()
            return redirect('admin:things_category_changelist')
        
        # If not default, let the default behavior run
        return super().delete_view(request, object_id, extra_context)

    # 3. Update delete_model to be safe (though delete_view is now handling the block)
    def delete_model(self, request, obj):
        # This should now only be called if delete_view allowed it
        if obj.is_default:
            messages.error(request, "Cannot delete the default category.")
            return redirect('admin:things_category_changelist')
        super().delete_model(request, obj)

    # 4. Fix the bulk delete action
    def delete_queryset(self, request, queryset):
        default_category = queryset.filter(is_default=True).first()
        
        if default_category:
            queryset = queryset.exclude(id=default_category.id)
            messages.error(
                request, 
                f"Cannot delete the default category '{default_category.name}'. "
            )
        count = queryset.count()
        if count < 1:
            messages.set_level(request, messages.ERROR)
        return super().delete_queryset(request, queryset)

admin.site.register(Thing, ThingAdmin)
admin.site.register(Category, CategoryAdmin)