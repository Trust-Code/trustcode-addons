from odoo import models


class EletronicDocument(models.Model):
    _inherit = 'eletronic.document'

    def _find_attachment_ids_email(self):
        atts = super(EletronicDocument, self)._find_attachment_ids_email()

        attachment_obj = self.env['ir.attachment']
        for transaction in self.move_id.transaction_ids:

            if transaction.boleto_pdf:
                pdf_id = attachment_obj.create(dict(
                    name="%s.pdf" % transaction.reference.replace('/', '-'),
                    datas=transaction.boleto_pdf,
                    mimetype='application/pdf',
                    res_model='account.move',
                    res_id=self.move_id.id,
                ))
                atts.append(pdf_id.id)

        return atts