from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from customer.application.soft_delete_customer import SoftDeleteCustomerService
from customer.domain.dto.soft_delete_customer_dto import SoftDeleteCustomerInput
from customer.domain.exceptions.customer_exceptions import CustomerNotFound
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class DeleteCustomerView(TemplateView):
    template_name = 'customer/confirm_delete_customer.html'
    _customer: Customer | None = None

    def get_service(self) -> SoftDeleteCustomerService:
        repository = DjangoCustomerRepository()
        return SoftDeleteCustomerService(repository)

    def get_customer(self) -> Customer:
        if self._customer is not None:
            return self._customer

        customer = DjangoCustomerRepository().get_by_id(self.kwargs['pk'])
        if customer is None:
            raise Http404(f'Cliente não encontrado: {self.kwargs["pk"]}')

        self._customer = customer
        return customer

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context['customer'] = self.get_customer()
        return context

    def post(
        self,
        request: HttpRequest,
        *args: object,
        **kwargs: object,
    ) -> HttpResponse:
        try:
            output = self.get_service().execute(
                SoftDeleteCustomerInput(customer_id=self.kwargs['pk'])
            )
        except CustomerNotFound as exc:
            raise Http404(str(exc)) from exc

        messages.success(request, f'Cliente {output.customer_id} excluído com sucesso.')
        return redirect('customer:list')
