# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    track_ref = fields.Char(string="Etiqueta de Rastreamento")
