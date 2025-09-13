# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    deposit_number = fields.Char(string='Número de depósito')

    @api.constrains('deposit_number')
    def _validar_deposit_number(self):
        if self.journal_id.type == 'bank' and self.deposit_number == False:
            raise ValidationError('Debe ingresar el número de depósito.')