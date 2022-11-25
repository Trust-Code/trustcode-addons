import io
import logging
import uuid

from odoo import _, api, models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from ofxparse import OfxParser
except ImportError:
    _logger.debug("ofxparse not found.")
    OfxParser = None


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    unique_transaction = fields.Boolean(
        string="Gerar ID Único",
        default=False,
        help="Apenas marque esta opção em caso do arquivo OFX conter \
        registros duplicados (campo FITID), alguns bancos exportam \
        o arquivo OFX com dois registros diferentes com mesmo número \
        de transação (o que não deveria). O comportamento padrão do Odoo \
        caso exista duplicados é ignorar os duplicados (mesmo FITID) \
        e se forem todos duplicados dizer que o arquivo já foi importado. \
        Se alguma dessas situações estiver ocorrendo ao importar o arquivo \
        talvez você precise marcar esta opção.",
    )

    @api.model
    def _check_ofx(self, data_file):
        if not OfxParser:
            return False
        try:
            ofx = OfxParser.parse(io.BytesIO(data_file))
        except Exception as e:
            _logger.debug(e)
            return False
        return ofx

    @api.model
    def _prepare_ofx_transaction_line(self, transaction):
        # Since ofxparse doesn't provide account numbers,
        # we cannot provide the key 'bank_account_id',
        # nor the key 'account_number'
        # If you read odoo10/addons/account_bank_statement_import/
        # account_bank_statement_import.py, it's the only 2 keys
        # we can provide to match a partner.
        payment_ref = transaction.payee
        if transaction.checknum:
            payment_ref += " " + transaction.checknum
        if transaction.memo:
            payment_ref += " : " + transaction.memo
        unique_id = transaction.id
        if self.unique_transaction:
            unique_id = str(uuid.uuid4())
        vals = {
            "date": transaction.date,
            "payment_ref": payment_ref,
            "amount": float(transaction.amount),
            "unique_import_id": unique_id,
        }
        return vals

    def _parse_file(self, data_file):
        ofx = self._check_ofx(data_file)
        if not ofx:
            return super()._parse_file(data_file)

        result = []
        try:
            for account in ofx.accounts:
                transactions = []
                total_amt = 0.00

                if not account.statement.transactions:
                    continue

                for transaction in account.statement.transactions:
                    vals = self._prepare_ofx_transaction_line(transaction)
                    if vals:
                        transactions.append(vals)
                        total_amt += vals["amount"]
                balance = float(account.statement.balance)
                vals_bank_statement = {
                    "name": account.number,
                    "transactions": transactions,
                    "balance_start": balance - total_amt,
                    "balance_end_real": balance,
                }
                result.append(
                    (
                        account.statement.currency,
                        account.number,
                        [vals_bank_statement],
                    )
                )
        except Exception as e:
            raise UserError(
                _(
                    "The following problem occurred during import. "
                    "The file might not be valid.\n\n %s"
                )
                % str(e)
            )
        return result
