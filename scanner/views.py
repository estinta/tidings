from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from .models import UserProfile
from .forms import UserProfileForm
from .utils import validate_ibd, validate_briefing

@login_required
def edit_profile(request):
    prof = request.user.get_profile()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=prof)
        if form.is_valid():
            # ensure we only edit our own
            up = form.save(commit=False)
            up.user = request.user
            up.save()
            if 'validate' not in request.POST:
                next = request.GET.get('next') or '/'
            else:
                next = request.path + '?check=true'
            return redirect(next)
    else:
        form = UserProfileForm(instance=prof)

    ctx = { 'form': form }
    if 'check' in request.GET:
        ctx['ibd_status'] = validate_creds(validate_ibd,
                prof.ibd_user, prof.ibd_password)
        ctx['briefing_status'] = validate_creds(validate_briefing,
                prof.briefing_user, prof.briefing_password)
        ctx['status_check'] = True

    return render_to_response('registration/profile.html',
            RequestContext(request, ctx))

def validate_creds(func, username, password):
    success = func(username, password)
    if success is None:
        return "No Credentials"
    if success:
        return "Valid Credentials"
    return "Invalid Credentials"

# vim: set ts=4 sw=4 et:
