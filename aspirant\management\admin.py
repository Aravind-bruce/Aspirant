from django.contrib import admin
from io import BytesIO
import pandas as pd
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.utils.timezone import is_aware, now
import openpyxl  # Ensure openpyxl is installed
from .models import Management, Clg, Syllabus  # Import models explicitly

# Function to export model data as an Excel backup (Admin Action)
def export_to_excel(modeladmin, request, queryset):
    model = modeladmin.model  
    model_name = str(_(model._meta.verbose_name_plural))  

    fields = [field.name for field in model._meta.fields]  
    data = list(queryset.values(*fields))  

    if not data:
        modeladmin.message_user(request, _("No records to export."), level='warning')
        return

    df = pd.DataFrame(data)

    # Convert timezone-aware datetime fields to naive and format properly
    for field in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[field]):
            df[field] = pd.to_datetime(df[field], errors='coerce')
            df[field] = df[field].apply(lambda dt: dt.replace(tzinfo=None) if is_aware(dt) else dt)
            df[field] = df[field].dt.strftime('%Y-%m-%d %H:%M:%S')
        elif df[field].dtype == "object":
            df[field] = df[field].astype(str)

    # Ensure proper handling of date fields
    for field in model._meta.fields:
        if field.get_internal_type() in ["DateField", "DateTimeField"]:
            if field.name in df.columns:
                df[field.name] = pd.to_datetime(df[field.name], errors='coerce')
                df[field.name] = df[field.name].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else "")

    # Generate dynamic filename with date and time
    timestamp = now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{model_name}_{timestamp}.xlsx"

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=model_name, index=False)

    output.seek(0)  # Reset buffer position

    # Set response headers for file download
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    
    return response

export_to_excel.short_description = _("Download as Excel Backup")

# Custom Admin Class to Enable Export Action
class CustomAdmin(admin.ModelAdmin):
    actions = [export_to_excel]

# Register models with Excel export action
admin.site.register(Management, CustomAdmin)
admin.site.register(Clg, CustomAdmin)
admin.site.register(Syllabus, CustomAdmin)
