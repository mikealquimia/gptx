# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import time

_logger = logging.getLogger(__name__)
        
class PtCollectionReportCollectionReport(models.TransientModel):
    _name = "payment.collection.report"
    _description = "Payment Collection Report"
    
    user_id = fields.Many2one('res.users', string='Vendedor')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    calls = fields.One2many('payment.collection.report.line','batch', string="llamadas")
    
    @api.multi
    def print_report(self):
        self.value_valls()
        return self.env.ref('charge_on_calls.id_payment_collection_report_pdf').report_action(self)
    
    def value_valls(self):
        if self.calls:
            for cal in self.calls:
                cal.unlink()
        if not self.user_id:
            data_calls = self.env['payment.collection'].search([('date','<=',self.date_to),
                                                                ('date','>=',self.date_from),
                                                                ('company_id','=',self.company_id.id),
                                                                ], order="date asc")
        else:
            data_calls = self.env['payment.collection'].search([('date','<=',self.date_to),
                                                                ('date','>=',self.date_from),
                                                                ('user_id','=',self.user_id.id),
                                                                ('company_id','=',self.company_id.id),
                                                                ], order="date asc")
        for call in data_calls:
            vals = {
                'batch': self.id,
                'invoice_id': call.invoice_id.display_name,
                'residual': call.residual,
                'date': call.date,
                'user_id': call.user_id.name,
                'partner_id': call.partner_id.name,
                'phone': call.phone,
                'note': call.note,
            }
            line = self.env['payment.collection.report.line'].create(vals)
        return 
    
class PaymentCollectionReportLine(models.TransientModel):
    _name = "payment.collection.report.line"
    _description = "Payment Collection Report"
    
    batch = fields.Char()
    invoice_id = fields.Char()
    residual = fields.Char()
    date = fields.Char()
    user_id = fields.Char()
    partner_id = fields.Char()
    phone = fields.Char()
    note = fields.Char()