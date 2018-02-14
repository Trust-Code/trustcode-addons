from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    imei = fields.Boolean(string=u"IMEI Obrigatório")
    iccd = fields.Boolean(string=u"ICCD Obrigatório")
    n_linha = fields.Boolean(string=u"Numero da linha Obrigatório")
