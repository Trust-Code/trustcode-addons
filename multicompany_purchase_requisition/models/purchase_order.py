from odoo import models, fields
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    centralizador_id = fields.Many2one(
        'purchase.multicompany.req', string="Centralizador"
    )

    def _get_pm_ids(self):

        pm_list = set()
        for line in self.order_line:
            for pm_line in line.req_line_id.requisition_line_ids:
                pm_list = pm_list.union(pm_line.requisition_id)
        return pm_list

    def _get_related_pm_line(self, line, pm_id):

        for pm_line in line.req_line_id.requisition_line_ids:
            if pm_line.requisition_id.id == pm_id:
                return pm_line

        return False


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    prod_original_qty = fields.Float(
        string="Original qty", digits=dp.get_precision(
            'Product Unit of Measure'))

    qty_increment = fields.Float(
        string='Qty Increment', digits=dp.get_precision(
            'Product Unit of Measure'))

    req_line_id = fields.Many2one('purchase.multicompany.req.line')
