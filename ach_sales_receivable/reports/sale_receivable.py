# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, timedelta
from datetime import datetime
from datetime import datetime, timedelta
import datetime
import pytz
from odoo.exceptions import UserError, ValidationError

class SaleReceivable(models.TransientModel):
    _name = 'sale.receivable'
    _description = 'Cuentas por Cobrar'

    name = fields.Char(string='Cuentas por Cobrar')
    date = fields.Date(string='Fecha final', default=lambda self: fields.date.today())
    date_start = fields.Date(string='Periodo', default=lambda self: self.env['sale.order'].search([], limit=1, order='confirmation_date asc').confirmation_date)
    journal_ids = fields.Many2many('account.journal', string="Diarios", domain=[('type','=','sale')])
    seller_id = fields.Many2one('res.users', string="Vendedor", required=True)

    def get_pdf(self):
        return self.env.ref('ach_sales_receivable.action_pdf_sale_receivable').report_action(self)

    def get_hour_tz(self, tz):
        hour = 6
        return hour

    def sale_receivable(self):
        sale_receivable = []
        journal_ids = [x.id for x in self.journal_ids] if self.journal_ids else [x.id for x in self.env['account.journal'].search([('type','=','sale')])]
        seller_id = self.seller_id.id if self.seller_id else False
        date_start = self.date_start
        date_end = self.date
        sale_receivable += self.report_data_sales(date_start, date_end, seller_id, journal_ids)
        return sale_receivable

    def report_data_sales(self, date_start, date_end, seller_id, journal_ids):
        sale_receivable = []
        sale_ids = self.env['sale.order'].search([
            ('confirmation_date','>=',date_start),('confirmation_date','<=',date_end),
            ('user_id','=',seller_id),('invoice_from_multiple_sales','=',False),
            ('total_residual','>=',1)], order='confirmation_date asc')
        for sale in sale_ids:
            sale_name = sale.name
            sale_date = sale.confirmation_date
            partner = sale.partner_invoice_id.name
            seller = sale.user_id.name
            payment_term = sale.payment_term_id.name
            sale_amount = sale.amount_total
            invoice_ids = []
            for invoice in sale.invoice_ids.filtered(lambda i: i.state in ['open','in_payment','paid'] and not i.refund_invoice_ids and i.journal_id.id in journal_ids):
                invoice_ids.append({'name':invoice.number,'amount':round(invoice.amount_total,2)})
            residual = sale.total_residual
            detail_sale_receivable = sale.detail_sale_receivable
            vals = {'sale_name':sale_name,
                    'sale_date': sale_date,
                    'partner' : partner,
                    'seller' : seller,
                    'payment_term' : payment_term,
                    'sale_amount' : sale_amount,
                    'invoice_ids': invoice_ids,
                    'residual': residual,
                    'note': detail_sale_receivable
                    }
            sale_receivable.append(vals)
        sale_ids = self.env['sale.order'].search([
            ('confirmation_date','>=',date_start),('confirmation_date','<=',date_end),
            ('user_id','=',seller_id),('invoice_from_multiple_sales','=',True),
            ('total_residual','>=',1)], order='confirmation_date asc')
        sale_exist = []
        for sale in sale_ids:
            invoice_ids = []
            for invoice in sale.invoice_ids.filtered(lambda i: i.state in ['open','in_payment','paid'] and not i.refund_invoice_ids and i.journal_id.id in journal_ids and "," in i.origin):
                if sale.name not in sale_exist:
                    sale_name = invoice.origin
                    sale_date = invoice.date_invoice
                    sale_amount = invoice.amount_total
                    seller = invoice.user_id.name
                    partner = invoice.partner_id.name
                    payment_term = invoice.payment_term_id.name
                    residual = 0
                    invoice_ids.append({'name':invoice.number,'amount':round(invoice.amount_total,2)})
                    for sale_split in invoice.origin.split(','):
                        sale_exist.append(sale_split.strip())
                        sale_ids = self.env['sale.order'].search([('name','=',sale_split.strip()),('user_id','=',seller_id)])
                        residual += sale_ids.total_residual
                    detail_sale_receivable = sale.detail_sale_receivable
                    vals = {'sale_name':sale_name,
                            'sale_date': sale_date,
                            'partner' : partner,
                            'seller' : seller,
                            'payment_term' : payment_term,
                            'sale_amount' : sale_amount,
                            'invoice_ids': invoice_ids,
                            'residual': residual,
                            'note': detail_sale_receivable
                            }
                    sale_receivable.append(vals)
        return sale_receivable

#TODO FUNCIONA BIEN SOLAMENTE QUE NO ESTA MAPENADO EL SALDO LA ACCIÖN AUTOMATIZADA DE ACH_PAYMENT, LA QUE CORRESPONDE A SALE_ORDER