from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models, router
from django.utils import timezone

from account.manager import CustomManager, SoftDeleteManager
from account.utils import phone_number_regex


# Create your models here.
class SoftDeleteBaseModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)

    objects = SoftDeleteManager()
    default_objects = BaseUserManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        if self.pk is None:
            raise ValueError(
                "%s object can't be deleted because its %s attribute is set "
                "to None." % (self._meta.object_name, self._meta.pk.attname)
            )

        using = using or router.db_for_write(self.__class__, instance=self)
        collector = NestedObjects(using=using, origin=self)
        collector.collect([self], keep_parents=keep_parents)
        to_update = collector.nested()
        # TODO need to double check if works properly
        # TODO performance check is needed
        # TODO many to many needs to be checked
        for obj in to_update:
            if hasattr(obj.__class__, "is_deleted"):
                obj.is_deleted = True
                obj.deleted_at = timezone.now()
                obj.save(update_fields=["is_deleted", "deleted_at"])
            else:
                obj.delete()


class User(AbstractUser, SoftDeleteBaseModel):
    username = None
    phone = models.CharField(
        validators=[phone_number_regex], unique=True, db_index=True
    )
    is_active = models.BooleanField("active", default=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = CustomManager()


class RecycleUser(User):
    deleted_object = BaseUserManager()

    class Meta:
        proxy = True
