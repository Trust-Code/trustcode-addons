from datetime import datetime
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    pre_pedido_id = fields.Many2one('pre.pedido')
    
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def action_return_item(self):
        order = self.order_id
        
        invoices = order.invoice_ids.filtered(lambda x: x.type == 'out_invoice')
        pickings = order.picking_ids.filtered(lambda x: x.picking_type_id.code == 'outgoing')

        invoice_item = None
        picking_item = None
        for invoice in invoices:
            for line in invoice.invoice_line_ids:
                
                if line.product_id == self.product_id:
                    
                    refund = self.env["account.invoice.refund"].with_context({
                        'active_id': invoice.id,
                        'active_ids': [invoice.id],
                    }).create({
                        'date_invoice': datetime.now(),
                        'date': datetime.now(),
                        'description': 'devoluçõ automatica'
                    })
                    refund.invoice_refund()
                    break
                
        for picking in pickings:
            for line in picking.move_ids_without_package:
                
                if line.product_id == self.product_id:
                    
                    devolucao = self.env['stock.return.picking'].with_context({
                        'active_id': picking.id,
                    }).create({})

                    devolucao.create_returns()
                    break
