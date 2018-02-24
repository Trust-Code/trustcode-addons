# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
import json
import requests
from unicodedata import normalize


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    kk_site_id = fields.Many2one('kk.sites', string="Site")

    description_proposta = fields.Html(string="Descrição para proposta")

    def _create_server_service_dir(self, res):
        task = res[self.id]
        access_token = self.env.user.company_id.egnyte_acess_token
        host = self.env.user.company_id.egnyte_host
        headers = {'Authorization': 'Bearer ' + access_token,
                   'Content-Type': 'application/json'}
        pasta = task.kk_site_id.pasta_servidor.replace(
            'https://' + host + '.egnyte.com/app/index.do#storage/files/1',
            '').replace('%20', ' ')
        name = task.name.replace(':', '_').strip()
        pasta += '/' + normalize('NFKD', name).encode('ASCII', 'ignore').\
            decode('ASCII').upper()
        domain = 'https://' + host + '.egnyte.com/pubapi/v1/fs' + pasta
        data = {"action": "add_folder"}
        data = json.dumps(data)
        response = requests.post(domain, headers=headers, data=data)
        self.env['kk.sites'].parse_response(response)

    @api.multi
    def _timesheet_find_task(self):
        result = super(SaleOrderLine, self)._timesheet_find_task()
        for so_line in self:
            task = result[so_line.id]
            task.write({'kk_site_id': so_line.kk_site_id.id,
                        'name': '%s:%s' % (so_line.order_id.name,
                                           so_line.product_id.name)})
            self._create_server_service_dir(result)
        return result

    @api.onchange('product_id')
    def _onchange_product(self):
        setattr(self, 'description_proposta',
                self.product_id.description_proposta)
