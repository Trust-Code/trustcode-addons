from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit ='sale.order.line'
   
    original_amount = fields.Monetary(string="Valor Devido")
    addition_amount = fields.Monetary(string="Valor Acrescido")