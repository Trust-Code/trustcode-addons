# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from date import date


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    contract_ids = fields.One2many(
        'royalties.contract', 'product_id')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            qty_to_invoice = 0.0
            for line in invoice.invoice_line_ids:
                line.commission_total = 0.0
                if not line.product_id.contract_ids:
                    continue
                line.commission_invoiced_ids.unlink()
                for contract in line.product_id.contract_ids:
                    if contract.validity_date < invoice.date_invoice:
                        continue
                    for commission_id in contract.commission_ids.sorted(
                        key=lambda r: r.min_qty, reverse=True):
                        qty_to_invoice = line.quantity
                        if qty_to_invoice >= commission_id.min_qty:
                            product_value = 0.0
                            if contract.partner_id.government:
                                product_value = line.product_id.standard_price
                            else:
                                product_value = line.product_id.list_price
                            comm_perc = (commission_id.commission / 100)
                            qty_sold = (product_value * qty_to_invoice)
                            commission_line = (qty_sold * comm_perc)
                            vals = {
                                'commission': commission_line,
                                'partner_id': contract.partner_id.id,
                                'invoice_line_id': line.id,
                                'contract_id': contract.id,
                            }
                            line.commission_total += commission_line
                            self.env['royalties.commission.invoiced'].create(
                                vals)
        return super(AccountInvoice, self).invoice_validate()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    commission_invoiced_ids = fields.One2many(
        'royalties.commission.invoiced', 'invoice_line_id')
    commission_total = fields.Float(
        string="Commissions")


class RoyaltiesLine(models.Model):
    _name = 'royalties'

    commission = fields.Float(
        string='Valor da Comissão', readonly=True)
    product_id = fields.Many2one(
        'product.template', string='Produto', required=True)
    order_id = fields.Many2one('account.invoice', string='Order')


class RoyaltiesContract(models.Model):
    _name = 'royalties.contract'

    validity_date = fields.Date(string="Data de Validade")
    royalty_type = fields.Char(string="Tipo")
    product_id = fields.Many2one(
        'product.template', string="Produto", required=True)
    commission_ids = fields.One2many(
        'royalties.contract.commission.rule', 'contract_id')
    partner_id = fields.Many2one('res.partner', string=u'Beneficiários')
    region = fields.Char(string=u"Região", size=20)

    @api.one
    @api.constrains('validity_date')
    def _check_date(self):
        year, month, day = map(int, self.validity_date.split('-'))
        today = str(date.today())
        if self.validity_date < today:
            raise ValidationError(
                _("Date must be today or later"))
        elif year > (date.today().year + 12):
            raise ValidationError(
                _("Date must be NO later than 12 years"))


class RoyaltiesContractCommissionRule(models.Model):
    _name = 'royalties.contract.commission.rule'

    commission = fields.Float(string=u"% Comissão")
    min_qty = fields.Float(string=u"Qtd. Mínima")
    contract_id = fields.Many2one('royalties.contract', string="Contratos")

    @api.one
    @api.constrains('commission')
    def _check_value(self):
        if self.commission < 0:
            raise ValidationError(
                _("Commission percentage must be higher than 0"))
        if self.commission > 100:
            raise ValidationError(
                _("Commission percentage must be lower than 100"))

    @api.one
    @api.constrains('commission')
    def _check_positive(self):
        if self.min_qty < 1:
            raise ValidationError(
                _("Quantity must be higher than 1"))


class RoyaltiesCommissionInvoiced(models.Model):
    _name = 'royalties.commission.invoiced'

    commission = fields.Float(string=u"Valor da Comissão")
    invoice_line_id = fields.Many2one('account.invoice.line', string="Linhas")
    partner_id = fields.Many2one('res.partner', string=u'Beneficiários')
    contract_id = fields.Many2one('royalties.contract', string="Contratos")
    voucher_id = fields.Many2one('account.voucher', ondelete="set null")
