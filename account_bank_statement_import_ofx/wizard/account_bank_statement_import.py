import io
import logging

from odoo import _, api, models
from odoo.exceptions import UserError

# from odoo.addons.base_iban.models.res_partner_bank import (
#     _map_iban_template,
#     validate_iban,
# )

_logger = logging.getLogger(__name__)

try:
    from ofxparse import OfxParser
except ImportError:
    _logger.debug("ofxparse not found.")
    OfxParser = None


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

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
    def _prepare_ofx_transaction_line(self, transaction, use_amount_as_identifier=False):
        # Since ofxparse doesn't provide account numbers,
        # we cannot provide the key 'bank_account_id',
        # nor the key 'account_number'
        # If you read odoo10/addons/account_bank_statement_import/
        # account_bank_statement_import.py, it's the only 2 keys
        # we can provide to match a partner.
        name = transaction.payee
        if transaction.checknum:
            name += " " + transaction.checknum
        if transaction.memo:
            name += " : " + transaction.memo
        unique_id = transaction.id
        if use_amount_as_identifier:
            unique_id = "%s-%.0d-%s" % (
                unique_id, abs(float(transaction.amount) * 100),
                transaction.date.strftime('%Y%m%d'))

        vals = {
            "date": transaction.date,
            "name": name,
            "ref": transaction.id,
            "amount": float(transaction.amount),
            "unique_import_id": unique_id,
        }
        return vals

    def _parse_file(self, data_file):
        ofx = self._check_ofx(data_file)
        if not ofx:
            return super()._parse_file(data_file)

        transactions = []
        total_amt = 0.00
        try:
            ids = [x.id for x in ofx.account.statement.transactions]
            use_amount_as_identifier = len(ids) != len(set(ids))
            for transaction in ofx.account.statement.transactions:
                vals = self._prepare_ofx_transaction_line(transaction, use_amount_as_identifier)
                if vals:
                    transactions.append(vals)
                    total_amt += vals["amount"]
        except Exception as e:
            raise UserError(
                _(
                    "The following problem occurred during import. "
                    "The file might not be valid.\n\n %s"
                )
                % e.message
            )

        balance = float(ofx.account.statement.balance)
        vals_bank_statement = {
            "name": ofx.account.number,
            "transactions": transactions,
            "balance_start": balance - total_amt,
            "balance_end_real": balance,
        }
        return ofx.account.statement.currency, ofx.account.number, [vals_bank_statement]
