# © 2019 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    create_in_child_companies = fields.Boolean(
        string="Create in child companies?", default=True)

    @api.model
    def create(self, values):
        account = super(AccountAccount, self).create(values)
        if not account.create_in_child_companies:
            return account
        companies = self.env['res.company'].sudo().search(
            [('id', '!=', account.company_id.id)])
        for company in companies:
            account.copy({
                'code': account.code,
                'create_in_child_companies': False,
                'company_id': company.id,
            })

        return account


class AccountMultiCompanySynchronize(models.TransientModel):
    _name = 'account.multi.company.synchronize'

    @api.model
    def _default_company(self):
        company = self.env['res.company'].sudo().search(
            [('main_company', '=', True)])
        return company and company.id

    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Concluído')], string="State",
        default='draft')
    base_company_id = fields.Many2one('res.company', default=_default_company)
    sync_item_ids = fields.One2many(
        'account.multi.company.synchronize.item',
        'synchronize_id', string="Items to Synchronize")

    @api.model
    def create(self, values):
        sync = super(AccountMultiCompanySynchronize, self).create(values)
        sync.action_reload_items_to_sync()
        return sync

    def action_reload_items_to_sync(self):
        self.sync_item_ids.unlink()
        account_ids = self.env['account.account'].search(
            [('company_id', '=', self.base_company_id.id)])
        for account in account_ids:

            self.env.cr.execute('select id from res_company where id not in \
                                (select company_id from account_account \
                                where code = %s)', (account.code, ))
            results = self.env.cr.fetchall()
            for result in results:
                self.env['account.multi.company.synchronize.item'].create({
                    'synchronize_id': self.id,
                    'company_id': result[0],
                    'account_id': account.id,
                    'account_code': account.code,
                    'account_name': account.name,
                    'create_account': True,
                })

    def action_confirm_sync(self):
        for item in self.sync_item_ids:
            item.account_id.copy({
                'code': item.account_code,
                'create_in_child_companies': False,
                'company_id': item.company_id.id,
            })

        self.write({'state': 'done'})


class AccountMultiCompanySynchronizeItem(models.TransientModel):
    _name = 'account.multi.company.synchronize.item'
    _order = 'company_id,account_code'

    synchronize_id = fields.Many2one('account.multi.company.synchronize')
    company_id = fields.Many2one('res.company', string="Company")
    account_id = fields.Many2one('account.account', string="Account")
    account_code = fields.Char(string="Code", size=20)
    account_name = fields.Char(string="Account", size=200)
    create_account = fields.Boolean(string="Create?")
