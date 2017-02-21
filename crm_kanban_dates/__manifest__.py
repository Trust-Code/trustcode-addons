# -*- coding: utf-8 -*-
# © 2015 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Customizações para o kanban e CRM',
    'description': 'Customizações para o Kanban e CRM',
    'summary': """Alterações desenvolvidas para Kanban e CRM""",
    'version': '10.0.1.0.0',
    'category': 'Customization',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
        'Alessandro Fernandes Martini <fmartini@gmail.com>'
    ],
    'depends': [
        'br_crm_zip', 'crm'
    ],
    'data': [
        'views/crm_lead.xml',
        'views/crm_stage.xml',
    ],
}
