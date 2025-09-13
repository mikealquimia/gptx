# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    authorized_credit = fields.Boolean(string='Autorización de Crédito')

    def action_confirm(self):
        if self.payment_term_id.credit_payment == True and self.authorized_credit == False:
            raise UserError('Solicite autorización de Crédito para validar esta orden de venta')
        res = super(SaleOrder, self).action_confirm()
        return res

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'
    
    credit_payment = fields.Boolean(string='Método de pago Crédito')
    