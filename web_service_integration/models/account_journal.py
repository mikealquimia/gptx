# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
#from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

class AccountJournal(models.Model):
        _inherit = "account.journal"

        is_eface = fields.Boolean('Factura Electrónica', required=False, help="Marque si este diario utilizara emisión de facturas electrónica")
        code_est = fields.Char(string="Código Establecimiento")

AccountJournal()

