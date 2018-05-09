# -*- coding: utf-8 -*-
# (c) 2015 AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://gnu.org/licenses/agpl-3.0.html)

{   # pylint: disable=C8101,C8103
    "name": "Stock Inventory Import from CSV file",
    "version": "11.0.1.0.0",
    "category": "Generic Modules",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "TrustCode,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "description": "Módulo para importar estoques a partir de um CSV.",
    "contributors": [
        "Daniel Campos <danielcampos@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Esther Martín <esthermartin@avanzosc.es>",
        "Alessandro Martini <alessandrofmartini@gmail.com>",
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    "website": "http://www.trustcode.com.br",
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_inventory.xml",
        "views/inventory.xml",
    ],
    "installable": True,
}
