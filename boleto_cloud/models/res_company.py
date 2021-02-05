from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    boleto_cloud_api_token = fields.Char('Boleto Cloud Api Token')