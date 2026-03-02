from django.test import SimpleTestCase

from audit.domain.exception.audit_exception import EntityTypeEmpty


class TestAuditExceptions(SimpleTestCase):
    def test_entity_type_empty_has_expected_message(self):
        exception = EntityTypeEmpty()

        self.assertEqual(
            str(exception),
            'O tipo de entidade do log de auditoria nao pode ser vazio',
        )
