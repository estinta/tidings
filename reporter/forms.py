import re

from django import forms

class CheckupForm(forms.Form):
    '''In theory, this could be a ModelForm, but we want to make absolutely
    sure changes are never saved back to the underlying objects.'''
    ticker = forms.CharField(max_length=15)
    sector_rank = forms.CharField(max_length=15, required=False)
    eps = forms.CharField(max_length=15, required=False)
    eps_rank = forms.CharField(max_length=15, required=False)
    sales_percentage = forms.CharField(max_length=15, required=False)
    total_float = forms.CharField(max_length=15, required=False)
    comment = forms.CharField(max_length=255, required=False)
    verdict = forms.CharField(max_length=15, required=False)
    risk_percentage = forms.CharField(max_length=15, required=False)

class BuildListForm(forms.Form):
    symbols = forms.CharField(widget=forms.Textarea, required=False,
            help_text="enter symbols, separated by spaces, tabs, and/or newlines")

    def clean_symbols(self):
        # ensure our symbols are normalized in some fashion
        data = self.cleaned_data['symbols']
        return data.upper()

def process_build_list(request):
    '''
	Check the request for a build list; if found process it and update the
	session with the list of symbols. This function will always return the
	known list of stock symbols even if invoked without a form being present.
    '''
    symbols = request.session.get('symbols', set())

    if 'build_list' not in request.POST:
        return symbols

    build_list_form = BuildListForm(data=request.POST, files=request.FILES)
    if build_list_form.is_valid():
        cleaned = build_list_form.cleaned_data['symbols']
        new_symbols = re.findall(r'\w+', cleaned)
        symbols |= set(new_symbols)
        request.session['symbols'] = symbols

    return symbols

# vim: set ts=4 sw=4 et:
