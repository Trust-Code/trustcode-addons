# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError, RedirectWarning
import requests
import json
from datetime import datetime
import math
import locale
import re


class KKSites(models.Model):
    _name = 'kk.sites'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    cod_site_kk = fields.Char(
        string="Código do Site: ",
        store=True,
        track_visibility='always')

    partner_id = fields.Many2one(
        'res.partner',
        string="Cliente",
        required=True,
        track_visibility='onchange')

    site_id = fields.Char(
        string="ID do Site: ",
        required=True,
        track_visibility='onchange')

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(string='CEP')
    district = fields.Char(string="Bairro")
    city_id = fields.Many2one(
        'res.state.city',
        string="Cidade",
        required=True,
        track_visibility='onchange')
    state_id = fields.Many2one(
        "res.country.state",
        string='Estado',
        ondelete='restrict',
        required=True,
        track_visibility='onchange')
    country_id = fields.Many2one(
        'res.country',
        string='País',
        ondelete='restrict',
        required=True)
    number = fields.Char(string='Número')

    referencia = fields.Char(string="Referência")

    coordenadas = fields.Char(
        string="Coodenadas em graus decimais (Latitude, Longitude)")

    tipo_acesso = fields.Char(string="Tipo de Acesso")

    local_retirada_chave = fields.Char(string='Local de Retirada da Chave')

    tipo_site = fields.Selection(
        [
            ('greenfield', 'Greenfield'),
            ('indoor', 'Indoor'),
            ('rooftop', 'Roof Top'),
            ('tunel', 'Túnel')
        ],
        string="Tipo de Site"
    )

    tipo_estrutura = fields.Selection(
        [
            ('cavalete_auto', 'Cavalete Metálico Autoportante'),
            ('cavalete_estaiado', 'Cavalete Metálico Estaiado'),
            ('fast_size', 'Fast Site'),
            ('mastro_metalico', 'Mastro Metálico'),
            ('poste_concreto', 'Poste de Concreto'),
            ('poste_madeira', 'Poste de Madeira'),
            ('poste_metalico', 'Poste Metálico'),
            ('torre_concreto', 'Torre de Concreto'),
            ('torre_auto', 'Torre Metálica Autoportante'),
            ('torre_estaiada', 'Torre Metálica Estaiada'),
            ('poste_torre', 'Poste Metálico + Torre Metálica Autoportante')

        ],
        string="Tipo de Estrutura"
    )

    secao_transversal = fields.Selection(
        [
            ('circular', 'Circular'),
            ('dodecagonal', 'Dodecagonal'),
            ('quadrada', 'Quadrada'),
            ('triangular', 'Triangular'),
            ('triangular_quadrada', 'Triangular + Quadrada'),
            ('retangular', 'Retangular'),
        ],
        string="Seção Transversal EV"
    )

    fabricante_id = fields.Many2one(
        'res.partner', string="Fabicante da EV")

    modelo = fields.Char('Modelo EV')

    altura_total = fields.Float('Altura Total EV (m)')

    ampliada = fields.Boolean('EV Ampliada?')

    abertura_base = fields.Integer('Abertura da Base (mm)')

    perfil_montante = fields.Selection(
        [
            ('cantoneira', 'Cantoneira (L)'),
            ('cantoneira_dobrada', 'Cantoneira Dobrada 60º (S)'),
            ('dobrada_l', 'Cantoneira Dobrada 60º (S) + Cantoneira (L)'),
            ('dobrada_dubla', 'Cantoneira Dobrada 60º Dupla (2S)'),
            ('cantoneira_dupla', 'Cantoneira Dupla (2L)'),
            ('chapa_dobrada', 'Chapa Dobrada (V)'),
            ('chapa_dob_cant_l', 'Chapa Dobrada (V) + Cantoneira (L)'),
            ('chapa_dob_cant_dob', 'Chapa Dobrada (V) +\
                 Cantoneira Dobrada 60º (S)'),
            ('chapa_dob_omega', 'Chapa Dobrada (V) + Ômega (O)'),
            ('omega', 'Ômega (O)'),
            ('omega_dupla', 'Ômega Dupla (2O)'),
            ('tubular', 'Tubular (TB)'),
            ('tubular_cantoneira', 'Tubular (TB) + Cantoneira (L)'),
            ('perfil_u', 'Perfil U (U)'),
            ('barra_redonda_macica', 'Barra Redonda Maciça (BR)')
        ],
        string='Perfil do Montante EV')

    tipo_fundacao = fields.Selection(
        [
            ('estaca_raiz', 'Estaca Raiz'),
            ('estaca_raiz_tirantes', 'Estaca Raiz + Tirantes'),
            ('chapa_metal', 'Chapa Metálica'),
            ('estaca_metal', 'Estaca Metálica'),
            ('estaca_raiz', 'Estaca Raiz'),
            ('estacao', 'Estacão'),
            ('raider', 'Radier'),
            ('sapata', 'Sapata'),
            ('tirante', 'Tirante'),
            ('tubo_metalico', 'Tubo Metálico'),
            ('tubulao', 'Tubulão'),
            ('tubulao_estaca', 'Tubulão + Estaca'),
            ('viga', 'Viga'),
        ],
        string="Tipo de Fundação")

    dimensoes_fundacao = fields.Char(string="Dimensões da Fundação (cm x cm)")

    profundidade_fundacao = fields.Integer(
        string='Profundidade da Fundação (cm)')

    notes = fields.Text("Observações")

    pasta_servidor = fields.Char(
        string="Pasta no Servidor",
        track_visibility='onchange')

    dir_ids = fields.One2many(
        comodel_name='kk.files',
        inverse_name='site_id',
        string="Diretórios",
        readonly=True,
        store=True)

    project_count = fields.Integer(
        string='Contador Projetos', compute='_compute_project_count')

    @api.multi
    def _compute_project_count(self):
        for item in self:
            count = self.env['project.project'].search_count(
                [('kk_site_id', '=', item.id)])
            item.update({'project_count': count})

    def check_cod_site_kk(self, cod, partner, sites):
        numbers = cod.split('/')
        try:
            if len(numbers) != 2:
                raise Exception
            int(numbers[0])
            int(numbers[1])
        except Exception:
            raise UserError('Código Site KK inválido.\
                Formato padrão: 000/00')
        if numbers[0] != partner.ref:
            raise UserError('Código Site KK inválido.\
                Digitos iniciais não correpondem à Referência Interna do\
                Cliente!')
        if sites:
            if cod in [site.cod_site_kk for site in sites]:
                raise UserError('Já existe um site com este código')

    def seq_cod_site_kk(self, vals):
        sites = self.search(
            [('partner_id', '=', vals['partner_id'])])
        partner = self.env['res.partner'].search(
            [('id', '=', vals['partner_id'])])
        cod = ''
        if vals.get('cod_site_kk'):
            self.check_cod_site_kk(vals['cod_site_kk'], partner, sites)
            cod = vals['cod_site_kk']
        else:
            seq = [0]
            for site in sites:
                try:
                    seq.append(int(site.cod_site_kk.split('/')[1]))
                except Exception:
                    seq.append(0)
            seq.sort()
            if not partner.ref:
                action = self.env.ref('contacts.action_contacts')
                raise RedirectWarning(
                    'Configure a Referência Interna do cliente.',
                    action.id, 'Ir para contatos')
            cod = "%s/%s" % (partner.ref, str(seq[-1] + 1).zfill(2))
        return cod

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            return {'domain': {'state_id': [(
                'country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            return {'domain': {'city_id': [(
                'state_id', '=', self.state_id.id)]}}
        else:
            return {'domain': {'city_id': []}}

    def get_server_folders(self, link, create_folders=True):
        host = self.env.user.company_id.egnyte_host
        pasta = link.replace(
            'https://' + host + '.egnyte.com/app/index.do#storage/files/1',
            '').replace('%20', ' ')
        headers = {'Authorization': 'Bearer ' +
                   self.env.user.company_id.egnyte_acess_token}
        domain = 'https://' + host + '.egnyte.com/pubapi/v1/fs' + pasta
        response = requests.get(domain, headers=headers)
        if '200' not in str(response):
            raise UserError('Ocorreu um erro ao tentar checar as pastas do \
                servidor: %s' % response.content)
        if create_folders:
            return self._create_folders_objects(response.json(), link)
        else:
            return response.json()

    def _create_folders_objects(self, res, link):
        vals = []
        if 'folders' in res:
            for item in res['folders']:
                vals.append({
                    'site_id': self.id,
                    'name': item['name'],
                    'link': link + '/' + item['name'],
                    'file_type': 'folder',
                    'last_modified': datetime.fromtimestamp(
                        item['lastModified']/1000)
                })

        if 'files' in res:
            for item in res['files']:
                previous = locale.getlocale(locale.LC_TIME)
                locale.setlocale(locale.LC_TIME, 'en_US.utf8')
                data = datetime.strptime(
                    item['last_modified'], '%a, %d %b %Y %H:%M:%S %Z')
                locale.setlocale(locale.LC_TIME, previous)
                vals.append({
                    'site_id': self.id,
                    'name': item['name'],
                    'file_type': 'file',
                    'size': item['size'],
                    'last_modified': data
                })
        return vals

    def refresh_list_dir(self):
        self.dir_ids.unlink()
        values = self.get_server_folders(self.pasta_servidor)
        if values:
            self.write({'dir_ids': [(0, 0, vals) for vals in values]})

    def _mask_dimensoes_fundacao(self, dimensoes):
        dimensoes = dimensoes.strip()
        try:
            dim = dimensoes.split('x')
            if len(dim) != 2:
                dim = dimensoes.split(' ')
            if len(dim) != 2:
                dim = dimensoes.split('-')
            if len(dim) != 2:
                raise Exception
            comprimento, largura = [int(item.strip()) for item in dim]
            return '{} x {}'.format(comprimento, largura)
        except Exception:
            raise ValidationError(
                "Verifique se as dimensões da fundação são válidas.\
                    \n Formato padrão: XXX x XXX")

    def _mask_coordenadas(self, coord):
        if 'maps.google' in coord:
            return coord
        coord = coord.split(',')
        if len(coord) > 2:
            raise ValidationError(
                "Use ponto para delimitar casas decimais no campo coordenadas.\
                \n Formato padrão: -XX.XXXXX, -XX.XXXXX")
        try:
            coord = [float(item.strip()) for item in coord]
            return 'https://maps.google.com?q={},{}'.format(
                coord[0], coord[1])
        except Exception:
            raise ValidationError("Verifique se as coordenadas são válidas.\
                Formato padrão: -XX.XXXXX, -XX.XXXXX")

    @api.multi
    def write(self, vals):
        if vals.get('cod_site_kk'):
            sites = self.search(
                [('partner_id', '=', self.partner_id.id)])
            self.check_cod_site_kk(vals['cod_site_kk'], self.partner_id, sites)
        if vals.get('coordenadas'):
            vals['coordenadas'] = self._mask_coordenadas(vals['coordenadas'])
        if vals.get('dimensoes_fundacao'):
            vals['dimensoes_fundacao'] = self._mask_dimensoes_fundacao(
                vals['dimensoes_fundacao'])
        if vals.get('partner_id'):
            vals['cod_site_kk'] = self.seq_cod_site_kk(vals)
        return super(KKSites, self).write(vals)

    def _get_company_folder(self, vals):
        host = self.env.user.company_id.egnyte_host
        partner = self.env['res.partner'].search([
            ('id', '=', vals['partner_id'])])
        if partner.pasta_servidor:
            return partner.pasta_servidor.replace(
                'https://' + host + '.egnyte.com/app/index.do#storage/files/1',
                '').replace('%20', ' '), partner.pasta_servidor
        else:
            raise UserError("Campo 'Pasta no Servidor' no cadastro do cliente\
                não está preenchido")

    def parse_response(self, response):
        if response.ok:
            return
        else:
            message = response.text
            if 'already exists' in message:
                message = 'Já existe uma pasta com este nome para este\
                    cliente no servidor'
            raise UserError('Erro ao tentar criar pasta no servidor: \
                %s' % message)

    def _create_server_dir(self, vals):
        access_token = self.env.user.company_id.egnyte_acess_token
        headers = {'Authorization': 'Bearer ' + access_token,
                   'Content-Type': 'application/json'}
        company_folder, company_pasta_servidor = self._get_company_folder(vals)
        site_folder = vals['cod_site_kk'].split('/')[1] + '_' + vals['site_id']
        domain = "https://" + self.env.user.company_id.egnyte_host +\
            ".egnyte.com/pubapi/v1/fs" + company_folder + '/' + site_folder
        data = {"action": "add_folder"}
        data = json.dumps(data)
        response = requests.post(domain, headers=headers, data=data)
        self.parse_response(response)
        vals.update({'pasta_servidor': company_pasta_servidor + '/' +
                     site_folder})

    @api.model
    def create(self, vals):
        vals['cod_site_kk'] = self.seq_cod_site_kk(vals)
        if not vals.get('pasta_servidor') and\
                self.env.user.company_id.egnyte_active:
            self._create_server_dir(vals)
        if vals.get('coordenadas'):
            vals['coordenadas'] = self._mask_coordenadas(vals['coordenadas'])
        if vals.get('dimensoes_fundacao'):
            vals['dimensoes_fundacao'] = self._mask_dimensoes_fundacao(
                vals['dimensoes_fundacao'])
        return super(KKSites, self).create(vals)

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s - %s" % (
                rec.cod_site_kk, rec.site_id or '')))
        return result

    @api.onchange('zip')
    def _onchange_zip(self):
        cep = re.sub('[^0-9]', '', self.zip or '')
        if len(cep) == 8:
            self.zip_search(cep)

    @api.multi
    def zip_search(self, cep):
        self.zip = "%s-%s" % (cep[0:5], cep[5:8])
        res = self.env['br.zip'].search_by_zip(zip_code=self.zip)
        if res:
            self.update(res)

    def action_view_projects(self):
        projetos = self.env['project.project'].search(
            [('kk_site_id', '=', self.id)])
        result = self.env.ref('project.open_view_project_all').read()[0]
        result['context'] = {}
        result['domain'] = [('id', 'in', projetos.ids)]
        return result


class KKFiles(models.Model):
    _name = 'kk.files'

    site_id = fields.Many2one('kk.sites', 'Id do Site')
    parent_id = fields.Many2one('kk.files', 'Pasta pai')
    link = fields.Char('Link no Servidor')
    name = fields.Char('Nome')
    size = fields.Char('Tamanho')
    file_type = fields.Selection(
        [('file', 'Arquivo'),
         ('folder', 'Pasta')],
        string="Tipo")
    last_modified = fields.Datetime('Última Modificação')

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    @api.model
    def create(self, vals):
        if vals.get('size'):
            vals['size'] = self.convert_size(int(vals['size']))
        return super(KKFiles, self).create(vals)

    def get_dir_function(self, kk_file, folder):
        if kk_file.site_id:
            return kk_file.site_id.get_server_folders(folder)
        else:
            return self.get_dir_function(kk_file.parent_id, folder)

    def open_folder_tree(self):
        dirs = self.get_dir_function(self, self.link)
        self.env['kk.files'].search([('parent_id', '=', self.id)]).unlink()
        ids = []
        for item in dirs:
            item['site_id'] = False
            item['parent_id'] = self.id
            ids.append(self.create(item))
        ids = [item.id for item in ids]

        return {"type": "ir.actions.act_window",
                "res_model": "kk.files",
                "views": [[False, "tree"]],
                "name": u"Diretórios",
                "target": "new",
                "domain": [["id", "in", ids]]}
