# -*- coding: utf-8 -*-

from typing import List

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import UserAccount

# Create your forms here.

class SignupForm(UserCreationForm):
	username = forms.CharField(required=True)

	class Meta:
		model = UserAccount
		fields = ("username", "password1", "password2")

	def save(self):
		user = UserAccount(username=self.cleaned_data['username'])
		user.set_password(self.cleaned_data['password2'])
		user.save()
		
		return user
	
	def get_fields_errors(self, request, *args, **kwargs) -> List[str]:
		form = SignupForm(request.POST)
		errors = []
		for field in form:
			print(field.errors)
			errors += field.errors
		return errors 
