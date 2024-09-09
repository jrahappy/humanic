# Create your views here.
from django.contrib.auth.models import User
from accounts.models import CustomUser, Profile
from customer.models import Company
from importdata.models import temp_doctor_table
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def index(request):

    doctors = CustomUser.objects.filter(is_staff=False).select_related("profile")
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
