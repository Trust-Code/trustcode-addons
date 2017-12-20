# -*- coding: utf-8 -*-
# © 2017 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import time
import socket
import logging

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

try:
    from fabric.api import local
except ImportError:
    _logger.debug(u'Cannot import fabric')

try:
    from boto.s3.connection import S3Connection
    from boto.s3.key import Key
except ImportError:
    _logger.debug(u'Cannot import boto and or odoorpc')


def execute(connector, method, *args):
    res = False
    try:
        res = getattr(connector, method)(*args)
    except socket.error as e:
        raise e
    return res


class BackupExecuteEDX(models.Model):
    _name = 'backup.executed.edx'
    _order = 'backup_date'

    def _compute_generate_s3_link(self):
        return self.s3_id

    name = fields.Char(u'Arquivo', size=100)
    configuration_id = fields.Many2one('backup.config.edx',
                                       string=u"Configuração")
    backup_date = fields.Datetime(string=u"Data")
    local_path = fields.Char(string=u"Caminho Local", readonly=True)
    s3_id = fields.Char(string=u"S3 Id", readonly=True)
    s3_url = fields.Char(
        u"Link S3", compute='_compute_generate_s3_link', readonly=True)
    state = fields.Selection(
        string=u"Estado", default='not_started',
        selection=[('not_started', u'Não iniciado'),
                   ('executing', u'Executando'),
                   ('sending', u'Enviando'),
                   ('error', u'Erro'), ('concluded', u'Concluído')])


class BackupConfigEDX(models.Model):
    _name = 'backup.config.edx'

    @api.multi
    @api.depends('interval')
    def name_get(self):
        result = []
        for backup in self:
            result.append(
                (backup.id,
                 self.env.cr.dbname +
                 " - " +
                 backup.interval))
        return result

    def _compute_get_total_backups(self):
        for item in self:
            item.backup_count = self.env['backup.executed.edx'].search_count(
                [('configuration_id', '=', item.id)])

    host = fields.Char(string=u"Endereço", size=200, default='localhost')
    port = fields.Char(string=u"Porta", size=10, default='8069')
    database_name = fields.Char(string=u'Banco de dados', size=100)
    admin_password = fields.Char(string=u'Senha Admin', size=100)
    interval = fields.Selection(
        string=u"Período",
        selection=[('hora', u'1 hora'), ('seis', u'6 horas'),
                   ('doze', u'12 horas'), ('diario', u'Diário')])

    send_to_s3 = fields.Boolean(u'Enviar Amazon S3 ?')
    aws_access_key = fields.Char(string=u"Chave API S3", size=100)
    aws_secret_key = fields.Char(string=u"Chave Secreta API S3", size=100)
    backup_dir = fields.Char(string=u"Diretório", size=300,
                             default="/home/johnychenjy/")

    next_backup = fields.Datetime(string=u"Próximo Backup")
    backup_count = fields.Integer(
        string=u"Nº Backups",
        compute='_compute_get_total_backups')

    def _set_next_backup(self):
        if self.interval == 'hora':
            self.next_backup = datetime.now() + timedelta(hours=1)
        elif self.interval == 'seis':
            self.next_backup = datetime.now() + timedelta(hours=6)
        elif self.interval == 'doze':
            self.next_backup = datetime.now() + timedelta(hours=12)
        else:
            self.next_backup = datetime.now() + timedelta(days=1)

    @api.multi
    def execute_backup(self):
        try:
            self.write({'next_backup': datetime.now()})
            self.schedule_backup()
        except Exception:
            _logger.error(u'Erro ao efetuar backup', exc_info=True)
            raise Warning(
                _(u'Erro ao executar backup - Verifique o log de erros'))

    @api.model
    def schedule_backup(self):
        confs = self.search([])
        for rec in confs:
            if rec.next_backup:
                next_backup = datetime.strptime(
                    rec.next_backup,
                    '%Y-%m-%d %H:%M:%S')
            else:
                next_backup = datetime.now()
            if next_backup < datetime.now():

                if not os.path.isdir(rec.backup_dir):
                    os.makedirs(rec.backup_dir)

                zip_name = 'edx_%s.tar.gz' % (time.strftime('%Y%m%d_%H_%M_%S'))
                zip_file = '%s%s' % (rec.backup_dir, zip_name)

                # Backup being done here! The file is renamed later.
                local(
                    'fab backup -f ~/projetos/odoo11/\
trustcode-addons/backup_edx/models/fabfile.py')
                local('mv ~/backup.tar.gz ~/' + zip_name)

                backup_env = self.env['backup.executed.edx']

                if rec.send_to_s3:
                    key = rec.send_for_amazon_s3(zip_file, zip_name, 'edx')
                    loc = ''
                    if not key:
                        key = u'Erro ao enviar para o Amazon S3'
                        loc = zip_file
                    else:
                        loc = 'https://s3.amazonaws.com/edx_bkp_pelican/%s' % (
                            key
                        )
                    backup_env.create({'backup_date': datetime.now(),
                                       'configuration_id': rec.id,
                                       's3_id': key, 'name': zip_name,
                                       'state': 'concluded',
                                       'local_path': loc})
                    if key:
                        os.remove(zip_file)
                else:
                    backup_env.create(
                        {'backup_date': datetime.now(), 'name': zip_name,
                         'configuration_id': rec.id, 'state': 'concluded',
                         'local_path': zip_file})
                rec._set_next_backup()

    def send_for_amazon_s3(self, file_to_send, name_to_store, database):
        try:
            if self.aws_access_key and self.aws_secret_key:
                access_key = self.aws_access_key
                secret_key = self.aws_secret_key

                conexao = S3Connection(access_key, secret_key)
                bucket_name = 'edx_bkp_pelican'
                bucket = conexao.create_bucket(bucket_name)

                k = Key(bucket)
                k.key = name_to_store
                k.set_contents_from_filename(file_to_send)
                return k.key
            else:
                _logger.error(
                    u'Configurações do Amazon S3 não setadas, \
                    pulando armazenamento de backup')
        except Exception:
            _logger.error(u'Erro ao enviar dados para S3', exc_info=True)
