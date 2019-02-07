# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import re
import time
import socket
import logging

import odoo
from odoo import api, fields, models
from odoo.exceptions import Warning
from datetime import datetime, timedelta

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
    @api.depends('interval', 'database_name')
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

    database_name = fields.Char(string=u'Banco de dados', size=100)
    interval = fields.Selection(
        string=u"Período",
        selection=[('hora', u'1 hora'), ('seis', u'6 horas'),
                   ('doze', u'12 horas'), ('diario', u'Diário')])

    send_to_s3 = fields.Boolean(u'Enviar Amazon S3 ?')
    aws_access_key = fields.Char(string=u"Chave API S3", size=100)
    aws_secret_key = fields.Char(string=u"Chave Secreta API S3", size=100)
    aws_bucket_prefix = fields.Char(
        string="Prefixo Bucket",
        help="Usado quando o nome do bucket dá conflito com existente")
    backup_dir = fields.Char(string=u"Diretório", size=300,
                             default="/opt/backups/database/")

    next_backup = fields.Datetime(string=u"Próximo Backup")
    backup_count = fields.Integer(
        string=u"Nº Backups",
        compute='_get_total_backups')

    def _set_next_backup(self):
        last_backup = datetime.strptime(self.next_backup, '%Y-%m-%d %H:%M:%S')
        if self.interval == 'hora':
            self.next_backup = last_backup + timedelta(hours=1)
        elif self.interval == 'seis':
            self.next_backup = last_backup + timedelta(hours=6)
        elif self.interval == 'doze':
            self.next_backup = last_backup + timedelta(hours=12)
        else:
            self.next_backup = last_backup + timedelta(days=1)

    @api.multi
    def execute_backup(self):
        try:
            self.schedule_backup(True)
        except Exception:
            _logger.error(u'Erro ao efetuar backup', exc_info=True)
            raise Warning(
                u'Erro ao executar backup - Verifique o log de erros')

    @api.model
    def schedule_backup(self, manual_backup=False):
        confs = self.search([])
        for rec in confs:

            if rec.next_backup:
                next_backup = datetime.strptime(
                    rec.next_backup,
                    '%Y-%m-%d %H:%M:%S')
            else:
                next_backup = datetime.now()
            if (next_backup < datetime.now()) or manual_backup:

                if not os.path.isdir(rec.backup_dir):
                    os.makedirs(rec.backup_dir)

                zip_name = '%s_%s.zip' % (self.env.cr.dbname,
                                          time.strftime('%Y%m%d_%H_%M_%S'))
                zip_file = '%s/%s' % (rec.backup_dir, zip_name)

                with open(zip_file, 'wb') as dump_zip:
                    odoo.service.db.dump_db(
                        self.env.cr.dbname, dump_zip, 'zip')

                backup_env = self.env['backup.executed']

                if rec.send_to_s3:
                    try:
                        rec.send_for_amazon_s3(
                            zip_file, zip_name, self.env.cr.dbname)
                        backup_env.create({'backup_date': datetime.now(),
                                           'configuration_id': rec.id,
                                           'name': zip_name,
                                           'state': 'concluded'})
                    finally:
                        os.remove(zip_file)
                else:
                    backup_env.create(
                        {'backup_date': datetime.now(), 'name': zip_name,
                         'configuration_id': rec.id, 'state': 'concluded',
                         'local_path': zip_file})
                if not manual_backup:
                    rec._set_next_backup()

    def send_for_amazon_s3(self, file_to_send, name_to_store, database):
        if self.aws_access_key and self.aws_secret_key:
            access_key = self.aws_access_key
            secret_key = self.aws_secret_key

            conexao = S3Connection(access_key, secret_key)

            database = re.sub('[^a-z]', '', database or '')
            prefix = re.sub('[^a-z]', '', self.aws_bucket_prefix or '')
            bucket_name = '%s%s-bkp' % (prefix, database)
            bucket = conexao.create_bucket(bucket_name)

            k = Key(bucket)
            k.key = name_to_store
            k.set_contents_from_filename(file_to_send)
            return k.key
        else:
            raise Exception('Configure a chave de acesso e chave secreta AWS')
