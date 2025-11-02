from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import CustomUser, Publisher, Article, Newsletter

# ----------------------------
# Article Form
# ----------------------------
class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing Article instances.

    Dynamically filters the publisher field based on the user's role:
        - Editors see a read-only display of the publisher for existing articles.
        - Journalists see only publishers they are assigned to, or can select 'Independent'.

    Attributes:
        publisher (ModelChoiceField): Allows selecting a publisher or marking as Independent.

    Methods:
        __init__(*args, **kwargs): Customize form fields based on the user role.
    """

    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.none(),
        required=False,
        empty_label="Independent",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Article Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your article here...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Editor: show publisher name readonly
            if user.role == 'Editor':
                if self.instance and self.instance.publisher:
                    self.fields['publisher_display'] = forms.CharField(
                        initial=self.instance.publisher.name,
                        disabled=True,
                        required=False,
                        label='Publisher'
                    )
                    del self.fields['publisher']  # remove dropdown
            else:
                # Journalist: filter publishers assigned to them
                assigned_publishers = Publisher.objects.filter(
                    Q(journalists=user) | Q(editors=user)
                ).distinct()
                self.fields['publisher'].queryset = assigned_publishers
                self.fields['publisher'].empty_label = "Independent"

# ----------------------------
# Newsletter Form
# ----------------------------
class NewsletterForm(forms.ModelForm):
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.none(),
        required=False,
        empty_label="Independent",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Newsletter
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Newsletter Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your newsletter here...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Editor: show publisher name readonly
            if user.role == 'Editor':
                if self.instance and self.instance.publisher:
                    self.fields['publisher_display'] = forms.CharField(
                        initial=self.instance.publisher.name,
                        disabled=True,
                        required=False,
                        label='Publisher'
                    )
                    del self.fields['publisher']  # remove dropdown
            else:
                # Journalist: filter publishers assigned to them
                assigned_publishers = Publisher.objects.filter(
                    Q(journalists=user) | Q(editors=user)
                ).distinct()
                self.fields['publisher'].queryset = assigned_publishers
                self.fields['publisher'].empty_label = "Independent"

# ----------------------------
# Custom User Registration Form
# ----------------------------
class CustomUserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('Reader', 'Reader'),
        ('Publisher', 'Publisher'),
        ('Editor', 'Editor'),
        ('Journalist', 'Journalist'),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    new_publisher_name = forms.CharField(
        required=False,
        label="Publisher Name (if registering as Publisher)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Publisher Name'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2', 'new_publisher_name']

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        new_pub_name = cleaned.get('new_publisher_name', '').strip()

        if role == 'Publisher' and not new_pub_name:
            raise ValidationError("As a Publisher, you must provide a publisher name.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.save()

        if user.role == 'Publisher':
            new_pub_name = self.cleaned_data.get('new_publisher_name', '').strip()
            if new_pub_name:
                Publisher.objects.create(name=new_pub_name, owner=user)

        return user
