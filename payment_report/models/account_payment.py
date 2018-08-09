from odoo import models, api
from collections import defaultdict


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def group_docs_by_user(self, doc_list):
        groups = defaultdict(list)
        for payment in doc_list:
            groups[payment.create_uid.id].append(payment)

        return groups.values()

    @api.multi
    def group_docs_by_company(self):
        groups = defaultdict(list)
        for payment in self:
            groups[payment.company_id.id].append(payment)

        return groups.values()

    @api.multi
    def get_total_value(self, payment_ids):
        return sum(payment.amount for payment in payment_ids)
