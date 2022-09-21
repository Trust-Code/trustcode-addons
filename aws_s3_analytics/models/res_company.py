from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    aws_access_key_id_o = fields.Char(string="Aws Token")
    aws_secret_access_key_o = fields.Char(string="Aws Secret Key")

