# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# © 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sale - Product variants",
    "summary": "Product variants in sale management",
    "description": "Product variants in sale management",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "product",
        "sale",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa",
    "contributors": [
        "Mikel Arregi <mikelarregi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Danimar Ribeiro <danimaribeiro@gmail.com>",
    ],
    "category": "Sales Management",
    "website": "http://www.trustcode.com.br",
    "data": [
        "security/ir.model.access.csv",
        "views/product_configurator.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
