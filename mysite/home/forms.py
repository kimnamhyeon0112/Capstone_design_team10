from django import forms
from users.models import PrivacyPolicy

class SummaryForm(forms.ModelForm):
    class Meta:
        model = PrivacyPolicy
        fields = ['url']
        labels = {
            'url': ''
        }
        help_texts = {
            'url': 'http:// 또는 https://로 시작하는 유효한 URL을 입력하세요.'
        }