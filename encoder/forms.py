from django import forms

from encoder import models as encoder


class CommentForm(forms.ModelForm):
    text = forms.CharField(label='New Comment', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        return super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated():
            raise forms.ValidationError("You must login to comment.")
        return self.cleaned_data

    class Meta:
        model = encoder.Comment
        exclude = ('commenter', 'last_modified_time', 'created_time', 'media')
