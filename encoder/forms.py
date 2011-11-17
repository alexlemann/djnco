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


class CommentNotificationForm(forms.ModelForm):

    def __init__(self, request, comment, *args, **kwargs):
        result = super(CommentNotificationForm, self).__init__(*args, **kwargs)
        #can't notify myself
        self.fields['receiver'].queryset = self.fields['receiver'].queryset.exclude(username=request.user.username)
        #can't notify already notified users
        notified = [n.receiver.username for n in comment.notifications.all()]
        self.fields['receiver'].queryset = self.fields['receiver'].queryset.exclude(username__in=notified)
        self.fields['receiver'].label = ''
        return result

    class Meta:
        model = encoder.CommentNotification
        exclude = ('comment', 'created_time', 'seen_time', 'sender')
