from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    support_contract_count = fields.Integer(related="partner_id.support_contract_count")

    def action_view_contract_lines(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "contract.line",
            "name": "Contratos do cliente",
            "view_mode": "tree,form",
            "domain": [('partner_id', 'child_of', self.partner_id.commercial_partner_id.id),
                       ('product_id.has_support_contract', '=', True)],
        }