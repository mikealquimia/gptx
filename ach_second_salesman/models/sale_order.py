# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    second_salesman = fields.Many2one('res.users', string="Second Salesman")