import base64
import tempfile
import csv
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class BomImportWizard(models.TransientModel):
    _name = "bom.import.wizard"

    csv_file = fields.Binary(string="Arquivo CSV")
    csv_delimiter = fields.Char(
        string='Delimitador', size=3, required=True)

    has_quote_char = fields.Boolean(string=u'Possui caracter de citação?')
    ncm_quote_char = fields.Char(string=u'Caracter de Citação', size=3)

    @api.multi
    def action_import(self):
        if not self.csv_file:
            raise UserError(_('No file attached/selected!'))

        csv_file = base64.decodestring(self.csv_file)

        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(csv_file)
        temp.close()
        with open(temp.name, 'r') as csvfile:
            if not self.has_quote_char:
                ncm_lines = csv.DictReader(
                    csvfile, delimiter=str(self.csv_delimiter))
            else:
                if not self.ncm_quote_char:
                    raise UserError(_(u'Se o campo indicador de caracter de \
citação estiver marcado é necessário informá-lo!'))
                ncm_lines = csv.DictReader(
                    csvfile, delimiter=str(self.csv_delimiter),
                    quotechar=self.ncm_quote_char)
            for line in ncm_lines:
                code = line['codigo']
                ncm_tax = {
                    'federal_nacional': float(line['nacionalfederal']),
                    'federal_importado': float(line['importadosfederal']),
                    'estadual_imposto': float(line['estadual']),
                    'municipal_imposto': float(line['municipal']), }
                if len(code.zfill(4)) == 4:
                    try:
                        code = code.zfill(4)
                        code = code[:2] + '.' + code[2:]
                        service = self.env['br_account.service.type'].search(
                            [('code', '=', code)])
                        service.update(ncm_tax)
                    except Exception as e:
                        _logger.error(e.message, exc_info=True)
                elif len(code.zfill(8)) == 8:
                    code = code.zfill(8)
                    code = code[:4] + '.' + code[4:6] + '.' + code[6:]
                    try:
                        service = self.env['product.fiscal.classification'].\
                            search([('code', '=', code)])
                        service.update(ncm_tax)
                    except Exception as e:
                        _logger.error(e.message, exc_info=True)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
