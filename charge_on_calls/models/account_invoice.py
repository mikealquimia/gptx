# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
from datetime import datetime, timedelta, date


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    count_payment_collection = fields.Integer(compute='_compute_count_payment_collection')

    def _compute_count_payment_collection(self):
        for rec in self:
            data_collection = self.env['payment.collection'].search([('invoice_id','=',rec.id)])
            rec.count_payment_collection = len(data_collection)
    
    def action_payment_collection(self):
        return {
            'name': _('Llamada de Cobro'),
            'res_model': 'payment.collection.invoice',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.invoice',
                'active_ids': self.ids,
                'default_partner_id': self.partner_id.id,
                'default_phone': self.partner_id.phone,
                'default_user_id': self.env.user.id,
                'default_date': date.today(),
                'default_residual': self.residual,
                'default_company_id': self.env.user.company_id.id,
                'default_invoice_id': self.id,
                'default_name': 'Llamada' + str(self.name),
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        
    def action_payment_collections(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "payment.collection",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['invoice_id', '=', self.id]],
            "name": "Llamadas de Cobro",
        }
