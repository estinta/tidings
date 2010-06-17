from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from .models import UserProfile
from .forms import UserProfileForm

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
            next = request.GET.get('next') or '/'
            return redirect(next)
    else:
        form = UserProfileForm(instance=prof)

    return render_to_response('registration/profile.html',
            RequestContext(request, { 'form': form }))

