# -*- coding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Fillipe ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class Royalties(models.Model):
    _name = 'royalties'

    name = fields.Char()
    validity_date = fields.Date(string=u"Validity Date")
    start_date = fields.Date(string=u"Start Date")
    royalty_type = fields.Char(string="Type")
    company_id = fields.Many2one("res.company", string="Company")
    payment_ids = fields.One2many("account.voucher", "royalties_id",
                                  readonly=True)
    line_ids = fields.One2many(
        'royalties.lines', 'royalties_id')
    partner_id = fields.Many2one('res.partner',
                                 string=u"Partner",
                                 required="1")
    region = fields.Char(string=u"Region", size=20)
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'in Progress'),
         ('waiting', 'Waiting Payment'), ('done', 'Done')],
        default='draft',
        store=True,
        compute='_compute_state')
    atived = fields.Boolean("Active")
    done = fields.Boolean("Contract Done")

    @api.one
    @api.constrains('validity_date')
    def _check_date(self):
        year, month, day = map(int, self.validity_date.split('-'))
        today = fields.Date.today()
        if self.validity_date < str(today):
            raise ValidationError(_("The validity date must be bigger then "
                                    "today"))
        elif year > int(today.split('-')[0]) + 12:
            raise ValidationError(_("The validity date can't be more then 12 "
                                    "years"))

    @api.multi
    @api.depends('atived', 'done', 'validity_date', 'payment_ids')
    def _compute_state(self):
        inv_royalties_obj = self.env['account.royalties.line']
        for item in self:
            line_ids = inv_royalties_obj.search([('voucher_id', '=', False),
                                                ('royalties_id', '!=', False)])
            royalties_ids = line_ids.mapped('royalties_id')
            if item.atived and item.validity_date <= str(fields.Date.today()):
                if royalties_ids and item.id in royalties_ids.ids:
                    item.state = 'waiting'
                else:
                    item.atived = False
                    item.done = True
                    item.state = 'done'
            elif item.atived:
                item.state = 'in_progress'
            elif item.done:
                item.state = 'done'
            elif not item.atived and not item.done:
                item.state = 'draft'

    @api.multi
    def button_confirm(self):
        for item in self:
            item.start_date = fields.Date.today()
            item.atived = True

    @api.multi
    def button_back_draft(self):
        for item in self:
            item.atived = False

    @api.multi
    def button_done(self):
        for item in self:
            item.atived = False
            item.done = True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('royalties')
        vals.update({'name': sequence})
        return super(Royalties, self).create(vals)

    @api.multi
    def royalties_payment(self):
        inv_royalties_obj = self.env['account.royalties.line']
        voucher_obj = self.env['account.voucher']
        journal_id = self.env['account.journal'].search([
            ('special_royalties', '=', True)])
        if not journal_id:
            raise Warning(_("The system didn't find the especific Account "
                            "Journal"))

        for item in self:
            voucher_id = voucher_obj.search([
                ('royalties_id', '=', item.id),
                ('state', '=', 'draft')], limit=1)
            if not voucher_id:
                vals = {
                    'partner_id': item.partner_id.id,
                    'account_id':
                        item.partner_id.property_account_payable_id.id,
                    'date': fields.Date.today(),
                    'pay_now': 'pay_later',
                    'voucher_type': 'purchase',
                    'journal_id': journal_id.id,
                    'royalties_id': item.id,
                    'reference': 'Royalties Payment(%s)' % item.name,
                    }
                voucher_id = voucher_obj.create(vals)

            product_ids = item.line_ids.mapped('product_id')
            for prod_id in product_ids:
                royalties_line_ids = inv_royalties_obj.search(
                    [('voucher_id', '=', False),
                     ('royalties_id', '=', item.id),
                     ('product_id', '=', prod_id.id)])

                qty = item._get_roayalties_qty(royalties_line_ids)
                fee = item._get_royalties_fee(qty, prod_id)
                dev_value = 0

                for roy_line in royalties_line_ids:
                    inv_line = roy_line.inv_line_id

                    if roy_line.inv_line_id_related:
                        inv_number = inv_line.invoice_id.number
                        self.royalties_repayment(roy_line, voucher_id,
                                                 inv_number)
                        #msg = voucher_id['narration'] + \
                        #       u'Devolução Royalties (%s) :: %s' % \
                        #       (item.name, inv_line.invoice_id.number)
                        #voucher_id.write({'narration': msg})
                        #dev_value = inv_line.quantity
                        continue

                    if item.partner_id.government:
                        unit_price = (inv_line.price_subtotal /
                                      inv_line.quantity)
                    else:
                        unit_price = inv_line.product_id.list_price

                    line_vals = {
                        'product_id': inv_line.product_id.id,
                        'quantity': inv_line.quantity - dev_value,
                        'name': 'Royalties (%s) :: %s' %
                                (item.name, inv_line.invoice_id.number),
                        'price_unit': unit_price * fee,
                        'account_id':
                            voucher_id.journal_id.default_debit_account_id.id,
                        'company_id': inv_line.company_id.id,
                        'inv_line_id': inv_line.id,
                        }

                    voucher_id.write({'line_ids': [(0, 0, line_vals)]})
                    royalties_line_ids.write({'voucher_id': voucher_id.id})
                    dev_value = 0

    def _get_royalties_fee(self, qty, product_id):
        self.ensure_one()
        result = False

        for line in self.line_ids.sorted(key=lambda r: r.min_qty,
                                         reverse=True):
            if line.product_id.id == product_id.id and qty >= line.min_qty:
                    return line.commission / 100
        return result

    def _get_roayalties_qty(self, royalties_line_ids):
        import ipdb
        ipdb.set_trace()
        royalties_line_sold_ids = royalties_line_ids.filtered(
            lambda x: len(x.inv_line_id_related) > 0).mapped('inv_line_id')
        royalties_line_devol_ids = royalties_line_ids.filtered(
            'inv_line_id_related').mapped('inv_line_id')
        qty_sold = sum([x.quantity for x in royalties_line_sold_ids])
        qty_dev = sum([x.quantity for x in royalties_line_devol_ids])
        return qty_sold - qty_dev

    def royalties_repayment(self, roy_line, voucher_id, inv_number):
        domain = [('inv_line_id', '=', roy_line.inv_line_id_related.id)]
        import ipdb
        ipdb.set_trace()
        voucher_line_id = self.env['account.voucher.line'].search(domain)
        qty = (voucher_line_id.quantity - roy_line.inv_line_id.quantity)

        name = (voucher_line_id['name'] +
                u'Devolução Royalties (%s) :: %s' %
                (self.name, inv_number))

        vals = {'name': name, 'quantity': qty}
        voucher_line_id.write(vals)
        return None


class RoyaltiesLines(models.Model):
    _name = 'royalties.lines'

    product_id = fields.Many2one(
        'product.product', string="Product", required=False)
    commission = fields.Float(string="% Commission")
    min_qty = fields.Float(string="Qty. minimum", default=1)
    royalties_id = fields.Many2one('royalties', string="Contracts")

    @api.one
    @api.constrains('commission')
    def _check_value(self):
        if self.commission < 0:
            raise ValidationError(
                _("The commission rate must be bigger them 0"))
        if self.commission > 100:
            raise ValidationError(
                _("The commission rate must be smaller them 100"))

    @api.one
    @api.constrains('commission')
    def _check_positive(self):
        if self.min_qty < 1:
            raise ValidationError(
                _("Quantity must be bigger them 1"))
