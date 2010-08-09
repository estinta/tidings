from django import forms

import re

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

    # backward-compatibility code- make sure all symbols are upper-case
    correct_symbols = set()
    for s in symbols:
        correct_symbols.add(s.upper())
    if symbols != correct_symbols:
        request.session['symbols'] = correct_symbols
        symbols = correct_symbols

    if 'build_list' not in request.POST:
        return symbols

    build_list_form = BuildListForm(data=request.POST, files=request.FILES)
    if build_list_form.is_valid():
        cleaned = build_list_form.cleaned_data['symbols']
        new_symbols = re.findall(r'\w+', cleaned)
        symbols |= set(new_symbols)
        request.session['symbols'] = symbols

    return symbols
