# -*- coding: utf-8 -*-
# (c) 2015 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://gnu.org/licenses/agpl-3.0.html)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    product_name = fields.Char(readonly=True)
    product_code = fields.Char(readonly=True)


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _selection_filter(self):
        res = super(StockInventory, self)._selection_filter()
        res.append(('file', _('By File')))
        return res

    @api.multi
    @api.depends('import_lines')
    def _file_lines_processed(self):
        for record in self:
            processed = True
            if record.import_lines:
                processed = any((not line.fail or
                                 (line.fail and
                                  line.fail_reason != 'No processed'))
                                for line in record.import_lines)
            record.processed = processed

    imported = fields.Boolean('Importado')
    import_lines = fields.One2many('stock.inventory.import.line',
                                   'inventory_id', string='Linhas Importadas')
    processed = fields.Boolean(string='Foi Processado?',
                               compute='_file_lines_processed')

    @api.multi
    def process_import_lines(self):
        """Process Inventory Load lines."""
        import_lines = self.mapped('import_lines')
        if not import_lines:
            raise UserError("É necessário pelo menos uma linha para processar")
        inventory_line_obj = self.env['stock.inventory.line']
        stk_lot_obj = self.env['stock.production.lot']
        product_obj = self.env['product.product']
        for line in import_lines:
            if line.fail:
                if not line.product:
                    prod_lst = product_obj.search([('default_code', '=',
                                                    line.code)], limit=1)
                    if prod_lst:
                        product = prod_lst
                    else:
                        line.fail_reason = 'Nenhum produto encontrado'
                        continue
                else:
                    product = line.product
                lot_id = None
                if line.lot:
                    lot_lst = stk_lot_obj.search([
                        ('name', '=', line.lot),
                        ('product_id', '=', product.id),
                    ])
                    if lot_lst:
                        lot_id = lot_lst[0].id
                    else:
                        lot = stk_lot_obj.create({'name': line.lot,
                                                  'product_id': product.id})
                        lot_id = lot.id
                inventory_line_obj.create({
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'product_qty': line.quantity,
                    'inventory_id': line.inventory_id.id,
                    'location_id': line.location_id.id,
                    'prod_lot_id': lot_id,
                    'partner_id': line.owner_id.id,
                })
                line.write({'fail': False, 'fail_reason': 'Processado'})
        return True

    @api.multi
    def action_done(self):
        for inventory in self:
            if not inventory.processed:
                raise UserError('Linhas carregadas devem ser processadas ao '
                                'menos uma vez para o inventário : %s' %
                                inventory.name)
            super(StockInventory, inventory).action_done()
        return True
