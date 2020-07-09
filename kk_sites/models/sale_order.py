# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
import json
import time
import requests
from unicodedata import normalize
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        lines = self.order_line.filtered(
            lambda x: x.invoice_status != 'invoiced')
        if all(not (line.is_invoice_ok and line.purchase_order) for line in
                lines):
            raise UserError('Não é possível faturar a ordem %s pois nenhuma das\
                linhas faturáveis está liberada para faturamento e ou a\
                ordem de compra não está preenchida.\n\
                Acesse as linhas que deseja faturar, marque a opção "Liberar\
                para faturamento" e preencha o campo "Ordem de compra"'
                            % self.name)
        else:
            return super(SaleOrder, self)._prepare_invoice()

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        self.update({'partner_invoice_id': False})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    kk_site_id = fields.Many2one(
        'kk.sites',
        string="Site",
        ondelete='restrict')

    description_proposta = fields.Html(string="Descrição para proposta")

    is_invoice_ok = fields.Boolean('Liberar para Faturamento')

    purchase_order = fields.Char('Ordem de Compra')

    def invoice_line_create(self, invoice_id, qty):
        lines = super(SaleOrderLine, self).invoice_line_create(invoice_id, qty)
        for line in lines:
            if any(not (item.is_invoice_ok and item.purchase_order) for item
                    in line.sale_line_ids):
                line.unlink()
        return lines

    def get_next_folder_number(self, project):
        link = project.kk_site_id.pasta_servidor
        res = self.env['kk.sites'].get_server_folders(link, False)
        numbers = []
        if not res.get('folders'):
            return 0
        for item in res['folders']:
            numbers.append(item['name'][:2])
        for index in range(len(numbers)):
            try:
                numbers[index] = int(numbers[index])
            except ValueError:
                numbers[index] = 0
        numbers.sort()
        return numbers[-1]

    def _create_server_service_dir(self):
        project = self.project_id
        access_token = self.env.user.company_id.egnyte_acess_token
        host = self.env.user.company_id.egnyte_host
        headers = {'Authorization': 'Bearer ' + access_token,
                   'Content-Type': 'application/json'}
        number = self.get_next_folder_number(project)
        pasta = project.kk_site_id.pasta_servidor.replace(
            'https://' + host + '.egnyte.com/app/index.do#storage/files/1',
            '').replace('%20', ' ')

        numero = 1 if number == 0 else number
        name = '{0}_{1} ({2})'.format(
            str(numero + 1).zfill(2), self.product_id.default_code,
            self.order_id.name).replace(':', '_').strip()
        name = normalize(
            'NFKD', name).encode('ASCII', 'ignore').decode('ASCII').upper()
        name = name.replace('[', '(').replace(']', ')')
        pasta1 = pasta + '/' + '00_ART'
        pasta2 = pasta + '/' + '01_DADOS {0}'.format(
            self.order_id.partner_id.commercial_partner_id.name.upper())
        pasta3 = pasta + '/' + name

        domain = 'https://' + host + '.egnyte.com/pubapi/v1/fs'
        data = {"action": "add_folder"}
        data = json.dumps(data)

        if number == 0:
            response = requests.post(domain + pasta1, headers=headers, data=data)
            if not response.ok:
                self.order_id.message_post(
                    'Problemas ao criar pasta no servidor do egnyte: %s'
                    % response.text)
            time.sleep(0.5)
            response = requests.post(domain + pasta2, headers=headers, data=data)
            if not response.ok:
                self.order_id.message_post(
                    'Problemas ao criar pasta no servidor do egnyte: %s'
                    % response.text)
            time.sleep(0.5)
            response = requests.post(domain + pasta3, headers=headers, data=data)
            time.sleep(0.5)
        else:
            response = requests.post(domain + pasta3, headers=headers, data=data)
            time.sleep(0.5)

        link = project.kk_site_id.pasta_servidor + '/' + name
        if response.ok:
            self.order_id.message_post(
                'Criada pasta de serviço no servidor: <a href=%s>%s</a>'
                % (link.replace(' ', '%20'), self.name))
        else:
            self.order_id.message_post(
                'Problemas ao criar pasta no servidor do egnyte: %s'
                % response.text)

    def _timesheet_create_task_prepare_values(self):
        v = super(SaleOrderLine, self)._timesheet_create_task_prepare_values()
        v['kk_site_id'] = self.kk_site_id.id
        return v

    def _timesheet_create_project(self, task=False):
        super(SaleOrderLine, self)._timesheet_create_project(task)
        self.project_id.kk_site_id = self.kk_site_id
        if self.kk_site_id and self.env.user.company_id.egnyte_active:
            self._create_server_service_dir()

    @api.onchange('product_id')
    def _onchange_product(self):
        setattr(self, 'description_proposta',
                self.product_id.description_proposta)
