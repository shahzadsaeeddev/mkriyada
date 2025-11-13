from celery import shared_task




@shared_task
def activity_log_task(company_id, user_id, action_type, module, description, ip_address):
    from .models import ActivityLog
    from accounts.models import Users
    from api.models import Company

    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return

    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        user = None

    ActivityLog.objects.create(
        company=company,
        user=user,
        action_type=action_type,
        module=module,
        description=description,
        ip_address=ip_address,
    )

