from django import forms
from .models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import password_validation
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms#html_forms
class RegistrationForm(forms.Form):
    display_name = forms.CharField(label="사용자 이름",help_text="사용자 이름", required=True)
    email = forms.EmailField(label="이메일 주소",help_text="이메일 주소. 로그인 시 사용됩니다", required=True)
    password = forms.CharField(label="새 비밀번호",help_text="비밀번호", widget=forms.PasswordInput, required=True)

    # Possible to add validation by overriding clean_<fieldname>()
    # Omitted here for testing purposes.
    # Also something possible is to use something called 'ModelForms' - which automatically creates a form based on existing models
    
class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일 주소", required=True)
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput, required=True)
    
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='이메일')
    additional_email = forms.EmailField(label='추가 이메일', required=False)
    contact_number = forms.CharField(label='연락처', required=False, max_length=15)
    nickname = forms.CharField(label='닉네임', required=False, max_length=30)
    display_name = forms.CharField(label='이름', max_length=30)
    
    class Meta:
        model = User
        fields = ['display_name', 'email', 'additional_email', 'contact_number', 'nickname']
        
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = "현재 비밀번호 (필수 입력)"
        self.fields['new_password1'].label = "새 비밀번호"
        self.fields['new_password2'].label = "새 비밀번호 확인"        
        
        self.fields['new_password1'].required = False
        self.fields['new_password2'].required = False
        
        def clean_new_password1(self):
        # 새 비밀번호가 비어 있지 않으면 검증
            new_password1 = self.cleaned_data.get('new_password1')
            if new_password1:
                password_validation.validate_password(new_password1, self.user)
            return new_password1

        def clean_new_password2(self):
        # 새 비밀번호가 비어 있지 않으면 일치 여부 확인
            new_password1 = self.cleaned_data.get('new_password1')
            new_password2 = self.cleaned_data.get('new_password2')
            if new_password1 and new_password2:
                if new_password1 != new_password2:
                    raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
            return new_password2