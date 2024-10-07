from django import forms
from users.models import PrivacyPolicy
from django.utils.translation import gettext_lazy as _

class SummaryForm(forms.ModelForm):
    class Meta:
        model = PrivacyPolicy
        fields = ['url']
        labels = {
            'url': ''
        }
        help_texts = {
            'url': _('http:// 또는 https://로 시작하는 유효한 URL을 입력하세요.')
        }