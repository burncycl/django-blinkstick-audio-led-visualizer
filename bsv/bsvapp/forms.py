from django import forms


class MusicModesForm(forms.Form):
    all_modes = forms.BooleanField(label='all_modes', required=False, initial=False)
    flash = forms.BooleanField(label='flash', required=False, initial=False)
    pulse = forms.BooleanField(label='pulse', required=False, initial=False)
    loop = forms.BooleanField(label='loop', required=False, initial=False)
    minimum = forms.CharField(label='minimum')
    maximum = forms.CharField(label='maximum')

class ColorModesForm(forms.Form):
    single_mode = forms.BooleanField(label='single_mode', required=False, initial=False)
    blink_mode = forms.BooleanField(label='blink_mode', required=False, initial=False)
    duration = forms.CharField(label='duration')
    blink_duration = forms.CharField(label='blink_duration')
    morph_mode = forms.BooleanField(label='morph_mode', required=False, initial=False)
    flow = forms.BooleanField(label='flow', required=False, initial=False)    
    sine = forms.BooleanField(label='sine', required=False, initial=False)
    leap = forms.BooleanField(label='leap', required=False, initial=False)
    rev = forms.BooleanField(label='rev', required=False, initial=False)
    blink = forms.BooleanField(label='blink', required=False, initial=False)
    brightness = forms.CharField(label='brightness')
    FF0063 = forms.BooleanField(label='FF0063', required=False, initial=False)
    FF005E = forms.BooleanField(label='FF005E', required=False, initial=False)
    FF0003 = forms.BooleanField(label='FF0003', required=False, initial=False)
    FF0000 = forms.BooleanField(label='FF0000', required=False, initial=False)
    FF5C00 = forms.BooleanField(label='FF5C00', required=False, initial=False)
    FF6000 = forms.BooleanField(label='FF6000', required=False, initial=False)
    FF7F00 = forms.BooleanField(label='FF7F00', required=False, initial=False)
    FFBC00 = forms.BooleanField(label='FFBC00', required=False, initial=False)
    FFC000 = forms.BooleanField(label='FFC000', required=False, initial=False)
    FFFF00 = forms.BooleanField(label='FFFF00', required=False, initial=False)
    E1FF00 = forms.BooleanField(label='E1FF00', required=False, initial=False)
    _81FF00 = forms.BooleanField(label='_81FF00', required=False, initial=False)
    _21FF00 = forms.BooleanField(label='_21FF00', required=False, initial=False)
    _00FF00 = forms.BooleanField(label='_00FF00', required=False, initial=False)    
    _00FF9E = forms.BooleanField(label='_00FF9E', required=False, initial=False)
    _00FFFD = forms.BooleanField(label='_00FFFD', required=False, initial=False)
    _00A0FF = forms.BooleanField(label='_00A0FF', required=False, initial=False)
    _0040FF = forms.BooleanField(label='_0040FF', required=False, initial=False)
    _0000FF = forms.BooleanField(label='_0000FF', required=False, initial=False)
    _1F00FF = forms.BooleanField(label='_1F00FF', required=False, initial=False)
    _7F00FF = forms.BooleanField(label='_7F00FF', required=False, initial=False)
    _4B0082 = forms.BooleanField(label='_4B0082', required=False, initial=False)
    _9400D3 = forms.BooleanField(label='_9400D3', required=False, initial=False)
    DF00FF = forms.BooleanField(label='DF00FF', required=False, initial=False)
    FF00C3 = forms.BooleanField(label='FF00C3', required=False, initial=False)
    FF00BE = forms.BooleanField(label='FF00BE', required=False, initial=False)
    CCCCCC = forms.BooleanField(label='CCCCCC', required=False, initial=False)
    FFFFFF = forms.BooleanField(label='FFFFFF', required=False, initial=False)
    
class ColorProgramsForm(forms.Form):
    rotating_rainbow = forms.BooleanField(label='rotating_rainbow', required=False, initial=False)
    rainbow_snake = forms.BooleanField(label='rainbow_snake', required=False, initial=False)
    breathing = forms.BooleanField(label='breathing', required=False, initial=False)
    snow_storm = forms.BooleanField(label='snow_storm', required=False, initial=False)
    rain_storm = forms.BooleanField(label='rain_storm', required=False, initial=False)
    fire_flies = forms.BooleanField(label='fire_flies', required=False, initial=False)
    fire = forms.BooleanField(label='fire', required=False, initial=False)
    stripes = forms.BooleanField(label='stripes', required=False, initial=False)
    clear_sky = forms.BooleanField(label='clear_sky', required=False, initial=False)
    cloudy_sky = forms.BooleanField(label='cloudy_sky', required=False, initial=False)
    stars = forms.BooleanField(label='stars', required=False, initial=False)
    