# -*- coding: utf-8 -*-
# © 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://gnu.org/licenses/agpl-3.0.html)

import odoo.tests.common as common
from odoo.modules.module import get_module_resource
from odoo import fields, exceptions


class TestInventoryLineImport(common.TransactionCase):

    def get_file(self, filename):
        """Retrieve file from test data, encode it as base64 """
        path = get_module_resource('stock_inventory_import',
                                   'tests', 'data', filename)
        test_data = open(path).read()
        return test_data.encode('base64')

    def setUp(self):
        super(TestInventoryLineImport, self).setUp()
        self.inventory = self.env['stock.inventory'].create({
            'name': 'Test Inventory',
            'filter': 'file',
        })
        self.partner = self.env['res.partner'].create(dict(
            name='partner 1',
        ))
        self.importer = self.env['import.inventory'].with_context({
            'active_id': [self.inventory.id]}).create(
            {'data': self.get_file('stock_inventory_line.csv'),
             'owner': self.partner.id,
             'delimeter': ',',
             }
        )
        self.product = self.env['product.template'].create(dict(
            name='product 1',
            type='product',
            list_price=42,
            default_code='A1B2C',
        ))

    def test_import_inventory(self):
        self.assertTrue(self.importer.location)
        self.importer.action_import()
        self.assertTrue(self.inventory.imported)
        self.assertEqual(self.inventory.state, 'confirm')
        inv_name = u'Estoque CSV - {}'.format(fields.Date.today())
        self.assertEqual(self.inventory.name, inv_name)
        self.assertTrue(len(self.inventory.import_lines), 4)
        self.assertTrue(all((line.owner_id.id == self.partner.id for line in
                             self.inventory.import_lines)))
        self.assertTrue(self.inventory.import_lines[0].location_id)
        self.inventory.process_import_lines()
        self.assertTrue(len(self.inventory.line_ids), 3)
        self.assertTrue(self.inventory.import_lines.filtered(
            lambda a: a.fail))
        self.inventory.action_done()
        self.assertEqual(self.inventory.state, 'done')
        prod = self.env['product.product'].search([
            ('default_code', '=', 'A1B2C')])
        prod_line = self.env['stock.inventory.import.line'].search([
            ('code', '=', 'A1B2C')])
        self.assertEqual(1, len(prod_line))
        self.assertEqual(prod_line.product.id, prod.id)

    def test_import_inventory_no_lines_processed(self):
        importer = self.env['import.inventory'].with_context({
            'active_id': [self.inventory.id]}).create(
            {'data': self.get_file('stock_inventory_line_empty.csv'),
             'delimeter': '',
             }
        )
        self.assertEqual(importer.delimeter, '')
        importer.action_import()
        with self.assertRaises(exceptions.UserError):
            self.inventory.process_import_lines()

    def test_import_inventory_no_code(self):
        importer = self.env['import.inventory'].with_context({
            'active_id': [self.inventory.id]}).create(
            {'data': self.get_file('stock_inventory_line_no_code.csv'),
             'delimeter': ',',
             }
        )
        with self.assertRaises(exceptions.UserError):
            importer.action_import()
