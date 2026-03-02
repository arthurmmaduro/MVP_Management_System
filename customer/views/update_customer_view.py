from django.contrib import messages
from django.http import Http404, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from audit.application.create_audit import CreateAuditService
from audit.infrastructure.customer_audit_adapter import CustomerAuditAdapter
from audit.infrastructure.django_audit_repository import DjangoAuditRepository
from common.domain.exceptions.base_exception import DomainException
from customer.application.update_customer import UpdateCustomerService
from customer.domain.exceptions.customer_exceptions import CustomerNotFound
from customer.forms.customer_forms import UpdateCustomerForm
from customer.infrastructure.django_customer_repository import DjangoCustomerRepository
from customer.models import Customer


class UpdateCustomerView(FormView):
    template_name = 'customer/form_customer.html'
    form_class = UpdateCustomerForm
    success_url = reverse_lazy('customer:list')
    _customer: Customer | None = None

    def get_service(self) -> UpdateCustomerService:
        repository = DjangoCustomerRepository()
        audit_repository = DjangoAuditRepository()
        audit_service = CreateAuditService(audit_repository)
        audit_gateway = CustomerAuditAdapter(audit_service)
        return UpdateCustomerService(repository, audit_gateway)

    def get_customer(self):
        if self._customer is not None:
            return self._customer

        customer = DjangoCustomerRepository().get_by_id(self.kwargs['pk'])
        if customer is None:
            raise Http404(f'Cliente não encontrado: {self.kwargs["pk"]}')

        self._customer = customer
        return customer

    def get_initial(self) -> dict[str, object]:
        initial = super().get_initial()
        initial['name'] = self.get_customer().name
        return initial

    def get_success_url(self) -> str:
        return reverse('customer:detail', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse('customer:detail', args=[self.kwargs['pk']])
        context['is_update'] = True
        context['customer'] = self.get_customer()
        return context

    def form_valid(self, form: UpdateCustomerForm) -> HttpResponse:
        user_id = self.request.user.id
        if user_id is None:
            form.add_error(
                None, 'É necessário estar autenticado para atualizar cliente.'
            )
            return self.form_invalid(form)

        customer = self.get_customer()

        try:
            self.get_service().execute(
                form.to_dto(customer_id=customer.id, updated_by=user_id)
            )
        except CustomerNotFound as exc:
            raise Http404(str(exc)) from exc
        except DomainException as exc:
            form.apply_domain_error(exc)
            return self.form_invalid(form)

        messages.success(
            self.request, f'Cliente {form.cleaned_data["name"]} atualizado com sucesso.'
        )
        return super().form_valid(form)
