# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import datetime


class PaymentCollection(models.Model):
    _name = 'payment.collection'
    _description = 'Payment Collection'
    _order = 'date'

    name = fields.Char(string="Llamada No.")
    invoice_id = fields.Many2one('account.invoice', string="Factura")
    residual = fields.Float(string="Saldo")
    date = fields.Date(string="Fecha")
    user_id = fields.Many2one('res.users', string="Usuario")
    company_id = fields.Many2one('res.company', string="Compañia")
    partner_id = fields.Many2one('res.partner', string="Contacto")
    phone = fields.Char(string="Teléfono")
    note = fields.Text(string="Nota")
    
class PaymentCollection(models.TransientModel):
    _name = 'payment.collection.invoice'
    _description = 'Payment Collection Transient'

    name = fields.Char(string="Llamada No.")
    invoice_id = fields.Many2one('account.invoice', string="Factura")
    residual = fields.Float(string="Saldo")
    date = fields.Date(string="Fecha")
    user_id = fields.Many2one('res.users', string="Usuario")
    company_id = fields.Many2one('res.company', string="Compañia")
    partner_id = fields.Many2one('res.partner', string="Contacto")
    phone = fields.Char(string="Teléfono")
    note = fields.Text(string="Nota")
    
    
    def create_call(self):
        vals = {
            'name': self.name,
            'invoice_id': self.invoice_id.id,
            'residual': self.residual,
            'date': self.date,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'phone': self.phone,
            'note': self.note,
        }
        payment_collection = self.env['payment.collection'].sudo().create(vals)
        return payment_collection

