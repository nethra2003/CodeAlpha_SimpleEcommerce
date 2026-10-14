from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(
                choices=[
                    (5, "★★★★★ - Excellent"),
                    (4, "★★★★☆ - Very Good"),
                    (3, "★★★☆☆ - Good"),
                    (2, "★★☆☆☆ - Fair"),
                    (1, "★☆☆☆☆ - Poor"),
                ]
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Share your experience with this product...",
                    "maxlength": 1000,
                }
            ),
        }

    def clean_comment(self):
        comment = self.cleaned_data["comment"].strip()

        if not comment:
            raise forms.ValidationError(
                "Please write a review before submitting."
            )

        return comment
