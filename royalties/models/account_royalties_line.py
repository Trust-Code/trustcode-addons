# -*- encoding: utf-8 -*-
# © 2017 Mackilem Van der Laan, Trustcode
# © 2017 Danimar Ribeiro, Trustcode
# © 2017 Fabio Luna, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountRoyaltiesLine(models.Model):
    _name = "account.royalties.line"

    inv_line_id = fields.Many2one('account.invoice.line', ondelete='set null')
    is_devol = fields.Boolean('Is Devolution?')
    product_id = fields.Many2one('product.product', required=True,
                                 string="Product", ondelete='set null')
    royalties_id = fields.Many2one('royalties', required=True,
                                   string='Royalties', ondelete='restrict')
    voucher_id = fields.Many2one('account.voucher', ondelete='set null')

    @api.multi
    def _create_royalties_line(self, royalties_id, inv_line_ids, devol=False):
        for l in inv_line_ids:
            vals = {'inv_line_id': l.id,
                    'royalties_id': royalties_id.id,
                    'product_id': l.product_id.id,
                    'is_devol': devol}
            result = self.create(vals)

        inv_line_ids.write({'royalties_ids': [(4, royalties_id.id)]})
        return result

    def get_invoice_royalties(self, royalties_ids):
        invoice_line_obj = self.env['account.invoice.line']

        for roy in royalties_ids:
            product_ids = roy.mapped('line_ids.product_id')
            inv_line_ids = invoice_line_obj.search([
                ('invoice_id.fiscal_position_id.royalties', '=', True),
                ('product_id', 'in', product_ids.ids),
                ('royalties_ids', 'not in', roy.id)])

            inv_line_sell_ids = inv_line_ids.filtered(
                lambda l:
                    l.invoice_id.fiscal_position_id.finalidade_emissao == '1')
            if inv_line_sell_ids:
                self._create_royalties_line(roy, inv_line_sell_ids, False)

            inv_line_devol_ids = inv_line_ids.filtered(
                lambda l:
                    l.invoice_id.fiscal_position_id.finalidade_emissao == '4')
            if inv_line_devol_ids:
                self._create_royalties_line(roy, inv_line_devol_ids, True)
