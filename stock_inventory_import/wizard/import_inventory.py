# -*- coding: utf-8 -*-
# (c) 2015 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://gnu.org/licenses/agpl-3.0.html)

import base64
import csv
import cStringIO

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

    data = fields.Binary('File', required=True)
    name = fields.Char('Filename')
    delimeter = fields.Char('Delimeter', default=',',
                            help='Default delimeter is ","')
    location = fields.Many2one('stock.location', 'Default Location',
                               default=_get_default_location, required=True)

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
        # Decode the file data
        data = base64.b64decode(self.data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        location = self.location
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise UserError("Not a valid file!")
        keys = reader_info[0]
        # check if keys exist
        if not isinstance(keys, list) or ('code' not in keys or
                                          'quantity' not in keys):
            raise UserError("Not 'code' or 'quantity' keys found")
        del reader_info[0]
        values = {}
        inv_name = u'{} - {}'.format(self.name, fields.Date.today())
        inventory.write({'name': inv_name,
                         'date': fields.Datetime.now(),
                         'imported': True,
                         'state': 'confirm',
                         })
        for i in range(len(reader_info)):
            val = {}
            field = reader_info[i]
            values = dict(zip(keys, field))
            prod_location = location.id
            if 'location' in values and values['location']:
                locations = stloc_obj.search([('name', '=',
                                               values['location'])])
                if locations:
                    prod_location = locations[:1].id
            prod_lst = product_obj.search([('default_code', '=',
                                            values['code'])])
            if prod_lst:
                val['product'] = prod_lst[0].id
            if 'lot' in values and values['lot']:
                val['lot'] = values['lot']
            val['code'] = values['code']
            val['quantity'] = values['quantity']
            val['location_id'] = prod_location
            val['inventory_id'] = inventory.id
            val['fail'] = True
            val['fail_reason'] = 'No processed'
            val['standard_price'] = values['standard_price']
            inv_imporline_obj.create(val)
