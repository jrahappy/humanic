from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Opportunity, Chance
from customer.models import Company, CustomerLog
from .forms import OpportunityForm, ChanceForm
from collab.models import Refers
from collab.forms import ReportForm, ReferChangeStatus
from collab.views import create_history
import datetime
import json


def collab_kanban(request):
    refers = Refers.objects.all().order_by("-created_at")

    status_rq = refers.filter(status="Requested")
    status_sch = refers.filter(status="Scheduled")
    status_in = refers.filter(status="Interpreted")
    status_cosign = refers.filter(status="Cosigned")

    context = {
        "refers": refers,
        "status_rq": status_rq,
        "status_rq_count": status_rq.count(),
        "status_sch": status_sch,
        "status_sch_count": status_sch.count(),
        "status_in": status_in,
        "status_in_count": status_in.count(),
        "status_cosign": status_cosign,
        "status_cosign_count": status_cosign.count(),
    }
    return render(request, "crm/collab_kanban.html", context)


def collab(request):
    refers = Refers.objects.all().order_by("-created_at")
    context = {"refers": refers}
    return render(request, "crm/collab.html", context)


def partial_collab_kanban(request):
    refers = Refers.objects.all().order_by("-created_at")

    status_rq = refers.filter(status="Requested")
    status_sch = refers.filter(status="Scheduled")
    status_in = refers.filter(status="Interpreted")
    status_cosign = refers.filter(status="Cosigned")

    context = {
        "refers": refers,
        "status_rq": status_rq,
        "status_rq_count": status_rq.count(),
        "status_sch": status_sch,
        "status_sch_count": status_sch.count(),
        "status_in": status_in,
        "status_in_count": status_in.count(),
        "status_cosign": status_cosign,
        "status_cosign_count": status_cosign.count(),
    }
    return render(request, "crm/partial_collab_kanban.html", context)


def crm_refers(request):
    refers = Refers.objects.all().order_by("-created_at")
    context = {"refers": refers}
    return render(request, "crm/crm_refers.html", context)


def collab_refer_detail(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    company = refer.company
    illnesses = refer.referillness_set.all()
    simples = refer.refersimplediagnosis_set.all()
    history = refer.referhistory_set.all()

    context = {
        "refer": refer,
        "company": company,
        "illnesses": illnesses,
        "simples": simples,
        "history": history,
    }
    return render(request, "crm/collab_refer_detail.html", context)


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


def collab_report(request, refer_id):
    refer = get_object_or_404(Refers, id=refer_id)
    if request.method == "POST":
        form = ReportForm(request.POST, instance=refer)
        if form.is_valid():
            report = form.save(commit=False)
            report.provider = request.user
            report.opinioned_at = datetime.datetime.now()
            report.updated_at = datetime.datetime.now()
            report.save()
            # 로그 넣는 부분 추가 필요
            new_status = form.cleaned_data["status"]
            create_history(request, refer.id, new_status, "회송 완료")
            history = refer.referhistory_set.all()

            return render(
                request,
                "crm/partial_history_report.html",
                {
                    # "form": form,
                    "refer": refer,
                    "history": history,
                },
            )

            # return HttpResponse(
            #     status=204,
            #     headers={
            #         "HX-Trigger": json.dumps(
            #             {
            #                 "RefersChanged": None,
            #                 "showMessage": "Report Updated.",
            #             }
            #         )
            #     },
            # )
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
            created_at__gte=datetime.date.today() - datetime.timedelta(days=2),
            deleted_at=None,
        )
        .prefetch_related("company", "updated_by")
        .order_by("-created_at")
    )

    context = {
        "opps": opps,
        "chs": chs,
        "c_logs": c_logs,
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
