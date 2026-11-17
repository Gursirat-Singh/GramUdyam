from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from accounts.forms import EntrepreneurRegistrationForm, UserProfileForm
from accounts.models import UserProfile


def ensure_user_profile(user):
    '''Ensures a UserProfile record exists for the given authenticated user.'''
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "state": "Punjab",
            "district": "Ludhiana",
            "village_or_town": "Samrala",
            "available_capital": Decimal("50000.00"),
        },
    )
    return profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    if request.method == "POST":
        form = EntrepreneurRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome, {user.get_short_name()}! Your entrepreneur profile has been created.",
            )
            return redirect("dashboard:index")
        messages.error(request, "Please correct the highlighted errors in the registration form.")
    else:
        form = EntrepreneurRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    profile = ensure_user_profile(request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your entrepreneur profile and capital settings have been updated.")
            return redirect("accounts:profile")
        messages.error(request, "Please check the form for invalid inputs.")
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "profile": profile,
        },
    )


class EntrepreneurLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class EntrepreneurLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class EntrepreneurPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    success_url = reverse_lazy("accounts:password_reset_done")


class EntrepreneurPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"
