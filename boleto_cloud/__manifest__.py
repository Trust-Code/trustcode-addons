{  # pylint: disable=C8101,C8103
    'name': 'Integração Boleto Cloud',
    'version': '13.0.1.0.0',
    'category': 'account',
    'author': 'Trustcode',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'l10n_br_account',
        'l10n_br_automated_payment',
        'l10n_br_eletronic_document',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/acquirer.xml',
        'views/account_journal.xml',
        'views/res_company.xml',
        'views/payment_transaction.xml',
        'views/cnab_remessa.xml',
    ],
}