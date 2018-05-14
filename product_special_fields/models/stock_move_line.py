from odoo import fields, models, _


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    imei = fields.Char(string=_(u"Valor do IMEI"))
    iccid = fields.Char(string=_(u"Valor do ICCID"))
    n_linha = fields.Char(string=_(u"Número da Linha"))

    conf_imei = fields.Boolean(related='move_id.product_id.imei')
    conf_iccid = fields.Boolean(related='move_id.product_id.iccid')
    conf_n_linha = fields.Boolean(related='move_id.product_id.n_linha')

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for ml in self:
            if ml.lot_id:
                ml.lot_id.update(
                    {'imei': ml.imei,
                     'iccid': ml.iccid,
                     'n_linha': ml.n_linha,
                     'partner_id': ml.move_id.picking_id.partner_id.id})
        return res
