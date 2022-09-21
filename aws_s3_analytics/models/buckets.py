import boto3
import datetime
from odoo import fields, models



class AwsS3Analytics(models.Model):
    _name = 'aws.s3.analytics'
    _description = 'AWS S3 Analytics'
    _rec_name = 'bucket_name'

    bucket_name = fields.Char(string="Bucket", readonly=True)
    object_line_ids = fields.One2many('object.lines', 'relation_id', string='Object Lines', readonly=True)

    def list_buckets(self):

        session = boto3.Session(
            aws_access_key_id=(self.env.company.aws_access_key_id_o),
            aws_secret_access_key=(self.env.company.aws_secret_access_key_o),
        )
        s3 = session.resource('s3')
        lista = []

        for bucket in s3.buckets.all():
            lista.append(bucket)

        self.create_bucket(lista)

    def create_bucket(self, lista):
        for i in lista:
            name_dir = i.name

            vals = {
                "bucket_name": name_dir,
            }

            self.create(vals)
            self.env.cr.commit()


class ObjectLines(models.Model):
    _name = 'object.lines'
    _description = 'Object lines'

    bucket_name_id = fields.Many2one('aws.s3.analytics', string='Bucket')
    bucket_object = fields.Char(string="Objeto")
    last_modified = fields.Datetime('Ultima modificação do Obj')
    disk_usage = fields.Float(string="Uso de disco", digits='Disk usage')
    relation_id = fields.Many2one('aws.s3.analytics', string='IDS')
