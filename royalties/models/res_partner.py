# -*- coding: utf-8 -*-
# © 2017 Fillipe Ramos, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    government = fields.Boolean(
        string="Governo",
        help="Marque este campo se o parceiro é uma instituição governamental")
    receive_royalties = fields.Boolean(
        string="Receive Royalties",
        help="Marque este campo se o parceiro é uma pessoa que recebe"
             "Royalties")
