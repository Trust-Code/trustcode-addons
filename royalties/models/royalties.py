# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    contract_ids = fields.One2many(
        'royalties.contract', 'product_id')


class RoyaltiesLine(models.Model):
    _name = 'royalties'

    commission = fields.Float(
        string=u'Valor da Comissão', readonly=True)
    product_id = fields.Many2one(
        'product.template', string='Produto', required=True)
    order_id = fields.Many2one('account.invoice', string='Pedido')


class RoyaltiesContract(models.Model):
    _name = 'royalties.contract'

    validity_date = fields.Date(string="Data de Validade")
    royalty_type = fields.Char(string="Tipo")
    product_id = fields.Many2one(
        'product.template', string="Produto", required=True)
    commission_ids = fields.One2many(
        'royalties.contract.commission.rule', 'contract_id')
    partner_id = fields.Many2one('res.partner', string=u"Beneficiários")
    region = fields.Char(string=u"Região", size=20)

    @api.one
    @api.constrains('validity_date')
    def _check_date(self):
        year, month, day = map(int, self.validity_date.split('-'))
        today = str(date.today())
        if self.validity_date < today:
            raise ValidationError(
                _("Data deve ser maior que hoje ou posterior"))
        elif year > (date.today().year + 12):
            raise ValidationError(
                _("Data não pode ultrapassar 12 anos"))


class RoyaltiesContractCommissionRule(models.Model):
    _name = 'royalties.contract.commission.rule'

    commission = fields.Float(string=u"% Comissão")
    min_qty = fields.Float(string=u"Qtd. Mínima")
    contract_id = fields.Many2one('royalties.contract', string=u"Contratos")

    @api.one
    @api.constrains('commission')
    def _check_value(self):
        if self.commission < 0:
            raise ValidationError(
                _("Percentual de comissão deve ser maior que 0"))
        if self.commission > 100:
            raise ValidationError(
                _("Percentual de comissão deve ser menor que 100"))

    @api.one
    @api.constrains('commission')
    def _check_positive(self):
        if self.min_qty < 1:
            raise ValidationError(
                _("Quantidade deve ser maior que 1"))


class RoyaltiesCommissionInvoiced(models.Model):
    _name = 'royalties.commission.invoiced'

    commission = fields.Float(string=u"Valor da Comissão")
    invoice_line_id = fields.Many2one('account.invoice.line', string=u"Linhas")
    partner_id = fields.Many2one('res.partner', string=u'Beneficiários')
    contract_id = fields.Many2one('royalties.contract', string=u"Contratos")
    voucher_id = fields.Many2one('account.voucher', ondelete="set null")
