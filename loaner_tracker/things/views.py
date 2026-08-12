from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from . import forms
from django.contrib import messages
from django.urls import reverse
from django.contrib import auth
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View

from .models import Thing

class loginView(View): 
    def get(self, request):
        return render(request, "login.html", {"login_form": auth.forms.AuthenticationForm()})

    def post(self, request, *args, **kwargs):
        login_form = auth.forms.AuthenticationForm(data = request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")
            password = login_form.cleaned_data.get("password")
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect(request.GET.get("next", "home"))
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
        return render(request, "login.html", {"login_form": auth.forms.AuthenticationForm()})

class logoutView(LoginRequiredMixin, View):
    def get(self, request):
        auth.logout(request)
        return redirect("home")

class homeView(View):
    def get(self, request):
        return render(request, "home.html")

class thingListView(LoginRequiredMixin, View):    
    def get(self, request):
        context = {"title": "List"}
        barcode = request.GET.get("barcode", None)
        assigned_to = request.GET.get("assigned_to", None)

        if barcode is not None:
            context["things"] = Thing.objects.filter(barcode__exact=request.GET.get("barcode", ""))
            context["searched_by"] = "barcode"
            context["query"] = barcode
            if context["things"].count() == 1:
                return redirect("get_thing", id=context["things"].first().id)
        elif assigned_to is not None:
            if assigned_to == "":
                context["things"] = Thing.objects.filter(assigned_to__exact="")
            else:
                context["things"] = Thing.objects.filter(assigned_to__icontains=request.GET.get("assigned_to", ""))
            context["searched_by"] = "assigned to"
            context["query"] = assigned_to
        else:
            context["things"] = Thing.objects.all()

        return render(
            request,
            "list.html",
            context
        )
    

class thingDetailView(LoginRequiredMixin, View):
    # View
    def get(self, request, id):
        thing = Thing.objects.filter(pk=id).first()
        context = {
            "title": "Details",
            "form_disabled": True,
            "form_editable": True,
        }
        
        if thing:
            context["thing_form"] = forms.ThingForm(instance=thing)
            context["thing_form_ro"] = forms.ThingFormRO(instance=thing)
            return render(request, "detail.html", context)
        else:
            return redirect("list")

    # Update
    def post(self, request, id):
        if "editors" not in request.user.groups.all().values_list("name"):
            return HttpResponseForbidden("Not Authorized")

        thing = Thing.objects.filter(pk=id).first()
        context = {
            "title": "Details",
            "form_disabled": True,
            "form_editable": True,
        }

        thing_form = forms.ThingForm(request.POST, instance=thing)
        context["thing_form"] = thing_form
        if thing_form.has_changed():
            if thing_form.is_valid():
                newThing = thing_form.save()
                if newThing is None:
                    messages.error(request, "There was a problem saving")
                else:
                    new_form = forms.ThingForm(request.POST, instance=newThing)
                    # The form doesn't match the db after save
                    if new_form.has_changed():
                        messages.info(request, "There was a problem saving")
                    else:
                        messages.success(request, "Saved successfully")
            else:
                messages.error(request, thing_form.errors)
        else:
            messages.info(request, "No changes")

        context["thing_form"] = forms.ThingForm(instance=thing)
        context["thing_form_ro"] = forms.ThingFormRO(instance=thing)
        return render(request, "detail.html", context)

class thingAddView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        context = {
            "title": "New",
            "form_editable": False
        }

        barcode = request.GET.get("barcode", None)
        context["thing_form"] = forms.ThingForm(initial={'barcode': barcode})
        return render(request, "detail.html", context)
    
    def post(self, request):
        context = {
            "title": "New",
            "form_editable": False
        }

        thing = forms.ThingForm(request.POST)
        if thing.is_valid():
            newThing = thing.save()
            if newThing is None:
                messages.error(request, "There was a problem saving")
                context["thing_form"] = thing
            else:
                messages.success(request, "Successfully created " + newThing.barcode)
                context["thing_form"] = forms.ThingForm()
        else:
            messages.error(request, thing.errors)
            context["thing_form"] = thing
        return render(request, "detail.html", context)

    def test_func(self):
        return self.request.user.groups.filter(name='editors').exists()

class thingLookupView(LoginRequiredMixin, View):
    def get(self, request):
        barcode = request.GET.get("barcode", None)
        if barcode is not None:
            things = Thing.objects.filter(barcode__exact=barcode)
            if things.count() == 1:
                return redirect("get_thing", id=things.first().id)
            else:
                urlString = reverse("list") + "?barcode=" + barcode
        else:
            urlString = reverse("list") + "?barcode=" + barcode

        return redirect(urlString)


class thingDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(request, id):
        thing = Thing.objects.filter(pk=id).first()
        if thing:
            thing.delete()
            messages.success(request, "Successfully deleted " + thing.barcode)
        else:
            messages.error(request, "Thing not found")
        return redirect("list")

    def test_func(self):
        return self.request.user.groups.filter(name='staff').exists()

class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = auth.models.User
    template_name = "user_detail.html"

    # Add context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "auth.models.User Details"
        return context

    # Only allow user to see their own data
    def test_func(self):
        return self.request.user.pk == self.get_object().pk