from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    expedition_notes = fields.Text('Expedition Notes')
