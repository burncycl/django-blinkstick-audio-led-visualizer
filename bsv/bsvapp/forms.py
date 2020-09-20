from django import forms


class MusicModeForm(forms.Form):    
    #test = forms.BooleanField(label='test', required=False, initial=False)
    flash = forms.BooleanField(label='flash', required=False, initial=False)
    pulse = forms.BooleanField(label='pulse', required=False, initial=False)
    loop = forms.BooleanField(label='loop', required=False, initial=False)
    minimum = forms.CharField(label='minimum')
    maximum = forms.CharField(label='maximum')

    def clean(self, *args, **kwargs):
        #test = self.cleaned_data.get('test')
        flash = self.cleaned_data.get('flash')
        pulse = self.cleaned_data.get('pulse')
        loop = self.cleaned_data.get('loop')                
        minimum = self.cleaned_data.get('minimum')
        maximum = self.cleaned_data.get('maximum')
        return super(MusicModeForm, self).clean(*args, **kwargs)
