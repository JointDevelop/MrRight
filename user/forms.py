from django import forms
from user.models import User
from user.models import Profile


class UserForm(forms.ModelForm):
    '''User Form refer to User model'''

    class Meta:
        model = User
        fields = [
            'nickname',
            'gender',
            'birthday',
            'location'
        ]


class ProfileForm(forms.ModelForm):
    '''Profile Form refer to Profile model'''

    class Meta:
        model = Profile
        fields = '__all__'

    def clean_max_distance(self):
        '''make sure max_distance is larger than min_distance'''
        cleaned = super(ProfileForm, self).clean()
        if cleaned['max_distance'] >= cleaned['min_distance']:
            return cleaned['max_distance']
        else:
            raise forms.ValidationError('must make sure `max_distance` is larger than `min_distance`...')

    def clean_max_dating_age(self):
        '''make sure max_dating_age is larger than min_dating_age'''
        cleaned = super(ProfileForm, self).clean()
        if cleaned['max_dating_age'] >= cleaned['min_dating_age']:
            return cleaned['max_dating_age']
        else:
            raise forms.ValidationError('must make sure `max_dating_age` is larger than `min_dating_age`...')

