from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import WebBlog, WebBlogComment, WebInquiry


class WebBlogForm(forms.ModelForm):
    class Meta:
        model = WebBlog
        fields = ['category', 'title', 'dept', 'from_date', 'to_date', 'status', 'content', 'featured_image', 'phone']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter title'}),
            'dept': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter department'}),
            'from_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'content': SummernoteWidget(),
            'featured_image': forms.FileInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter phone number'}),
        }
        labels = {
            'category': 'Category',
            'title': 'Title',
            'dept': 'Department',
            'from_date': 'Start Date',
            'to_date': 'End Date',
            'status': 'Status',
            'content': 'Content',
            'featured_image': 'Featured Image',
            'phone': 'Phone',
        }


class WebBlogCommentForm(forms.ModelForm):
    class Meta:
        model = WebBlogComment
        fields = ['applicant', 'phone', 'email', 'is_agreed', 'attached_file']
        widgets = {
            'applicant': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter your name'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Enter email'}),
            'is_agreed': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'attached_file': forms.FileInput(attrs={'class': 'form-input'}),
        }
        labels = {
            'applicant': 'Applicant',
            'phone': 'Phone',
            'email': 'Email',
            'is_agreed': 'Agree to Privacy Policy',
            'attached_file': 'Attachment',
        }


class WebInquiryForm(forms.ModelForm):
    class Meta:
        model = WebInquiry
        fields = ['business_name', 'name', 'position', 'phone', 'email', 'message', 'is_agreed', 'status']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '업체명을 입력하세요'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '담당자명을 입력하세요'}),
            'position': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '직책을 입력하세요'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '연락처를 입력하세요'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': '이메일을 입력하세요'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5, 'placeholder': '문의내용을 입력하세요'}),
            'is_agreed': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'business_name': '업체명',
            'name': '담당자명',
            'position': '직책',
            'phone': '연락처',
            'email': '이메일',
            'message': '문의내용',
            'is_agreed': '개인정보 수집 및 이용 동의',
            'status': '처리상태',
        }
    
    def __init__(self, *args, **kwargs):
        exclude_status = kwargs.pop('exclude_status', False)
        super().__init__(*args, **kwargs)
        if exclude_status:
            self.fields.pop('status', None)


class PublicWebInquiryForm(forms.ModelForm):
    is_agreed = forms.BooleanField(
        required=True,
        error_messages={'required': '개인정보 수집 및 이용에 동의해주세요.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label='개인정보 수집 및 이용 동의'
    )
    
    class Meta:
        model = WebInquiry
        fields = ['business_name', 'name', 'position', 'phone', 'email', 'message', 'is_agreed']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '업체명을 입력하세요'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '담당자명을 입력하세요'}),
            'position': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '직책을 입력하세요'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '연락처를 입력하세요'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': '이메일을 입력하세요'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5, 'placeholder': '문의내용을 입력하세요'}),
        }
        labels = {
            'business_name': '업체명',
            'name': '담당자명',
            'position': '직책',
            'phone': '연락처',
            'email': '이메일',
            'message': '문의내용',
        }