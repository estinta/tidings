from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from .models import UserProfile
from .forms import UserProfileForm
from .utils import validate_credentials

@login_required
def edit_profile(request):
    prof = request.user.get_profile()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=prof)
        if form.is_valid():
            # ensure we only edit our own
            up = form.save(commit=False)
            up.user = request.user
            validate_credentials(up, save=False)
            up.save()
            return redirect(request.path)
    else:
        form = UserProfileForm(instance=prof)

    ctx = {
        'form': form,
        'ibd_status': status(prof.ibd_valid),
        'briefing_status': status(prof.briefing_valid),
    }

    return render_to_response('registration/profile.html',
            RequestContext(request, ctx))

def status(success):
    if success is None:
        return "No Credentials"
    if success:
        return "Valid Credentials"
    return "Invalid Credentials"

# vim: set ts=4 sw=4 et:
