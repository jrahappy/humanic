# Create your views here.
from django.contrib.auth.models import User
from accounts.models import CustomUser, Profile
from customer.models import Company
from importdata.models import temp_doctor_table
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q


def index(request):

    q = request.GET.get("q")
    if q:
        doctors = (
            CustomUser.objects.filter(
                Q(profile__real_name__icontains=q)
                | Q(profile__specialty2__icontains=q)
                | Q(profile__email__icontains=q)
                | Q(profile__cv3_id__icontains=q)
                | Q(profile__onpacs_id__icontains=q)
            )
            .filter(is_staff=False)
            .select_related("profile")
            .order_by("profile__real_name")
        )
    else:
        doctors = (
            CustomUser.objects.filter(is_staff=False)
            .select_related("profile")
            .order_by("-username")
        )
        # update_profile = Profile.objects.filter(specialty2="신경두경부").update(
        #     specialty2="신경두경"
        # )

    paginator = Paginator(doctors, 10)  # Show 10 doctors per page
    page = request.GET.get("page")

    try:
        doctors = paginator.page(page)
    except PageNotAnInteger:
        doctors = paginator.page(1)
    except EmptyPage:
        doctors = paginator.page(paginator.num_pages)

    context = {"doctors": doctors}
    return render(request, "provider/index.html", context)


def new_provider(request):

    return render(request, "provider/new_provider.html")


def view_provider(request, id):
    provider = CustomUser.objects.select_related("profile").get(pk=id)
    print(provider.profile.real_name)
    return render(request, "provider/view_provider.html", {"provider": provider})


def rawdata(request):
    rawdata = temp_doctor_table.objects.all()
    context = {"rawdata": rawdata}
    return render(request, "provider/rawdata.html", context)


def create_user_rawdata(request):
    rawdata = temp_doctor_table.objects.all()
    company = Company.objects.get(pk=1)
    created_users = []

    # try:
    #     with transaction.atomic():
    #         for record in rawdata:
    #             user = CustomUser.objects.create_user(
    #                 username=record.doctor_id,
    #                 email=record.email,
    #                 password=record.doctor_id,
    #             )
    #             Profile.objects.create(
    #                 user=user,
    #                 real_name=record.name,
    #                 specialty1=record.department,
    #                 specialty2=record.specialty,
    #                 position=record.position,
    #                 email=record.email,
    #                 cv3_id=record.cv3_id,
    #                 onpacs_id=record.onpacs_id,
    #                 company=company,
    #                 fee_rate=record.fee_rate,
    #             )
    #             created_users.append(user)
    #         # rawdata.delete()
    # except Exception as e:
    #     messages.error(request, f"Error creating user {record.name}: {e}")

    for record in rawdata:
        try:
            user = CustomUser.objects.create_user(
                username=record.doctor_id,
                email=record.email,
                password=record.doctor_id,
            )
            Profile.objects.create(
                user=user,
                real_name=record.name,
                specialty1=record.department,
                specialty2=record.specialty,
                position=record.position,
                email=record.email,
                cv3_id=record.cv3_id,
                onpacs_id=record.onpacs_id,
                company=company,
                fee_rate=record.fee_rate,
            )
            created_users.append(user)
            # rawdata.delete()
        except Exception as e:
            messages.error(request, f"Error creating user {record.name}: {e}")

    context = {"created_users": created_users, "recordname": record.name}
    return render(request, "provider/result.html", context)


def update_profile(request):
    profiles = Profile.objects.all()
    company = Company.objects.get(pk=1)

    try:
        with transaction.atomic():
            for profile in profiles:
                try:
                    rawdata = temp_doctor_table.objects.get(
                        doctor_id=profile.user.username
                    )

                    # Update profile fields
                    profile.real_name = rawdata.name
                    profile.specialty1 = rawdata.department
                    profile.specialty2 = rawdata.specialty
                    profile.position = rawdata.position
                    profile.email = rawdata.email
                    profile.cv3_id = rawdata.cv3_id
                    profile.onpacs_id = rawdata.onpacs_id
                    profile.company = company
                    profile.fee_rate = rawdata.fee_rate
                    profile.save()
                except temp_doctor_table.DoesNotExist:
                    messages.error(
                        request,
                        f"No matching record found in temp_doctor_table for user {profile.user.username}",
                    )

    except Exception as e:
        messages.error(request, f"Error updating profiles: {e}")

    return redirect("provider:index")
