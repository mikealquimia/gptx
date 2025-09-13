# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import logging

class SaleOrder(models.Model):
    _inherit = "sale.order"

    '''@api.onchange('order_line')
    def _onchange_order_line(self):
        type_taxpayer = self.partner_id.type_taxpayer
        print('TipoContribuyente', type_taxpayer)
        order_lines = self.order_line
        print('LINEAS',order_lines)
        for order_line in order_lines:
            taxes = order_line.tax_id
            for tax in taxes:
                tax_name = tax.name
                print('Tax', tax_name)
                type_tax_use = tax.type_tax_use
                if type_tax_use == 'sale' and type_taxpayer == 'big':'''
                    

