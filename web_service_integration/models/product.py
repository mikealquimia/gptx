# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    CodeGravable = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ], string='Código Unidad Gravable', store=True, readonly=False, default='1')
    CodeEscenario = fields.Selection([
        ('0', 'Afectos'),
        ('1', 'Exportaciones'),
        ('2', 'Servicios'),
        ('3', 'Ventas de Cooperativas'),
        ('4', 'Aportes y Donaciones a Asociaciones'),
        ('5', 'Pagos por el derecho de ser miembro y las cuotas periódicas'),
        ('6', 'Servicios Exentos'),
        ('7', 'Venta de Activos'),
        ('8', 'Servicios exentos centros educativos privados'),
        ('9', 'Medicamentos'),
        ('10', 'Vehículos'),
        ('11', 'Venta a Maquilas'),
        ('12', 'Ventas a zonas francas'),
        ], string='Codigo Escenario', store=True, readonly=False, default='0')


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange('CodeEscenario')
    def onchange_escenario(self):
        if int(self.CodeEscenario) > 0:
           self.CodeGravable = '2'
        else:
            self.CodeGravable = '1'
        return {}
