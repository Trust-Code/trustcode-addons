from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    imei = fields.Boolean(string=u"IMEI Obrigatório")
    iccid = fields.Boolean(string=u"ICCID Obrigatório")
    n_linha = fields.Boolean(string=u"Numero da linha Obrigatório")
