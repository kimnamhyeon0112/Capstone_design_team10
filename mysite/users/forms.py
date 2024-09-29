from django import forms
from .models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import password_validation
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Forms#html_forms
class RegistrationForm(forms.Form):
    display_name = forms.CharField(
        label="사용자 이름", 
        required=True, 
        widget=forms.TextInput(attrs={
            'placeholder': '사용자 이름을 입력하세요'  # 사용자 이름 필드의 placeholder
        })
    )
    email = forms.EmailField(
        label="이메일 주소", 
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': '이메일 주소를 입력하세요'  # 이메일 필드의 placeholder
        })
    )
    password = forms.CharField(
        label="비밀번호", 
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': '비밀번호를 입력하세요'  # 비밀번호 필드의 placeholder
        })
    )
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # 라벨 뒤의 콜론을 없애기 위한 설정
        self.label_suffix = ''  # 콜론 제거

    # Possible to add validation by overriding clean_<fieldname>()
    # Omitted here for testing purposes.
    # Also something possible is to use something called 'ModelForms' - which automatically creates a form based on existing models
    
class LoginForm(forms.Form):
    email = forms.EmailField(label="이메일 주소", required=True)
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput, required=True)
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # 라벨 뒤의 콜론을 없애기 위한 설정
        self.label_suffix = ''  # 콜론 제거
class UserUpdateForm(forms.ModelForm):
    additional_email_local = forms.CharField(label='추가 이메일', required=False)
    additional_email_domain = forms.CharField(
        label='', 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': '도메인 (예: example.com)'})
    )
    contact_number1 = forms.CharField(label='연락처', required=False, max_length=3)
    contact_number2 = forms.CharField(label='', max_length=4, required=False)
    contact_number3 = forms.CharField(label='', max_length=4, required=False)
    
    nickname = forms.CharField(label='닉네임', required=False, max_length=30)
    display_name = forms.CharField(label='이름', max_length=30)
    

    class Meta:
        model = User
        fields = ['display_name', 'additional_email_local','additional_email_domain', 'contact_number1', 'contact_number2', 'contact_number3', 'nickname']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        # 라벨 뒤의 콜론을 없애기 위한 설정
        self.label_suffix = ''  # 콜론 제거
    
        additional_email = self.instance.additional_email
        
        if additional_email and '@' in additional_email:
            local_part, domain_part = additional_email.split('@', 1)
            self.fields['additional_email_local'].initial = local_part
            self.fields['additional_email_domain'].initial = domain_part
            
            print(f"사용자명: {local_part}, 도메인: {domain_part}")
        else:
            self.fields['additional_email_local'].initial = additional_email
            print(f"전체 이메일: {additional_email} (분리되지 않음)")
    
        phone_number = self.instance.contact_number  # User의 프로필에서 전화번호 가져오기
        
        if phone_number and '-' in phone_number:
            phone_parts = phone_number.split('-')
            if len(phone_parts) == 3:
                self.fields['contact_number1'].initial = phone_parts[0]
                self.fields['contact_number2'].initial = phone_parts[1]
                self.fields['contact_number3'].initial = phone_parts[2]
                
    def clean(self):
        cleaned_data = super().clean()
        
        additional_email_local = cleaned_data.get('additional_email_local')
        additional_email_domain = cleaned_data.get('additional_email_domain')

        # 추가 이메일과 도메인이 모두 입력된 경우 처리
        if additional_email_local and additional_email_domain:
            # 이메일 주소로 합치기
            combined_additional_email = f"{additional_email_local}@{additional_email_domain}"
            cleaned_data['additional_email'] = combined_additional_email
        elif additional_email_local and not additional_email_domain:
            # 도메인이 없으면 사용자명만 유지 (이메일이 제대로 저장되지 않도록 주의 필요)
            cleaned_data['additional_email'] = None

        contact_number1 = cleaned_data.get('contact_number1')
        contact_number2 = cleaned_data.get('contact_number2')
        contact_number3 = cleaned_data.get('contact_number3')

        if contact_number1 and contact_number2 and contact_number3:
            contact_number = f"{contact_number1}-{contact_number2}-{contact_number3}"
            cleaned_data['contact_number'] = contact_number  # 전화번호 합쳐서 저장
        else:
            cleaned_data['contact_number'] = None  # 전화번호가 비었을 경우 None 처리
            
        return cleaned_data

    def save(self, commit=True):
        # 사용자 데이터를 저장하기 전에 clean된 데이터를 가져옴
        user = super(UserUpdateForm, self).save(commit=False)

        # 합쳐진 추가 이메일이 있다면 저장
        additional_email = self.cleaned_data.get('additional_email')
        if additional_email:
            user.additional_email = additional_email  # 합쳐진 추가 이메일을 저장

        contact_number = self.cleaned_data.get('contact_number')
        if contact_number:
            user.contact_number = contact_number  # Profile 모델에 저장된 전화번호 필드
            
        if commit:
            user.save()
            
        return user
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = "현재 비밀번호 (필수 입력)"
        self.fields['new_password1'].label = "새 비밀번호"
        self.fields['new_password2'].label = "새 비밀번호 확인"        
        
        self.fields['new_password1'].required = False
        self.fields['new_password2'].required = False
        
        self.label_suffix = ''  # 콜론 제거
        
    def clean_new_password1(self):
        # 새 비밀번호가 비어 있지 않으면 검증
        new_password1 = self.cleaned_data.get('new_password1')
        if not new_password1:
            return None  # 새 비밀번호를 입력하지 않았다면 기존 비밀번호를 유지하도록 처리
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
    
    def save(self, commit=True):
        user = super().save(commit=False)  # 기존 유저 데이터를 가져옴

        # 비밀번호 필드가 비어있지 않으면 비밀번호 변경
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1:  # 새 비밀번호가 제공된 경우에만 비밀번호 변경
            user.set_password(new_password1)

        if commit:
            user.save()  # 새 비밀번호가 있으면 변경된 비밀번호로 저장, 없으면 기존 비밀번호 유지
        return user
    