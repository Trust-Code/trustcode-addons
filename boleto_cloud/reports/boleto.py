import pytz
import base64
import logging
import PyPDF2
from lxml import etree
from io import BytesIO
from odoo import models

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def render_qweb_html(self, res_ids, data=None):
        if self.report_name == 'boleto_cloud.multiple_boleto':
            return

        return super(IrActionsReport, self).render_qweb_html(
            res_ids, data=data)

    def render_qweb_pdf(self, res_ids, data=None):
        if self.report_name != 'boleto_cloud.multiple_boleto':
            return super(IrActionsReport, self).render_qweb_pdf(
                res_ids, data=data)

        move_ids = self.env['account.move'].search([('id', 'in', res_ids)])

        pdf_merge = PyPDF2.PdfFileMerger()
        
        for transaction in move_ids.transaction_ids.sorted(lambda x: x.date_maturity):
            if not transaction.boleto_pdf:
                continue

            tmp_boleto = BytesIO()
            boleto = base64.b64decode(transaction.boleto_pdf)
            tmp_boleto.write(boleto)
            tmp_boleto.seek(0)

            pdf_merge.append(tmp_boleto)

        tmpDanfe = BytesIO()
        pdf_merge.write(tmpDanfe)
        pdf_merge.close()
        danfe_file = tmpDanfe.getvalue()
        tmpDanfe.close()

        return danfe_file, 'pdf'
