from django import forms


class CommentForm(forms.Form):
    name = forms.CharField(label='Name')
    message = forms.CharField(label='Message')


class RequestForm(forms.Form):
    email = forms.EmailField(label='Email')
    request = forms.CharField(label='Request')

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password')
    
