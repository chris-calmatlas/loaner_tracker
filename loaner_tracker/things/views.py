from django.shortcuts import render, redirect
from .forms import ThingForm, ThingFormRO
from django.contrib import messages

from .models import Thing

def login(request):
    return render(request, "login.html")

def home(request):
    return redirect("lookup", permanent=True)

def lookup(request):
    if request.method == "GET":
        context = {"title": "Lookup"}
        barcode = request.GET.get("barcode", None)
        assigned_to = request.GET.get("assigned_to", None)

        if barcode is not None:
            context["things"] = Thing.objects.filter(barcode__exact=request.GET.get("barcode", ""))
            context["searched_by"] = "barcode"
            context["query"] = barcode
            if context["things"].count() == 1:
                return redirect("get_thing", id=context["things"].first().id, permanent=True)
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
            "lookup.html",
            context
        )

def get_thing(request, id):
    thing = Thing.objects.filter(pk=id).first()
    context = {
        "title": "Details",
        "form_disabled": True,
        "form_editable": True,
    }
    
    if request.method == "GET":
        if thing:
            context["thing_form"] = ThingForm(instance=thing)
            context["thing_form_ro"] = ThingFormRO(instance=thing)
            return render(request, "detail.html", context)
        else:
            messages.error(request, "No thing found with id " + str(id))
            return redirect("lookup", permanent=True)

    if request.method == "POST":
        thing_form = ThingForm(request.POST, instance=thing)
        context["thing_form"] = thing_form
        if thing_form.has_changed():
            if thing_form.is_valid():
                newThing = thing_form.save()
                if newThing is None:
                    messages.error(request, "There was a problem saving")
                else:
                    if thing is newThing:
                        messages.info(request, "No changes")
                    else:
                        messages.success(request, "Saved")
            else:
                messages.error(request, thing_form.errors)
        else:
            messages.info(request, "No changes")

        context["thing_form"] = ThingForm(instance=thing)
        context["thing_form_ro"] = ThingFormRO(instance=thing)
        return render(request, "detail.html", context)

def add_thing(request):
    context = {
        "title": "New",
        "form_editable": False
    }

    if request.method == "GET":
        barcode = request.GET.get("barcode", None)
        thingForm = ThingForm(initial={'barcode': barcode})
        context["thing_form"] = thingForm
        return render(request, "detail.html", context)
    
    if request.method == "POST":
        thing = ThingForm(request.POST)
        if thing.is_valid():
            newThing = thing.save()
            if newThing is None:
                messages.error(request, "There was a problem saving")
                context["thing_form"] = thing
            else:
                messages.success(request, "Successfully created " + newThing.barcode)
                context["thing_form"] = ThingForm()
        else:
            messages.error(request, thing.errors)
            context["thing_form"] = thing
        return render(request, "detail.html", context)