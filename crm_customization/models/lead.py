from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit ='crm.lead'
   
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Já existe um registro com esse código!')
    ]

    registro_aluno = fields.Char(related='partner_id.registro_aluno', store=True)
    
    coligada_id = fields.Many2one(related='partner_id.coligada_id', store=True)
    cfo_partner_id = fields.Many2one(related='partner_id.cfo_partner_id', store=True)

    curso = fields.Char(size=150, string="Curso")
    universidade = fields.Char(size=150, string="Universidade")
    data_matricula = fields.Date(string="Data Matricula")
    periodo = fields.Selection([
        ('morning','Matutino'),
        ('afternoon','Vespertino'),
        ('evening','Noturno'),
        ('integral','Integral')], string="Período")
    semestre = fields.Integer(string="Semestre")
    situacao_curso = fields.Selection([
        ('progress','Em andamento'),
        ('braided','Trancado')], string="Situação Curso")
    situacao_estudante = fields.Selection(
        [('active','Ativo'),
        ('inactive','Inativo')], string="Situação Aluno")
    data_vencimento = fields.Date(string="Data Vencimento")
    vencido_ha = fields.Integer(string="Vencido há", compute='_compute_overdue_days')

    currency_id = fields.Many2one(related='company_id.currency_id')
    valor_original = fields.Monetary()
    bolsa_pontualidade = fields.Monetary()
    demais_bolsas = fields.Monetary()
    valor_a_cobrar = fields.Monetary()
    
    planned_revenue = fields.Monetary(compute='_compute_planned_revenue', store=True)

    @api.depends('data_vencimento')
    def _compute_overdue_days(self):
        for item in self:
            if not item.data_vencimento:
                item.vencido_ha = 0
                continue

            diferenca = datetime.now().date() - item.data_vencimento
            days = 0 if diferenca.days < 0 else diferenca.days

            item.vencido_ha = int(days)

    @api.depends('valor_a_cobrar')
    def _compute_planned_revenue(self):
        for item in self:
            item.planned_revenue = item.valor_a_cobrar
        
    def action_merge_and_create_quotation(self):
        result = None
        for item in self:
            result = item.action_new_quotation()
        return result

    def get_or_create_quotation(self):
        order = self.env['sale.order'].search([
            ('state', '=', 'draft'),
            ('partner_id', '=', self.partner_id.id,)
        ], limit=1)
        if not order:
            order = self.env['sale.order'].create({
                'opportunity_id': self.id,
                'partner_id': self.partner_id.id,
                'team_id': self.team_id.id,
                'campaign_id': self.campaign_id.id,
                'medium_id': self.medium_id.id,
                'origin': self.name,
                'source_id': self.source_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'tag_ids': self.tag_ids.ids,
            })
        return order

    def action_new_quotation(self):
        rule = self.env['negotiation.rule'].search([('vencido_ate_dias', '>', self.vencido_ha)], limit=1)
        if not rule:
            rule = self.env['negotiation.rule'].search([], limit=1, order='vencido_ate_dias desc')
            if not rule:
                raise UserError('Configure uma regra de juros para calcular o valor a ser cobrado')
           
        order = self.get_or_create_quotation()

        juros = self.valor_a_cobrar * ((rule.percentual_multa / 100 / 30) * self.vencido_ha)
        multa = self.valor_a_cobrar * (rule.percentual_multa / 100)

        self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.env['product.product'].search([], limit=1).id,  # TODO Ajustar isso depois
            'name': 'Cobrança - %s' % self.name,
            'original_amount': self.valor_a_cobrar,
            'product_uom_qty': 1,
            'product_uom': 1,
            'addition_amount': juros + multa,
            'price_unit': self.valor_a_cobrar + juros + multa,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_id': order.id,
            'res_model': 'sale.order',
            'target': 'current',
            'view_mode': 'form',
        }
