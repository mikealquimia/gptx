# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime as dt
from datetime import date, datetime, timedelta

class InvoiceDateRestrict(models.Model):
    _name = 'invoice.date.restrict'
    _description = 'Invoice Date Restrict'

    name = fields.Char(string='Período')
    date_month = fields.Selection([
        ('enero','Enero'),
        ('febrero','Febrero'),
        ('marzo','Marzo'),
        ('abril','Abril'),
        ('mayo','Mayo'),
        ('junio','Junio'),
        ('julio','Julio'),
        ('agosto','Agosto'),
        ('septiembre','Septiembre'),
        ('octubre','Octubre'),
        ('noviembre','Noviembre'),
        ('diciembre','Diciembre'),
        ], string='Mes')
    date_year = fields.Integer(string='Año')
    bloqued = fields.Boolean(strin='Bloqueado')
    
    @api.model
    def create(self, vals):
        date_year = vals['date_year']
        date_month = vals['date_month']
        date_restrict = self.env['invoice.date.restrict'].search([('date_month','=',date_month),('date_year','=',date_year)])
        if date_restrict:
            raise ValidationError('Ya un Período contable con esa fecha')
        return super(InvoiceDateRestrict, self).create(vals)
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        if self.id:
            if self.type == "out_invoice":
                if self.date_invoice != False:
                    date_in =  datetime.strptime(self.date_invoice, '%Y-%m-%d')
                    if date_in.month == 1:
                        month = 'enero'
                    if date_in.month == 2:
                        month = 'febrero'
                    if date_in.month == 3:
                        month = 'marzo'
                    if date_in.month == 4:
                        month = 'abril'
                    if date_in.month == 5:
                        month = 'mayo'
                    if date_in.month == 6:
                        month = 'junio'
                    if date_in.month == 7:
                        month = 'julio'
                    if date_in.month == 8:
                        month = 'agosto'
                    if date_in.month == 9:
                        month = 'septiembre'
                    if date_in.month == 10:
                        month = 'octubre'
                    if date_in.month == 11:
                        month = 'noviembre'
                    if date_in.month == 12:
                        month = 'diciembre'
                    date_year = date_in.year
                    date_restrict = self.env['invoice.date.restrict'].search([('date_month','=',month),('date_year','=',date_year)])
                    if len(date_restrict) == 0:
                        raise ValidationError('No existe un Período contable establecido para la fecha de esta factura.')
                    else:
                        if len(date_restrict) > 1:
                            raise ValidationError('Existe más de un Período contable establecido para la fecha de esta factura, notifique esto con su administrador.')
                        else:
                            if date_restrict.bloqued == True:
                                raise ValidationError('El Período contable establecido para la fecha de esta factura esta en estado bloqueado.')
                else:
                    raise ValidationError('Debe establecer fecha de esta factura.')
            if self.type == "in_invoice":
                if self.date != False:
                    date_in =  datetime.strptime(self.date, '%Y-%m-%d')
                    if date_in.month == 1:
                        month = 'enero'
                    if date_in.month == 2:
                        month = 'febrero'
                    if date_in.month == 3:
                        month = 'marzo'
                    if date_in.month == 4:
                        month = 'abril'
                    if date_in.month == 5:
                        month = 'mayo'
                    if date_in.month == 6:
                        month = 'junio'
                    if date_in.month == 7:
                        month = 'julio'
                    if date_in.month == 8:
                        month = 'agosto'
                    if date_in.month == 9:
                        month = 'septiembre'
                    if date_in.month == 10:
                        month = 'octubre'
                    if date_in.month == 11:
                        month = 'noviembre'
                    if date_in.month == 12:
                        month = 'diciembre'
                    date_year = date_in.year
                    date_restrict = self.env['invoice.date.restrict'].search([('date_month','=',month),('date_year','=',date_year)])
                    if len(date_restrict) == 0:
                        raise ValidationError('No existe un Período contable establecido para la fecha de esta factura.')
                    else:
                        if len(date_restrict) > 1:
                            raise ValidationError('Existe más de un Período contable establecido para la fecha de esta factura, notifique esto con su administrador.')
                        else:
                            if date_restrict.bloqued == True:
                                raise ValidationError('El Período contable establecido para la fecha de esta factura esta en estado bloqueado.')
                else:
                    raise ValidationError('Debe establecer fecha de esta factura.')
        return res