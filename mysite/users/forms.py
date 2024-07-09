from django import forms

# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms#html_forms
class RegistrationForm(forms.Form):
    display_name = forms.CharField(label="사용자 이름",help_text="사용자 이름", required=True)
    email = forms.EmailField(label="이메일 주소",help_text="이메일 주소. 로그인 시 사용됩니다", required=True)
    password = forms.CharField(label="새 비밀번호",help_text="비밀번호", widget=forms.PasswordInput, required=True)

    # Possible to add validation by overriding clean_<fieldname>()
    # Omitted here for testing purposes.
    # Also something possible is to use something called 'ModelForms' - which automatically creates a form based on existing models