from odoo import fields, models, _


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    imei = fields.Char(string=_(u"Valor do IMEI"))
    iccid = fields.Char(string=_(u"Valor do ICCID"))
    n_linha = fields.Char(string=_(u"Número da Linha"))
    partner_id = fields.Many2one('res.partner', 'Cliente', store=True)
