from odoo import fields, models, _


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    imei = fields.Char(string=_(u"Valor do IMEI"))
    iccd = fields.Char(string=_(u"Valor do ICCD"))
    n_linha = fields.Char(string=_(u"Número da Linha"))
