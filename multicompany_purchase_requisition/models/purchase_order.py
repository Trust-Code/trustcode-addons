from odoo import models, fields
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    centralizador_id = fields.Many2one(
        'purchase.multicompany.req', string="Centralizador"
    )

    def _get_pm_ids(self):
        """Retorna um set de purchase_requisitions únicos"""
        return set(self.mapped(
            'order_line.req_line_id.requisition_line_ids.requisition_id'))

    def _get_related_pm_line(self, po_line, pm_id):
        """Retorna uma lista de requisition_lines que estejam associados
        ao purchase_multicompany
        """
        # For future reference: mapped returns list; filtered + lambda
        return po_line.mapped('req_line_id.requisition_line_ids')\
            .filtered(lambda x, pm_id=pm_id: x.requisition_id.id == pm_id)

    def button_confirm(self):
        """ Cria PO para cada filial e confirma em seguida"""
        res = super(PurchaseOrder, self).button_confirm()
        # Variável po está aqui para que não ocorra recursão
        po = None

        if self.centralizador_id and not po:
            po_object = self.env['purchase.order']
            for pm_id in self._get_pm_ids():
                lines_list = []

                vals = {
                    'name': self.name,
                    'partner_id': self.partner_id.id,
                    'date_order': self.date_order,
                    'company_id': pm_id.company_id.id,
                    'notes': self.notes,
                    'date_planned': self.date_planned,
                    'incoterm_id': self.incoterm_id.id,
                }

                po = po_object.sudo().create(vals)
                for line in self.order_line:
                    related_pm_line = self._get_related_pm_line(line, pm_id.id)
                    for item in related_pm_line:
                        lines_list.append(
                            [item, line.price_unit, line.date_planned])

                for item in lines_list:
                    line_val = {
                        'product_id': item[0].product_id.id,
                        'name': item[0].product_id.name,
                        'company_id': item[0].company_id.id,
                        'date_planned': item[2],
                        'product_uom': item[0].product_uom_id.id,
                        'product_qty': item[0].product_qty,
                        'price_unit': item[1],
                    }
                    po.sudo().write({'order_line': [(0, 0, line_val)]})
                po.button_confirm()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    prod_original_qty = fields.Float(
        string="Original qty", digits=dp.get_precision(
            'Product Unit of Measure'))

    qty_increment = fields.Float(
        string='Qty Increment', digits=dp.get_precision(
            'Product Unit of Measure'))

    req_line_id = fields.Many2one('purchase.multicompany.req.line')
