from django import forms

class AccessForm(forms.Form):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'style':'color: #000; '}),
        max_length=100,
        required=True,
    )