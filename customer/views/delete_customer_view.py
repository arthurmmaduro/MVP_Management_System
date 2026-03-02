from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from audit.application.create_audit import CreateAuditService
from audit.infrastructure.customer_audit_adapter import CustomerAuditAdapter
from audit.infrastructure.django_audit_repository import DjangoAuditRepository
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
        audit_repository = DjangoAuditRepository()
        audit_service = CreateAuditService(audit_repository)
        audit_gateway = CustomerAuditAdapter(audit_service)
        return SoftDeleteCustomerService(repository, audit_gateway)

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
        user_id = request.user.id
        if user_id is None:
            return redirect_to_login(request.get_full_path())

        try:
            output = self.get_service().execute(
                SoftDeleteCustomerInput(
                    customer_id=self.kwargs['pk'],
                    updated_by=user_id,
                )
            )
        except CustomerNotFound as exc:
            raise Http404(str(exc)) from exc

        messages.success(request, f'Cliente {output.customer_id} excluído com sucesso.')
        return redirect('customer:list')
