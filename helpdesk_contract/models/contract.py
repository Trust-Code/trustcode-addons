from odoo import fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    partner_id = fields.Many2one(
        related="contract_id.partner_id", store=True, readonly=True)