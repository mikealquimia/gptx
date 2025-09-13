# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from decimal import Decimal, ROUND_HALF_UP

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    tax_withold_amount = fields.Monetary(string='Retención (-)',store=True, readonly=True, compute='_compute_amount')
    user_country_id = fields.Char(string="UserCountry", default=lambda self: self.env.user.company_id.country_id.code)

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        response = super(AccountInvoice, self)._compute_amount()

        amount_total = self.amount_total
        partner_type_taxpayer = self.partner_id.type_taxpayer
        if partner_type_taxpayer == "big" and amount_total > 100:
            
            amount_untaxed = self.amount_untaxed
            tax_amount = self.amount_tax
            tax_withold_amount = amount_total * 0.01
            new_total = amount_total - tax_withold_amount
            self.amount_total = new_total
            
            self.tax_withold_amount = tax_withold_amount

        return response
