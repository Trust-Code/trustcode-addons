# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
import json
import requests
from unicodedata import normalize


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    kk_site_id = fields.Many2one(
        'kk.sites',
        string="Site",
        ondelete='restrict')

    description_proposta = fields.Html(string="Descrição para proposta")

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
        name = str(number + 1).zfill(2) + '_' + self.name.replace(
            ':', '_').strip()
        name = normalize(
            'NFKD', name).encode('ASCII', 'ignore').decode('ASCII').upper()
        pasta += '/' + name
        domain = 'https://' + host + '.egnyte.com/pubapi/v1/fs' + pasta
        data = {"action": "add_folder"}
        data = json.dumps(data)
        response = requests.post(domain, headers=headers, data=data)
        link = project.kk_site_id.pasta_servidor + '/' + name
        if response.ok:
            self.order_id.message_post(
                'Criada pasta de serviço no servidor: <a href=%s>%s</a>'
                % (link.replace(' ', '%20'), project.name))
            project.arquivado_fisicamente = link
        else:
            self.order_id.message_post(
                'Problemas ao criar pasta no servidor do egnyte: %s'
                % response.text)

    def _timesheet_create_project(self, task=False):
        super(SaleOrderLine, self)._timesheet_create_project(task)
        self.project_id.kk_site_id = self.kk_site_id
        if self.kk_site_id and self.env.user.company_id.egnyte_active:
            self._create_server_service_dir()

    @api.onchange('product_id')
    def _onchange_product(self):
        setattr(self, 'description_proposta',
                self.product_id.description_proposta)
