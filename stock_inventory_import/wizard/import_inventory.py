# -*- coding: utf-8 -*-
# (c) 2015 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://gnu.org/licenses/agpl-3.0.html)

import base64
import csv
import io

from odoo import api, fields, models
from odoo.exceptions import UserError


class ImportInventory(models.TransientModel):
    _name = 'import.inventory'
    _description = 'Import inventory'

    def _get_default_location(self):
        ctx = self.env.context
        if 'active_id' in ctx:
            inventory_obj = self.env['stock.inventory']
            inventory = inventory_obj.browse(ctx['active_id'])
            return inventory.location_id or self.env['stock.location']
        return False

    data = fields.Binary('CSV', required=True)
    delimeter = fields.Char('Divisória', default=',')
    location = fields.Many2one('stock.location', 'Default Location',
                               default=_get_default_location, required=True)
    owner = fields.Many2one('res.partner', 'Proprietário')

    @api.multi
    def action_import(self):
        """Load Inventory data from the CSV file."""
        ctx = self.env.context
        stloc_obj = self.env['stock.location']
        inventory_obj = self.env['stock.inventory']
        inv_imporline_obj = self.env['stock.inventory.import.line']
        product_obj = self.env['product.product']
        inventory = inventory_obj
        if 'active_id' in ctx:
            inventory = inventory_obj.browse(ctx['active_id'])
        data = base64.b64decode(self.data)
        file_input = io.StringIO(data.decode('utf-8'))
        file_input.seek(0)
        location = self.location
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.DictReader(file_input, delimiter=delimeter,
                                lineterminator='\n', restval=False)
        keys = reader.fieldnames
        if ('codigo' not in keys or 'quantidade' not in keys):
            raise UserError("Arquivo CSV deve conter pelo menos codigo "
                            "e quantidade no cabeçalho.")
        inv_name = u'Estoque CSV - {}'.format(fields.Date.today())
        inventory.write({'name': inv_name,
                         'date': fields.Datetime.now(),
                         'imported': True,
                         'state': 'confirm',
                         })
        for row in reader:
            val = {}
            prod_location = location.id
            if row.get('local', False):
                locations = stloc_obj.search(
                    [('name', '=', row['local'])], limit=1)
                prod_location = locations.id if locations else prod_location
            product = product_obj.search([('default_code', '=',
                                           row['codigo'])], limit=1)
            val['owner_id'] = self.owner.id
            val['product'] = None or product.id
            val['lot'] = row['lote'] if 'lote' in row else None
            val['list_price'] = row['preco'].strip() if 'preco' in row \
                else product.list_price
            val['code'] = row['codigo']
            val['quantity'] = row['quantidade']
            val['location_id'] = prod_location
            val['inventory_id'] = inventory.id
            val['fail'] = True
            val['fail_reason'] = 'Não Processada'
            inv_imporline_obj.create(val)
