from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count, Q, Func
from django.db.models.functions import Collate
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from .models import Opportunity, Chance
from .forms import OpportunityForm, ChanceForm
from customer.models import Company, CustomerLog
from collab.models import Refers, ReferFile, ReferSimpleDiagnosis
from collab.forms import ReportForm, ReferChangeStatus, ReferFileForm
from collab.views import create_history
from .filters import RefersFilter, LogsFilter
import datetime
import json
from rich import print


def report_by_company(request):
    """
    A view to generate a report by company.
    """

    current_month = timezone.now().month
    current_year = timezone.now().year

    pre_month = current_month - 1 if current_month > 1 else 12
    pre_year = current_year if current_month > 1 else current_year - 1

    ko_kr = Func(
        "business_name",
        function="ko_KR.utf8",
        template='(%(expressions)s) COLLATE "%(function)s"',
    )

    # companies = (
    #     Company.objects.filter(is_collab_contract=True)
    #     .annotate(
    #         refers_count=Count(
    #             "refers",
    #             filter=Q(
    #                 refers__referred_date__month=current_month,
    #                 refers__referred_date__year=current_year,
    #             )
    #             & ~Q(refers__status="Draft"),
    #         ),
    #     )  # Remove the extra closing parenthesis here
    #     .annotate(
    #         pre_refers_count=Count(
    #             "refers",
    #             filter=Q(
    #                 refers__referred_date__month=pre_month,
    #                 refers__referred_date__year=pre_year,
    #             )
    #             & ~Q(refers__status="Draft"),
    #         ),
    #     )
    #     .order_by(ko_kr.asc())
    # )

    companies = (
        Company.objects.filter(is_collab_contract=True)
        .annotate(
            refers_count=Count(
                "refers",
                filter=Q(
                    refers__cosigned_at__month=current_month,
                    refers__cosigned_at__year=current_year,
                )
                & ~Q(refers__status="Draft"),
            ),
        )  # Remove the extra closing parenthesis here
        .annotate(
            pre_refers_count=Count(
                "refers",
                filter=Q(
                    refers__cosigned_at__month=pre_month,
                    refers__cosigned_at__year=pre_year,
                )
                & ~Q(refers__status="Draft"),
            ),
        )
        .order_by(ko_kr.asc())
    )

    # print(companies, "companies")

    if not companies:
        return HttpResponse("No company found for the user.", status=404)

    context = {
        "companies": companies,
        "current_month": current_month,
        "current_year": current_year,
        "pre_month": pre_month,
        "pre_year": pre_year,
    }
    return render(request, "crm/report_by_company.html", context)


def refers_by_company_monthly(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    s_month = request.GET.get("s_month", "")
    if s_month:
        s_month = int(s_month)
    else:
        s_month = timezone.now().month
    s_year = request.GET.get("s_year", "")
    if s_year:
        s_year = int(s_year)
    else:
        s_year = timezone.now().year

    today = timezone.now().date()
    today_month = today.month
    one_month_before = today - relativedelta(months=1)
    two_months_before = today - relativedelta(months=2)

    print(
        today,
        one_month_before,
        two_months_before,
        "today, one_month_before, two_months_before",
    )

    selected_date = datetime.date(s_year, s_month, 1)
    start_date = selected_date
    last_date = (selected_date + datetime.timedelta(days=31)).replace(
        day=1
    ) - datetime.timedelta(days=1)

    # print(start_date, last_date, "start_date, last_date")
    s_month = selected_date.month
    s_year = selected_date.year
    refers = (
        Refers.objects.filter(
            company=company, cosigned_at__gte=start_date, cosigned_at__lte=last_date
        )
        .exclude(status="Draft")
        .order_by("-cosigned_at")
    )

    refer_count = refers.count()

    rsd = (
        ReferSimpleDiagnosis.objects.filter(refer__in=refers)
        .values(
            "diagnosis__code1",
            "diagnosis__code2",
            "diagnosis__code3",
            "diagnosis__code4",
        )
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    rsd_count = ReferSimpleDiagnosis.objects.filter(refer__in=refers).count()

    context = {
        "company": company,
        "refers": refers,
        "refer_count": refer_count,
        "rsd": rsd,
        "rsd_count": rsd_count,
        "s_month": s_month,
        "s_year": s_year,
        "today": today,
        "one_month_before": one_month_before,
        "two_months_before": two_months_before,
    }
    return render(request, "crm/refers_by_company_monthly.html", context)


def collab_refer_file_upload(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    if request.method == "POST":
        form = ReferFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("file")
            if len(files) > 200:
                return HttpResponse(
                    status=400,
                    headers={
                        "HX-Trigger": json.dumps(
                            {
                                "showMessage": "You can upload a maximum of 200 files.",
                            }
                        )
                    },
                )
            for file in files:
                ReferFile.objects.create(refer=refer, file=file)
                # referfile.objects.create(refer=refer, file=file)

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "ReferFilesChanged": None,
                            "showMessage": "File Uploaded.",
                        }
                    )
                },
            )
        else:
            print(form.errors)

    else:
        form = ReferFileForm()
        context = {"form": form, "refer": refer}
        return render(request, "crm/collab_refer_file_upload.html", context)


def collab_refer_file_delete(request, file_id):
    file = get_object_or_404(ReferFile, id=file_id)
    refer = file.refer
    file.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "ReferFilesChanged": None,
                    "showMessage": "File Deleted.",
                }
            )
        },
    )


def collab_refer_file_delete_all(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    files = ReferFile.objects.filter(refer=refer)
    files.delete()
    return HttpResponse(
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "ReferFilesChanged": None,
                    "showMessage": "All Files Deleted.",
                }
            )
        },
    )


def collab_refer_files(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    files = ReferFile.objects.filter(refer=refer)
    # files_list = [{"path": file.file.path, "name": file.file.name} for file in files]
    # print(files_list, "test")
    # print(files)
    context = {"refer": refer, "files": files}
    return render(request, "crm/collab_refer_files.html", context)


def collab_kanban(request):
    q = request.GET.get("q", "")
    if q:
        refers = (
            Refers.objects.filter(patient_name__icontains=q)
            .exclude(status="Draft")
            .select_related("company")
            .order_by("-created_at")
        )
    else:
        refers = (
            Refers.objects.exclude(status="Draft")
            .select_related("company")
            .order_by("-created_at")
        )

    status_rq = refers.filter(status="Requested")
    status_sch = refers.filter(status="Scheduled")
    status_in = refers.filter(status="Interpreted")
    status_cosign = refers.filter(status="Cosigned")
    status_cancelled = refers.filter(status="Cancelled")[:5]

    context = {
        "refers": refers,
        "status_rq": status_rq,
        "status_sch": status_sch,
        "status_in": status_in,
        "status_cosign": status_cosign,
        "status_cancelled": status_cancelled,
        "q": q,
    }
    return render(request, "crm/collab_kanban.html", context)


def collab(request):
    # q = request.GET.get("q", "")
    # if q:
    #     refers = (
    #         Refers.objects.filter(patient_name__icontains=q)
    #         .exclude(status="Draft")
    #         .select_related("company")
    #         .order_by("-created_at")
    #     )
    # else:
    #     refers = (
    #         Refers.objects.filter(~Q(status="Draft"))
    #         .select_related("company")
    #         .order_by("-created_at")
    #     )

    refers = Refers.objects.all().exclude(status="Draft").order_by("-created_at")
    refers_filter = RefersFilter(request.GET, queryset=refers)
    refers = refers_filter.qs

    paginator = Paginator(refers, 25)  # Show 10 refers per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"refers": refers, "page_obj": page_obj, "filter": refers_filter}

    return render(request, "crm/collab.html", context)


def partial_collab_kanban(request):
    refers = Refers.objects.all().exclude(status="Draft").order_by("-created_at")

    status_rq = refers.filter(status="Requested")
    status_sch = refers.filter(status="Scheduled")
    status_in = refers.filter(status="Interpreted")
    status_cosign = refers.filter(status="Cosigned")
    # status_cancelled = refers.filter(status="Cancelled")[0:5]
    context = {
        "refers": refers,
        "status_rq": status_rq,
        "status_sch": status_sch,
        "status_in": status_in,
        "status_cosign": status_cosign,
        # "status_cancelled": status_cancelled,
        # "status_rq_count": status_rq.count(),
        # "status_sch_count": status_sch.count(),
        # "status_in_count": status_in.count(),
        # "status_cosign_count": status_cosign.count(),
    }
    return render(request, "crm/partial_collab_kanban.html", context)


def crm_refers(request):
    refers = Refers.objects.filter(status="Requested").order_by("-created_at")
    refers = Refers.objects.all().order_by("-created_at")
    context = {"refers": refers}
    return render(request, "crm/crm_refers.html", context)


def collab_refer_archive(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    refer.status = "Archived"
    refer.updated_at = datetime.datetime.now()
    refer.save()
    create_history(request, refer.id, "Archived", "Archived")
    return redirect("crm:collab_kanban")


def collab_refer_detail(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    company = refer.company
    illnesses = refer.referillness_set.all()
    simples = refer.refersimplediagnosis_set.all()
    history = refer.referhistory_set.all()
    # files = refer.referfile_set.all()
    files = ReferFile.objects.filter(refer=refer)
    # files_list = [[file.file.name] for file in files]
    # print(files_list, "test")
    print(files)
    context = {
        "refer": refer,
        "company": company,
        "illnesses": illnesses,
        "simples": simples,
        "history": history,
        "files": files,
        # "files_list": files_list,
    }
    return render(request, "crm/collab_refer_detail.html", context)


def dicom_viewer(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    files = ReferFile.objects.filter(refer=refer)
    files_list = [
        f"https://humanicfiles.s3.us-east-2.amazonaws.com/{file.file}" for file in files
    ]
    # files_list = html.unescape(str(files_list))
    # files_list = f"params = [{files_list}]"

    print(files_list, "test")

    context = {
        "refer": refer,
        "files": files,
        "files_list": files_list,
    }
    return render(request, "collab/dicom_viewer.html", context)


def collab_reschedule(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    refer.status = "Scheduled"
    # refer.opinioned_at = datetime.datetime.now()
    # refer.updated_at = datetime.datetime.now()
    refer.save()
    create_history(request, refer.id, "Scheduled", "재 예약처리")
    return redirect("crm:collab_kanban")


def collab_schedule_one(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    refer.status = "Scheduled"
    refer.scheduled_at = datetime.datetime.now()
    refer.updated_at = datetime.datetime.now()
    refer.save()
    create_history(request, refer.id, "Scheduled", "간편예약 처리")
    return redirect("crm:collab_kanban")


def collab_schedule(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    if request.method == "POST":
        form = ReferChangeStatus(request.POST, instance=refer)
        # print(form)
        if form.is_valid():
            report = form.save(commit=False)
            report.updated_at = datetime.datetime.now()
            # report.status = form.cleaned_data["status"]
            report.save()
            new_status = form.cleaned_data["status"]
            scheduled_at = form.cleaned_data["scheduled_at"]
            # 로그 넣는 부분 추가 필요
            create_history(request, refer.id, new_status, "예약 완료")
            history = refer.referhistory_set.all()

            return render(
                request,
                "crm/partial_history.html",
                {
                    "form": form,
                    "refer": refer,
                    "history": history,
                    "scheduled_at": scheduled_at,
                },
            )

        else:
            print(form.errors)
            # return HttpResponse(
            #     status=400,
            #     headers={
            #         "HX-Trigger": json.dumps(
            #             {
            #                 "showMessage": "Error Updating Report.",
            #             }
            #         )
            #     },
            # )
    else:
        form = ReferChangeStatus(instance=refer)
        context = {
            "form": form,
            "refer": refer,
        }

    return render(request, "crm/collab_schedule.html", context)


def collab_report_one(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    refer.status = "Interpreted"
    refer.opinioned_at = datetime.datetime.now()
    refer.updated_at = datetime.datetime.now()
    refer.save()
    create_history(request, refer.id, "Interpreted", "간편회송서 처리")
    return redirect("crm:collab_kanban")


def collab_report(request, refer_id):
    user = request.user
    is_doctor = user.is_doctor
    refer = get_object_or_404(Refers, id=refer_id)
    simples = ReferSimpleDiagnosis.objects.filter(refer=refer)
    count_simples = simples.count()
    print(count_simples, "count_simples")

    if request.method == "POST":
        form = ReportForm(request.POST, instance=refer)
        if form.is_valid():
            report = form.save(commit=False)
            if is_doctor:
                report.provider = request.user
                report.radio_doctor = request.user.first_name
            else:
                report.provider = None

            # report.collab_price = form.cleaned_data["readprice"] / 2
            report.opinioned_at = datetime.datetime.now()
            report.updated_at = datetime.datetime.now()
            report.save()
            # 로그 넣는 부분 추가 필요
            new_status = form.cleaned_data["status"]
            create_history(request, refer.id, new_status, "회송 완료")
            history = refer.referhistory_set.all()
            illnesses = refer.referillness_set.all()

            return render(
                request,
                "crm/partial_history_report.html",
                {
                    # "form": form,
                    "refer": refer,
                    "history": history,
                    "illnesses": illnesses,
                },
            )

        else:
            print(form.errors)
            return HttpResponse(
                status=400,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "showMessage": "Error Updating Report.",
                        }
                    )
                },
            )
    else:
        form = ReportForm(instance=refer)
        context = {
            "form": form,
            "refer": refer,
            "count_simples": count_simples,
        }

    return render(request, "crm/collab_report.html", context)


def chances(request):
    chs = Chance.objects.all().order_by("-created_at")[0:20]
    context = {
        "chs": chs,
    }
    return render(request, "crm/chances.html", context)


def new_chance(request):

    if request.method == "POST":
        form = ChanceForm(request.POST)
        if form.is_valid():
            new_chance = form.save(commit=False)
            new_chance.agent = request.user
            new_chance.save()

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "ChancesChanged": None,
                            "showMessage": "Chance Added.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
            return HttpResponse(
                status=400,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "showMessage": "Error Adding Chance.",
                        }
                    )
                },
            )
    else:
        form = ChanceForm()
        context = {
            "form": form,
            "agent": request.user,
        }

    return render(request, "crm/new_chance.html", context)


def delete_chance(request, chance_id):
    # chance = get_object_or_404(Chance, id=chance_id)
    chance = Chance.objects.filter(id=chance_id)

    # print(chance.count())
    chance.delete()
    # print("Chance Deleted: ", chance_id)
    return HttpResponse(
        json.dumps({"message": "Chance Deleted."}),
        content_type="application/json",
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "ChancesChanged": None,
                    "showMessage": "Chance Deleted.",
                }
            )
        },
    )


def edit_chance(request, chance_id):
    chance = get_object_or_404(Chance, id=chance_id)
    agent = request.user

    if request.method == "POST":
        form = ChanceForm(request.POST, instance=chance)
        if form.is_valid():
            chance = form.save(commit=False)
            chance.agent = agent
            chance.save()

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "ChancesChanged": None,
                            "showMessage": "Chance Updated.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
            return HttpResponse(
                status=400,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "showMessage": "Error Updating Chance.",
                        }
                    )
                },
            )
    else:
        form = ChanceForm(instance=chance)
        context = {
            "form": form,
            "agent": request.user,
            "chance": chance,
        }

    return render(request, "crm/edit_chance.html", context)


def index(request):
    opps = (
        Opportunity.objects.all()
        .prefetch_related("company")
        .order_by("-created_at")[:20]
    )
    chs = Chance.objects.all().order_by("-created_at")[:20]

    c_logs = (
        CustomerLog.objects.filter(
            # created_at__gte=datetime.date.today() - datetime.timedelta(days=2),
            deleted_at=None,
        )
        .prefetch_related("company", "updated_by")
        .order_by("-created_at")
    )

    log_filter = LogsFilter(request.GET, queryset=c_logs)
    c_logs = log_filter.qs[:50]

    context = {
        "opps": opps,
        "chs": chs,
        "c_logs": c_logs,
        "filter": log_filter,
    }

    return render(request, "crm/index.html", context)


def new_opp(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == "POST":
        form = OpportunityForm(request.POST)
        if form.is_valid():
            new_opp = form.save(commit=False)
            new_opp.company = company
            # new_opp.agent = request.user
            new_opp.save()

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "OppsChanged": None,
                            "showMessage": "Opportunity Added.",
                        }
                    )
                },
            )
        else:
            print(form.errors)

            return render(
                request,
                "crm/new_opp.html",
                {"form": form, "company": company, "agent": request.user},
            )
    else:
        form = OpportunityForm()
        context = {
            "form": form,
            # "agent": request.user,
            "company": company,
        }

    return render(request, "crm/new_opp.html", context)


def opps(request):
    opps = Opportunity.objects.all().order_by("-created_at")
    context = {
        "opps": opps,
    }
    return render(request, "crm/opps.html", context)


def opp(request, opp_id):
    opp = get_object_or_404(Opportunity, id=opp_id)
    context = {
        "opp": opp,
    }
    return render(request, "crm/opp.html", context)


def opps_customer(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    opps = Opportunity.objects.filter(company=company).order_by("-created_at")

    context = {
        "company": company,
        # "agent": request.user,
        "opps": opps,
    }
    return render(request, "crm/opps.html", context)


def edit_opp(request, opp_id):
    opp = get_object_or_404(Opportunity, id=opp_id)
    company = opp.company
    # agent = request.user

    if request.method == "POST":
        form = OpportunityForm(request.POST, instance=opp)
        if form.is_valid():
            opp = form.save(commit=False)
            # opp.agent = agent
            opp.company = company
            opp.save()

            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "OppsChanged": None,
                            "showMessage": "Opportunity Updated.",
                        }
                    )
                },
            )
        else:
            print(form.errors)
            return HttpResponse(
                status=400,
                headers={
                    "HX-Trigger": json.dumps(
                        {
                            "showMessage": "Error Updating Opportunity.",
                        }
                    )
                },
            )
    else:
        form = OpportunityForm(instance=opp)
        context = {
            "form": form,
            # "agent": request.user,
            "company": opp.company,
            "opp": opp,
        }

    return render(request, "crm/edit_opp.html", context)


def delete_opp(request, opp_id):
    # opp = get_object_or_404(Opportunity, id=opp_id)
    opp = Opportunity.objects.filter(id=opp_id)

    # print(opp.count())
    opp.delete()
    # print("Opportunity Deleted: ", opp_id)
    return HttpResponse(
        json.dumps({"message": "Opportunity Deleted."}),
        content_type="application/json",
        status=204,
        headers={
            "HX-Trigger": json.dumps(
                {
                    "OppsChanged": None,
                    "showMessage": "Opportunity Deleted.",
                }
            )
        },
    )
