from datetime import datetime
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
# from odoo.exceptions import UserError


class ToBeDefined(models.Model):
    _name = "to.be.defined"
    _order = "id desc"

    name = fields.Char(
        string='Agreement Reference', required=True, copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'purchase.multicompany.requisition'))
    ordering_date = fields.Date(string="Ordering Date")
    date_end = fields.Datetime(string='Agreement Deadline')
    schedule_date = fields.Date(string='Delivery Date', index=True)
    user_id = fields.Many2one(
        'res.users', string='Responsible', default=lambda self: self.env.user)
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'purchase.requisition'))
    line_ids = fields.One2many(
        'to.be.defined.line', 'requisition_id',
        string='Products to Purchase', states={'done': [('readonly', True)]},
        copy=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'Confirmed'),
         ('needs_attention', 'Needs attention'),
         ('done', 'Done'), ('cancel', 'Cancelled')],
        'Status', track_visibility='onchange', required=True,
        copy=False, default='draft')
    purchase_order_ids = fields.Many2many(
        'purchase.order', string="Purchase Orders"
    )
    purchase_requisition_ids = fields.Many2many(
        'purchase.requisition', string="Purchase Requisitions"
    )

    @api.multi
    def juntatuto(self, multicompany_requests):
        import ipdb
        ipdb.set_trace()
        rfq = {}
        tenders = {}
        for item in multicompany_requests:
            for line in item.line_ids:
                seller_id = line.product_id.seller_ids[0].name.id
                product_id = line.product_id

                if line.product_id.purchase_requisition == 'rfq':

                    if seller_id not in rfq:
                        rfq[seller_id] = {}

                    if product_id not in rfq[seller_id]:
                        rfq[seller_id][product_id] = line.product_qty

                    else:
                        rfq[seller_id][product_id] += line.product_qty

                elif line.product_id.purchase_requisition == 'tenders':

                    if seller_id not in tenders:
                        tenders[seller_id] = {}

                    if product_id not in tenders[seller_id]:
                        tenders[seller_id][product_id] = line.product_qty

                    else:
                        tenders[seller_id][product_id] += line.product_qty

        self._create_purchase_orders(rfq)
        self._create_purchase_requisition(tenders)

    def _create_purchase_requisition(self, tender_dict):
        pr_lines = []
        requisition_ids = {}
        req_ids = []

        for vendor_id, lines in tender_dict.items():
            for product_id, quantity in lines.items():
                line_vals = {
                    'product_id': product_id.id,
                    'product_qty': quantity,
                    'price_unit': product_id.seller_ids[0].price,
                }
                pr_lines.append(self.env[
                    'purchase.requisition.line'].create(line_vals).id)
            vals = {
                'vendor_id': vendor_id,
                'line_ids': [(6, 0, pr_lines)],
                'user_id': self[0].user_id.id,
                # 'centralizador_id': self.id,
            }

            req_id = self.env['purchase.requisition'].create(vals).id
            requisition_ids[vendor_id] = req_id
            req_ids.append(req_id)
        self.write({'purchase_requisition_ids': [(6, 0, req_ids)]})
        self._create_purchase_orders(tender_dict, requisition_ids)

    def _create_purchase_orders(self, rfq_dict, req_ids=False):
        po_lines = []
        po_ids = []
        for vendor_id, lines in rfq_dict.items():
            vals = {
                'partner_id': vendor_id,
                'requisition_id': req_ids[vendor_id] if req_ids else None,
                # 'centralizador_id': self.id,
            }
            po_id = self.env['purchase.order'].create(vals)
            po_ids.append(po_id.id)

            for product_id, quantity in lines.items():
                line_vals = {
                    'product_id': product_id.id,
                    'name': product_id.name,
                    'date_planned': datetime.now(),
                    'product_uom': product_id.uom_id.id,
                    'product_qty': quantity,
                    'price_unit': product_id.seller_ids[0].price,
                    'order_id': po_id.id,
                }
                po_lines.append(self.env[
                    'purchase.order.line'].create(line_vals).id)
        self.write({'purchase_order_ids': [(6, 0, po_ids)]})

    class ToBeDefinedLine(models.Model):
        _name = "to.be.defined.line"
        _description = "To Be Defined Line"
        _rec_name = 'product_id'

        product_id = fields.Many2one(
            'product.product', string='Product',
            domain=[('purchase_ok', '=', True)], required=True)
        product_uom_id = fields.Many2one(
            'product.uom', string='Product Unit of Measure')
        product_qty = fields.Float(
            string='Quantity', digits=dp.get_precision(
                'Product Unit of Measure'))
        qty_increment = fields.Float(
            string='Increment', digits=dp.get_precision(
                'Product Unit of Measure'))
        requisition_id = fields.Many2one(
            'purchase.multicompany', string='Purchase Company',
            ondelete='cascade')
        company_id = fields.Many2one(
            'res.company', related='requisition_id.company_id',
            string='Company',
            store=True, readonly=True,
            default=lambda self: self.env['res.company']._company_default_get(
                'purchase.multicompany.line'))

        @api.onchange('product_id')
        def _onchange_product_id(self):
            if self.product_id:
                self.product_uom_id = self.product_id.uom_id
                self.product_qty = 1.0
