# © 2018 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
            'projetista': bom.projetista,
            'height': bom.height,
            'width': bom.width,
            'trat_perf': bom.trat_perf,
        })
        return res
