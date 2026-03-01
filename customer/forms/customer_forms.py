from django import forms

from customer.domain.constants.constants import CUSTOMER_NAME_MAX_LENGTH
from customer.domain.dto.create_customer_dto import CreateCustomerInput
from customer.domain.dto.update_customer_dto import UpdateCustomerInput
from customer.domain.exceptions.customer_exceptions import (
    CustomerAlreadyExists,
    CustomerNameIsEmpty,
    CustomerNameIsTooLong,
    CustomerNameIsTooShort,
)


class CustomerBaseForm(forms.Form):
    name = forms.CharField(
        max_length=CUSTOMER_NAME_MAX_LENGTH,
        label='Nome',
        widget=forms.TextInput(),
    )

    def apply_domain_error(self, exc: Exception) -> None:
        if isinstance(
            exc,
            (
                CustomerAlreadyExists,
                CustomerNameIsEmpty,
                CustomerNameIsTooLong,
                CustomerNameIsTooShort,
            ),
        ):
            self.add_error('name', exc.message)
            return

        self.add_error(None, 'Não foi possível processar a requisição.')


class CreateCustomerForm(CustomerBaseForm):
    def to_dto(self, created_by: int) -> CreateCustomerInput:
        return CreateCustomerInput(
            name=self.cleaned_data['name'],
            created_by=created_by,
            updated_by=created_by,
        )


class UpdateCustomerForm(CustomerBaseForm):
    def to_dto(self, customer_id: int, updated_by: int) -> UpdateCustomerInput:
        return UpdateCustomerInput(
            customer_id=customer_id,
            name=self.cleaned_data['name'],
            updated_by=updated_by,
        )
