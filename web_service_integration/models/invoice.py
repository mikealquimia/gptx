# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
#from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

class AccountInvoice(models.Model):
        _inherit = "account.invoice"

        uuid = fields.Char("Número de Autorización", readonly=True, states={'draft': [('readonly', False)]})
        serie = fields.Char("Serie", readonly=True, states={'draft': [('readonly', False)]})
        numero_dte = fields.Char("Número DTE", readonly=True, states={'draft': [('readonly', False)]})
        dte_fecha = fields.Datetime("Fecha Autorización", readonly=True, states={'draft': [('readonly', False)]})
        cae = fields.Text("CAE", readonly=True, states={'draft': [('readonly', False)]})
        letras = fields.Text("Total Letras", readonly=True, states={'draft': [('readonly', False)]})
        retencion = fields.Float(string="Retención", readonly=True, states={'draft': [('readonly', False)]})
        tipo_f = fields.Selection([
            ('normal', 'Factura Normal'),
            ('especial', 'Factura Especial'),
            ('cambiaria', 'Factura Cambiaria'),
            ('cambiaria_exp', 'Factura Cambiaria Exp.'),
            ], string='Tipo de Factura', default='normal', readonly=True, states={'draft': [('readonly', False)]})
        regimen_antiguo = fields.Boolean(string="Nota de crédito rebajando régimen antiguo", readonly=True, states={'draft': [('readonly', False)]}, default=False)
        nota_abono = fields.Boolean(string="Nota de Abono", readonly=True, states={'draft': [('readonly', False)]}, default=False)
        url_invoice_fel = fields.Char(string='URL')

AccountInvoice()

