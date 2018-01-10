# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import time
import socket
import logging
import subprocess

import odoo
from odoo import api, fields, models
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTFT
from datetime import datetime, timedelta
from zipfile import ZipFile
_logger = logging.getLogger(__name__)

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


class BackupExecuted(models.Model):
    _name = 'backup.executed'
    _order = 'backup_date'

    def _generate_s3_link(self):
        return self.s3_id

    name = fields.Char(u'Arquivo', size=100)
    configuration_id = fields.Many2one('backup.config', string=u"Configuração")
    backup_date = fields.Datetime(string=u"Data")
    local_path = fields.Char(string=u"Caminho Local", readonly=True)
    s3_id = fields.Char(string=u"S3 Id", readonly=True)
    s3_url = fields.Char(
        u"Link S3", compute='_generate_s3_link', readonly=True)
    state = fields.Selection(
        string=u"Estado", default='not_started',
        selection=[('not_started', u'Não iniciado'),
                   ('executing', u'Executando'),
                   ('sending', u'Enviando'),
                   ('error', u'Erro'), ('concluded', u'Concluído')])


class BackupConfig(models.Model):
    _name = 'backup.config'

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

    def _get_total_backups(self):
        for item in self:
            item.backup_count = self.env['backup.executed'].search_count(
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
                             default="/opt/backups/database/")

    next_backup = fields.Datetime(string=u"Próximo Backup")
    last_filestore_backup = fields.Datetime(string=u"Último Filestore Backup")
    backup_count = fields.Integer(
        string=u"Nº Backups",
        compute='_get_total_backups')

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
                u'Erro ao executar backup - Verifique o log de erros')

    def _sync_filestore(self, bucket_name):
        if self.last_filestore_backup:
            last = datetime.strptime(
                self.last_filestore_backup, DTFT)
            if datetime.now() - timedelta(days=7) > last:
                date = datetime.now()
                self.last_filestore_backup = date
            else:
                date = self.last_filestore_backup
        else:
            date = datetime.now()
            self.last_filestore_backup = date

        method = 'aws s3 sync filestore/ s3://%s/filestores/%s/filestore/' % (
            bucket_name, date.strftime('%Y%m%d_%H_%M_%S')
        )
        subprocess.call(method, shell=True)

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

                zip_name = '%s_%s.zip' % (self.env.cr.dbname,
                                          time.strftime('%Y%m%d_%H_%M_%S'))
                zip_file = '%s/%s' % (rec.backup_dir, zip_name)

                with open(zip_file, 'wb') as dump_zip:
                    odoo.service.db.dump_db(
                        self.env.cr.dbname, dump_zip, 'zip')

                backup_env = self.env['backup.executed']

                archive = ZipFile(zip_file)
                path_to_filestore = []
                other_files = []
                for name in archive.namelist():
                    if name.startswith('filestore'):
                        path_to_filestore.append(name)
                    else:
                        other_files.append(name)
                archive.extractall()

                if rec.send_to_s3:
                    key = rec.send_for_amazon_s3(zip_file, zip_name,
                                                 self.env.cr.dbname)
                    loc = ''
                    if not key:
                        key = u'Erro ao enviar para o Amazon S3'
                        loc = zip_file
                    else:
                        loc = 'https://s3.amazonaws.com/%s_bkp_pelican/%s' % (
                            self.env.cr.dbname, key
                        )
                    backup_env.create({'backup_date': datetime.now(),
                                       'configuration_id': rec.id,
                                       's3_id': key, 'name': zip_name,
                                       'state': 'concluded',
                                       'local_path': loc})

                    if key:
                        os.remove(zip_file)
                        for name in path_to_filestore:
                            os.remove(name)
                        for name in other_files:
                            os.remove(name)

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

                bucket_name = '%s_bkp_pelican' % database

                bucket = conexao.create_bucket(bucket_name)

                k = Key(bucket)
                k.key = name_to_store
                k.set_contents_from_filename(file_to_send)
                self._sync_filestore(bucket_name)
                return k.key
            else:
                _logger.error(
                    u'Configurações do Amazon S3 não setadas, \
                    pulando armazenamento de backup')
        except Exception:
            _logger.error(u'Erro ao enviar dados para S3', exc_info=True)
