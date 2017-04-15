import hashlib

from django import forms
from django.utils import crypto, timezone

from monki.boards.formatting import name_and_tripcode
from monki.boards.models import Post, Image, Video


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = [
            'file',
        ]


class VideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = [
            'file',
        ]


class PostForm(forms.ModelForm):
    ct_to_form = {
        'image/jpeg': ImageForm,
        'image/png': ImageForm,
        'image/gif': ImageForm,
        'video/mp4': VideoForm,
        'video/webm': VideoForm,
    }

    file = forms.FileField(required=False)

    class Meta:
        model = Post

        fields = [
            'board',
            'parent',
            'name',
            'email',
            'subject',
            'message',
            'file',
            'password',
        ]

        widgets = {
            'board': forms.HiddenInput(),
            'parent': forms.HiddenInput(),
            'password': forms.PasswordInput(render_value=True),
            'subject': forms.TextInput(attrs={'size': 35}),
            'message': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }

    def clean_board(self):
        data = self.cleaned_data['board']

        if data.locked:
            raise forms.ValidationError('This board is closed for new posts.')

        return data

    def clean_thread(self):
        data = self.cleaned_data.get('thread')

        if data.locked:
            raise forms.ValidationError('This thread is closed for new replies.')

        return data

    def clean_file(self):
        data = self.cleaned_data['file']

        if not data:
            return None  # early exit

        try:
            form_class = self.ct_to_form[data.content_type]
        except KeyError:
            raise forms.ValidationError(
                '%(content_type)s is not a valid file.',
                params={'content_type': data.content_type},
                code='invalid_file',
            )

        form = form_class(files={'file': data})

        if form.is_valid():
            obj = form.save(commit=False)
            obj.size = data.size
            obj.original_filename = data.name
            obj.checksum = hashlib.sha1(data.read()).hexdigest()

            return obj
        else:
            raise forms.ValidationError(
                'The uploaded file is invalid.',
                code='invalid_file',
            )

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get('file')
        message = cleaned_data.get('message')
        parent = cleaned_data.get('parent')

        if not parent and not file:
            raise forms.ValidationError('New thread requires a file.')

        if not file and not message:
            raise forms.ValidationError('You should provide at least a file or a message.')

        return cleaned_data

    def save(self, commit=False, *args, **kwargs):
        obj = super().save(commit=False, *args, **kwargs)

        if self.request.user.is_superuser:
            obj.ip_address = '::1'
            obj.user_agent = 'curl/7.51.0'
        else:
            obj.ip_address = self.request.META['REMOTE_ADDR']
            obj.user_agent = self.request.META['HTTP_USER_AGENT']

        obj.cid = self.request.get_signed_cookie('cid')

        obj.name, obj.tripcode = name_and_tripcode(self.cleaned_data.get('name'))

        if self.request.user.is_authenticated:
            obj.author = self.request.user

        if obj.parent:
            obj.parent.bumped_at = timezone.now()
            obj.parent.save()

        obj.save()

        attachment = self.cleaned_data.get('file')

        if attachment is not None:
            attachment.post = obj
            attachment.save()

        return obj
