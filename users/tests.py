from django.test import TestCase
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFormTests(TestCase):
    def test_create_user_form_valid(self):
        data = {
            'username':'usuariotest',
            'email':'t@x.com',
            'first_name':'X',
            'last_name':'Y',
            'password1':'ContrasenyaFort4!',
            'password2':'ContrasenyaFort4!',
        }
        f = CustomUserCreationForm(data=data)
        self.assertTrue(f.is_valid())
        user = f.save()
        self.assertEqual(User.objects.count(), 1)