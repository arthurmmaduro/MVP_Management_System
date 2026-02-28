from __future__ import annotations

from django.db import models

from customer.models.customer_queryset import CustomerQueryset


class CustomerManager(models.Manager):
    def get_queryset(self) -> CustomerQueryset:
        return CustomerQueryset(self.model, using=self._db).active()

    def active(self) -> CustomerQueryset:
        return self.get_queryset().active()

    def search(self, query: str) -> CustomerQueryset:
        return self.get_queryset().search(query)

    def order_by_name(self) -> CustomerQueryset:
        return self.get_queryset().order_by_name()


class CustomerAllManager(models.Manager):
    def get_queryset(self) -> CustomerQueryset:
        return CustomerQueryset(self.model, using=self._db)

    def active(self) -> CustomerQueryset:
        return self.get_queryset().active()

    def inactive(self) -> CustomerQueryset:
        return self.get_queryset().inactive()

    def search(self, query: str) -> CustomerQueryset:
        return self.get_queryset().search(query)

    def order_by_name(self) -> CustomerQueryset:
        return self.get_queryset().order_by_name()
