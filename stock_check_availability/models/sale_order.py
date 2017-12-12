# -*- coding: utf-8 -*-
# © 2017 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    """ This only checks for the items required to manufacture.
    Basicaly, it checks for the quantity of the 'ingredients' in stock and
    the quantity required for the manufacture.
    """
    def _check_routing(self):
        res = super(SaleOrderLine, self)._check_routing()
        """ If availability(res) is true, returns true, since it
        is already in stock.
        """
        if res:
            return res

        """ Now, given that availability is false, it checks the
        possibility of it being a manufacturable item, and checks for
        the available quantity(in stock).
        """
        # Searches for the necessary 'ingredients' list
        lista_manufatura = self.product_id.bom_ids
        # Checks if something(ingredient list) was found. If not,
        # returns False
        if not lista_manufatura:
            return res

        # Now, it checks the availability of each item in the
        # ingredient list, garanteeing that there's enough to
        # manufacture the main product. If there's not enough,
        # returns False; else, True.
        for item in lista_manufatura.bom_line_ids:
            if item.product_id.qty_available < item.product_qty:
                return res
        return True
