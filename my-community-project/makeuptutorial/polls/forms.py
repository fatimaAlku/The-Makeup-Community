from django import forms
from django.forms import inlineformset_factory
from .models import Review, ReviewMedia, ReviewHelpfulness
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class ReviewForm(forms.ModelForm):
    start_wear_test = forms.BooleanField(required=False)  # from UI toggle

    class Meta:
        model = Review
        fields = ["title", "body", "rating", "is_verified_purchase", "receipt", 
                 "skin_type", "skin_tone", "age_range"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Summarize your experience..."}),
            "body": forms.Textarea(attrs={"rows": 4, "placeholder": "Share your detailed thoughts about this product..."}),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5, "step": 1, "class": "rating-input"}),
            "skin_type": forms.Select(choices=[
                ("", "Select skin type"),
                ("oily", "Oily"),
                ("dry", "Dry"),
                ("combination", "Combination"),
                ("sensitive", "Sensitive"),
                ("normal", "Normal"),
            ]),
            "skin_tone": forms.Select(choices=[
                ("", "Select skin tone"),
                ("fair", "Fair"),
                ("light", "Light"),
                ("medium", "Medium"),
                ("tan", "Tan"),
                ("deep", "Deep"),
            ]),
            "age_range": forms.Select(choices=[
                ("", "Select age range"),
                ("18-24", "18-24"),
                ("25-34", "25-34"),
                ("35-44", "35-44"),
                ("45-54", "45-54"),
                ("55+", "55+"),
            ]),
        }

    def clean_rating(self):
        r = self.cleaned_data.get("rating") or 0
        return max(1, min(5, int(r)))

ReviewMediaFormSet = inlineformset_factory(
    Review, ReviewMedia,
    fields=["file", "kind"],
    extra=2, can_delete=True,
    widgets={
        "kind": forms.Select(choices=[("photo", "Photo"), ("video", "Video")]),
    }
)

class ReviewHelpfulnessForm(forms.ModelForm):
    class Meta:
        model = ReviewHelpfulness
        fields = ["is_helpful"]
        widgets = {
            "is_helpful": forms.HiddenInput()
        }

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add CSS classes/placeholders
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " text-input").strip()
            field.widget.attrs.setdefault("placeholder", field.label)
