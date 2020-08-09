from django.contrib.auth.forms import UserCreationForm , UserChangeForm , ReadOnlyPasswordHashField
from ibmUsers.models import User
from django import forms


class UserCreation(UserCreationForm):
    password1 = forms.CharField(label="Password" , widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password Confirmation", widget=forms.PasswordInput)

    class Meta(UserCreationForm):
        model = User
        fields = ('email' , 'first_name' , 'last_name' , 'phone_number'  , 'is_teacher' , 'is_staff')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChange(UserChangeForm):
    password = ReadOnlyPasswordHashField

    class Meta(UserChangeForm):
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number', 'is_teacher', 'is_staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]