from django.contrib import admin
from io import BytesIO
import pandas as pd
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.utils.timezone import is_aware, now
import openpyxl  # Ensure openpyxl is installed
from .models import Course, Question, Result

# Function to export model data as an Excel backup (Admin Action)
def export_to_excel(modeladmin, request, queryset):
    model = modeladmin.model  
    model_name = str(_(model._meta.verbose_name_plural))  

    fields = [field.name for field in model._meta.fields]  
    data = list(queryset.values(*fields))  
    df = pd.DataFrame(data)  

    # Convert timezone-aware datetime fields to naive and format properly
    for field in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[field]):  
            df[field] = df[field].apply(lambda dt: dt.replace(tzinfo=None) if is_aware(dt) else dt)
            df[field] = df[field].dt.strftime('%Y-%m-%d %H:%M:%S')  

    # Generate dynamic filename with date and time
    timestamp = now().strftime("%Y-%m-%d_%H-%M-%S")  # Current date-time
    filename = f"{model_name}_{timestamp}.xlsx"  

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=model_name, index=False)

    # Set response headers for file download
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    
    return response

export_to_excel.short_description = _("Download as Excel Backup")

# Register models with export action in Django Admin
@admin.register(Course)
@admin.register(Question)
@admin.register(Result)
class CustomAdmin(admin.ModelAdmin):
    actions = [export_to_excel]
