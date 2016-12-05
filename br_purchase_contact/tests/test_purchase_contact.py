# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import faker
from datetime import datetime
from odoo.tests.common import TransactionCase


def fake_cnpj():
    import random
    cnpj_s_dv = [random.randint(0, 9) for _ in range(12)]
    peso = [5 - i for i in range(4)] + [9 - j for j in range(8)]
    peso = sum([cnpj_s_dv[k] * peso[k] for k in range(12)]) % 11
    resto = 0 if peso < 2 else 11 - peso
    cnpj_s_dv += [resto]
    peso = [6 - i for i in range(5)] + [9 - j for j in range(8)]
    peso = sum([cnpj_s_dv[k] * peso[k] for k in range(13)]) % 11
    resto = 0 if peso < 2 else 11 - peso
    cnpj_s_dv += [resto]
    cpf = ''.join([str(d) for d in cnpj_s_dv])
    return cpf


class TestPurchaseContact(TransactionCase):

    def setUp(self):
        super(TestPurchaseContact, self).setUp()

        empresa_1_only_child = {
            'type': 'contact', 'name': 'ONLY CHILD',
        }

        empresa_2_child_1 = {
            'type': 'contact', 'name': 'CHILD 1',
        }
        empresa_2_child_2 = {
            'type': 'contact', 'name': 'CHILD 2',
        }
        empresa_2_childs = [(0, False, empresa_2_child_1),
                            (0, False, empresa_2_child_2)]

        self.partner_company_1 = self.env['res.partner'].create({
            'company_type': 'company', 'is_company': True,
            'name': 'EMPRESA 1', 'legal_name': 'EMPRESA 1',
            'cnpj_cpf': fake_cnpj(),
            'child_ids': [(0, False, empresa_1_only_child)],
        })

        self.partner_company_2 = self.env['res.partner'].create({
            'company_type': 'company', 'is_company': True,
            'name': 'EMPRESA 1', 'legal_name': 'EMPRESA 1',
            'cnpj_cpf': fake_cnpj(),
            'child_ids': empresa_2_childs,
        })

        self.fisical_person = self.env['res.partner'].create({
            'company_type': 'person', 'is_company': False,
            'name': 'PERSONA', 'cnpj_cpf': faker.Fake('pt_BR').cpf(),
        })

    def test_contact_insertion(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_company_1.id,
            'date_order': datetime.now()
        })
        self.assertEqual(sale_order.partner_contact_id.id,
                         self.partner_company_1.child_ids[0].id)
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_company_2.id,
            'date_order': datetime.now()
        })
        self.assertEqual(sale_order.partner_contact_id.id,
                         self.partner_company_1.child_ids[0].id)
        # self.assertNone(sale_order.partner_contact_id)
