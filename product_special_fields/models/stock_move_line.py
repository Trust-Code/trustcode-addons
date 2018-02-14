from odoo import fields, models, _


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    imei = fields.Char(string=_(u"Valor do IMEI"))
    iccd = fields.Char(string=_(u"Valor do ICCD"))
    n_linha = fields.Char(string=_(u"Número da Linha"))

    conf_imei = fields.Boolean(related='move_id.product_id.imei')
    conf_iccd = fields.Boolean(related='move_id.product_id.iccd')
    conf_n_linha = fields.Boolean(related='move_id.product_id.n_linha')

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for ml in self:
            if ml.lot_id:
                ml.lot_id.update(
                    {'imei': ml.imei, 'iccd': ml.iccd, 'n_linha': ml.n_linha})
        return res
