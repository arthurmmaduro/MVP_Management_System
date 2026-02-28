from django.db import models

from common.models.base_model import BaseModel
from customer.domain.constants.constants import CUSTOMER_NAME_MAX_LENGTH

from .customer_manager import CustomerAllManager, CustomerManager


class Customer(BaseModel):
    objects = CustomerManager()
    all_objects = CustomerAllManager()

    name = models.CharField(max_length=CUSTOMER_NAME_MAX_LENGTH)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['name', 'is_active'], name='idx_name_is_active')
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                condition=models.Q(is_active=True),
                name='unique_active_name',
            ),
        ]

    def __str__(self):
        return self.name
