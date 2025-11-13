from .tasks import activity_log_task

class ActivityLogMixin:
    module_name = None

    def log_activity(self, action_type, instance):
        company_id = None
        if hasattr(instance, "company_id"):
            company_id = instance.company_id
        elif hasattr(instance, "company") and instance.company:
            company_id = instance.company.id


        activity_log_task.delay(
            company_id=company_id,
            user_id=getattr(self.request.user, "id", None),
            module=self.module_name or instance.__class__.__name__,
            action_type=action_type,
            description=f"{action_type} {instance.__class__.__name__} {instance}",
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self.log_activity("Create", instance)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        self.log_activity("Update", instance)
        return instance

    def perform_destroy(self, instance):
        self.log_activity("Delete", instance)
        instance.delete()
