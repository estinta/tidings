from django import forms

class BuildListForm(forms.Form):
    symbols = forms.CharField(widget=forms.Textarea, required=False,
            help_text="enter symbols, separated by spaces, tabs, and/or newlines")
    #upload_file = forms.FileField(required=False,
    #        help_text = "upload textfile containing symbols separated by whitespace")


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
        cleaned = build_list_form.cleaned_data
        symbols |= set(cleaned['symbols'].split())
        #if cleaned['upload_file']:
        #    symbols |= cleaned['upload_file'].read().split()
        request.session['symbols'] = symbols

    return symbols
