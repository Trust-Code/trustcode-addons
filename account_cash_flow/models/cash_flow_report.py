# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from datetime import date
from openerp import api, fields, models


class CashFlowReport(models.TransientModel):
    _name = 'account.cash.flow'
    _description = 'Cash Flow Report'

    def _compute_final_amount(self):
        for item in self:
            balance = 0
            start_balance = 0
            receivables = 0
            payables = 0
            balance_period = 0
            for line in item.line_ids:
                balance += line.amount
                if line.liquidity:
                    start_balance += line.amount
                if line.line_type == 'receivable':
                    receivables += line.amount
                if line.line_type == 'payable':
                    payables += line.amount
                if not line.liquidity:
                    balance_period += line.amount
            balance += item.start_amount

            item.start_balance = start_balance
            item.total_payables = payables
            item.total_receivables = receivables
            item.period_balance = balance_period
            item.final_amount = balance

    ignore_outstanding = fields.Boolean(string="Ignorar Vencidos?")
    account_ids = fields.Many2many('account.account', string="Filtrar Contas")
    end_date = fields.Date(
        string="Data Final", required=True,
        default=fields.date.today()+datetime.timedelta(6*365/12))
    start_amount = fields.Float(string="Valor Inicial",
                                digits='Account')
    start_balance = fields.Float(string="Saldo Inicial",
                                 compute="_compute_final_amount",
                                 digits='Account')
    total_receivables = fields.Float(string="Total de Recebimentos",
                                     compute="_compute_final_amount",
                                     digits='Account')
    total_payables = fields.Float(string="Total de Despesas",
                                  compute="_compute_final_amount",
                                  digits='Account')
    period_balance = fields.Float(string="Saldo do Período",
                                  compute="_compute_final_amount",
                                  digits='Account')
    final_amount = fields.Float(string="Saldo Final",
                                compute="_compute_final_amount",
                                digits='Account')
    line_ids = fields.One2many(
        "account.cash.flow.line", "cashflow_id",
        string="Cash Flow Lines")

    def draw_chart(self):
        import plotly.graph_objs as go
        import pandas as pd

        diarios = []
        bancos = self.line_ids.filtered(lambda x: x.liquidity)
        for item in bancos:
            diarios.append((item.amount, item.name))

        movimentacoes = []
        for item in self.line_ids.filtered(lambda x: not x.liquidity):
            movimentacoes.append((item.amount, item.date, item.line_type))

        diarios = pd.DataFrame(diarios, columns=['total', 'name'])
        moves = pd.DataFrame(
            movimentacoes, columns=['total', 'date_maturity', 'type'])

        moves['total'] = moves["total"].astype(float)
        moves['date_maturity'] = pd.to_datetime(moves["date_maturity"])
        moves['receitas'] = moves["total"]
        moves['despesas'] = moves["total"]

        moves.loc[moves.type == 'payable', 'receitas'] = 0.0
        moves.loc[moves.type == 'receivable', 'despesas'] = 0.0
        moves = moves.sort_values(by="date_maturity")
        moves["acumulado"] = moves["total"].cumsum()
        moves["acumulado"] += diarios["total"].sum()

        saldo = []
        saldo_inicial = 0.0

        for index, row in diarios.iterrows():
            saldo.append(go.Bar(
                x=["Saldo"],
                y=[row["total"]],
                name=row["name"]
            ))
            saldo_inicial += row["total"]

        acumulado_x = pd.Series(["Saldo"])
        acumulado_y = pd.Series([saldo_inicial])

        trace3 = go.Bar(
            x=moves['date_maturity'],
            y=moves['receitas'],
            name='Receitas',
        )
        trace4 = go.Bar(
            x=moves['date_maturity'],
            y=moves['despesas'],
            name='Despesas',
        )
        moves.drop_duplicates(
            subset='date_maturity', keep='last', inplace=True)
        x = acumulado_x.append(moves["date_maturity"])
        y = acumulado_y.append(moves["acumulado"])

        trace5 = go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            name="Saldo",
            line=dict(
                shape='spline'
            ),
        )

        data = [trace3, trace4, trace5]
        layout = go.Layout(
            barmode='stack',
            xaxis=dict(
                tickformat="%d-%m-%Y"
            ),
        )
        fig = go.Figure(data=data, layout=layout)

        plot_html = fig.to_html(default_width='100%', default_height='525', validate=True)

        # plot_html, plotdivid, width, height = _plot_html(
        #     fig, {}, True, '100%', 525, False)

        return plot_html

    def calculate_liquidity(self):
        domain = [('user_type_id.type', '=', 'liquidity')]
        if self.account_ids:
            domain += [('id', 'in', self.account_ids.ids)]
        accs = self.env['account.account'].search(domain)
        liquidity_lines = []
        for acc in accs:
            self.env.cr.execute(
                "select sum(debit - credit) as val from account_move_line aml \
                inner join account_move am on aml.move_id = am.id \
                where account_id = %s and am.state = 'posted'", (acc.id, ))
            total = self.env.cr.fetchone()
            if total[0]:
                liquidity_lines.append({
                    'name': '%s - %s' % (acc.code, acc.name),
                    'cashflow_id': self.id,
                    'account_id': acc.id,
                    'debit': 0,
                    'credit': total[0],
                    'amount': total[0],
                    'liquidity': True,
                })
        return liquidity_lines

    def calculate_moves(self):
        moveline_obj = self.env['account.move.line']
        domain = [
            '|',
            ('account_id.user_type_id.type', '=', 'receivable'),
            ('account_id.user_type_id.type', '=', 'payable'),
            ('reconciled', '=', False),
            ('move_id.state', '!=', 'draft'),
            ('company_id', '=', self.env.user.company_id.id),
            ('date_maturity', '<=', self.end_date),
        ]
        if self.ignore_outstanding:
            domain += [('date_maturity', '>=', date.today())]
        moveline_ids = moveline_obj.search(domain)

        moves = []
        for move in moveline_ids:
            debit = move.amount_residual if move.amount_residual < 0 else 0.0
            credit = move.amount_residual if move.amount_residual > 0 else 0.0
            amount = credit + debit

            # Temporário: não mostra as linhas com os campos 'a receber' e
            # 'a pagar' zerados
            if not credit and not debit:
                continue

            name = "%s/%s" % (move.move_id.name, move.ref or move.name)
            moves.append({
                'name': name,
                'cashflow_id': self.id,
                'partner_id': move.partner_id.id,
                'journal_id': move.journal_id.id,
                'account_id': move.account_id.id,
                'line_type': move.account_id.internal_type,
                'date': move.date_maturity,
                'debit': debit,
                'credit': credit,
                'amount': amount,
            })
        return moves

    def action_calculate_report(self):
        self.write({'line_ids': [(5, 0, 0)]})
        balance = self.start_amount
        liquidity_lines = self.calculate_liquidity()
        move_lines = self.calculate_moves()

        move_lines.sort(key=lambda x: x['date'])

        for lines in liquidity_lines+move_lines:
            balance += lines['credit'] + lines['debit']
            lines['balance'] = balance
            self.env['account.cash.flow.line'].create(lines)


class CashFlowReportLine(models.TransientModel):
    _name = 'account.cash.flow.line'
    _description = u'Cash flow lines'

    name = fields.Char(string="Descrição", required=True)
    liquidity = fields.Boolean(strign=u"Liquidez?")
    line_type = fields.Selection(
        [('receivable', 'Recebível'), ('payable', 'Pagável')], string="Tipo")
    date = fields.Date(string="Data")
    partner_id = fields.Many2one("res.partner", string="Cliente")
    account_id = fields.Many2one("account.account", string="Conta Contábil")
    journal_id = fields.Many2one("account.journal", string="Diário")
    move_id = fields.Many2one("account.move", string="Fatura")
    debit = fields.Float(string="Débito", digits='Account')
    credit = fields.Float(string="Crédito", digits='Account')
    amount = fields.Float(string="Saldo(C-D)", digits='Account')
    balance = fields.Float(string="Saldo Acumulado", digits='Account')
    cashflow_id = fields.Many2one("account.cash.flow", string="Fluxo de Caixa")
