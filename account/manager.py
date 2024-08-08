from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager, Q
from django.db.models.query import QuerySet
from django.utils import timezone


class SoftQuerySet(QuerySet):

    def delete(self):
        self._not_support_combined_queries("delete")
        if self.query.is_sliced:
            raise TypeError("Cannot use 'limit' or 'offset' with delete().")
        if self.query.distinct or self.query.distinct_fields:
            raise TypeError("Cannot call delete() after .distinct().")
        if self._fields is not None:
            raise TypeError("Cannot call delete() after .values() or .values_list()")

        del_query = self._chain()

        del_query._for_write = True

        del_query.query.select_for_update = False
        del_query.query.select_related = False
        del_query.query.clear_ordering(force=True)

        collector = NestedObjects(using=del_query.db, origin=self)
        collector.collect(del_query)

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

        self._result_cache = None


class CustomManager(BaseUserManager):
    def create_user(self, phone, password):
        if not phone:
            raise ValueError("Users must have an phone")
        if not password:
            raise ValueError("Users must have an password")

        user = self.model(phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password):
        user = self.create_user(phone, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
