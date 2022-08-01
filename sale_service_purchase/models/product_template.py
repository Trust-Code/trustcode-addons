# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_type = fields.Selection(selection_add=[
        ('create_purchase_order', 'Create a Purchase Order'),
        ])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
