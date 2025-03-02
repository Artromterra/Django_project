from django import forms


class ComparisonForm(forms.Form):
    product_id = forms.IntegerField()