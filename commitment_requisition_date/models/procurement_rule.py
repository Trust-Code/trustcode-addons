from odoo import models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _prepare_mo_vals(
            self, product_id, product_qty, product_uom,
            location_id, name, origin, values, bom):

        res = super(ProcurementRule, self)._prepare_mo_vals(
            product_id, product_qty, product_uom,
            location_id, name, origin, values, bom)

        res.update({
            'commitment_date': values.get('commitment_date') or False,
            'requisition_date': values.get('requisition_date') or False,
        })

        return res
