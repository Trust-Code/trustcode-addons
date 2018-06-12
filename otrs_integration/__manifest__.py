# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{   # pylint: disable=C8101,C8103
    'name': "OTRS Integration",

    'summary': """""",

    'description': """""",
    'author': "Trustcode",
    'website': "http://www.trustcode.com.br",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'contributors': [
        'Felipe Paloschi <paloschi.eca@gmail.com>',
    ],
    'depends': ['helpdesk'],
    'data': [
        'views/res_users.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/helpdesk_ticket.xml',
        'wizard/otrs_tickets_import.xml',
    ],
}
