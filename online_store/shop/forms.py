from django import forms


class NewImportFileForm(forms.Form):
    """Form for uploading a new import file."""

    new_import_file = forms.FileField(
        required=False,
        help_text="Загрузить новый файл импорта",
        label="Новый файл импорта"
    )


class ImportFilesForm(forms.Form):
    """Form for selecting files to import."""

    email = forms.EmailField(
        required=False,
        label="Email админа",
        help_text="Email, куда будет отправлен отчет об импорте. "
                  "Если не указать, будут использоваться email-ы админов, "
                  "установленных по умолчанию."
    )
    files = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=[],
        label="Выберете файлы импорта",
        required=True,
    )
