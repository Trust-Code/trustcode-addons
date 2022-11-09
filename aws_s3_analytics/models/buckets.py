import datetime
from odoo import fields, models

try:
    import boto3
except ImportError:
    _logger.error('Cannot import Boto3', exc_info=True)


class AwsS3Buckets(models.Model):
    _name = 'aws.s3.buckets'
    _description = 'AWS S3 Analytics'
    _rec_name = 'name'

    name = fields.Char(string="Bucket", readonly=False)
    find_bucket = fields.Boolean('Bucket encontrado: ')
    bucket_risk = fields.Boolean('Bucket em risco: ')

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
                "name": name_dir,
            }

            bucket_c = self.search([("name", "=", name_dir)])
            print(name_dir)
            print(bucket_c)
            if bucket_c:
                bucket_c.write(vals)
            else:
                self.create(vals)

