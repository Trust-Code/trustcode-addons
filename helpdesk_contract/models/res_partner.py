from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    support_contract_count = fields.Integer(
        string="Contratos de Suporte", compute="_compute_contract_count"
    )

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        contract_model = self.env["contract.line"]
        fetch_data = contract_model.read_group(
            [("partner_id", "in", self.mapped('commercial_partner_id').ids),
             ("product_id.has_support_contract", "=", True)],
            ["partner_id"],
            ["partner_id"],
            lazy=False,
        )
        result = [[data["partner_id"][0], data["__count"]] for data in fetch_data]
        for partner in self:
            partner.support_contract_count = sum(
                [r[1] for r in result]
            )
