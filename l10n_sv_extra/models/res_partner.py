# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    user_country_id = fields.Char(string="UserCountry", default=lambda self: self.env.user.company_id.country_id.code)  
    contact_dui = fields.Char(string="DUI")
    contact_nrc = fields.Char(string="NRC")
    type_taxpayer = fields.Selection([
        ('other', 'Otros'),
        ('medium', 'Mediano'),
        ('big', 'Grande')        
    ], string="Tipo de contribuyente", required=False, default='other')

