# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_residual = fields.Monetary(string="Saldo")
    residual_manual = fields.Boolean(string="Monto de deuda manual")
    detail_sale_receivable = fields.Text(string="Observaciones de CxC")
    uncollectible_account = fields.Boolean(string="Cuenta incobrable")
    invoice_from_multiple_sales = fields.Boolean(string="Facturado con multiples ventas")

    def compute_amount_residual(self):
        #Ventas menores a cero
        self.env.cr.execute("""select so.id as sale_id
            from sale_order so 
            where so.residual_manual = false and so.amount_total <= 0""")
        for sale in self.env.cr.dictfetchall():
            self.env.cr.execute("""UPDATE sale_order SET total_residual = %s WHERE id = %s""", (0, sale['sale_id']))
        #Ventas mayor a cero
        #Ventas anuladas o cotizaciones
        self.env.cr.execute("""select so.id as sale_id
            from sale_order so 
            left join account_invoice_sale_order_rel aisor on aisor.sale_order_id = so.id 
            where so.residual_manual = false and so.amount_total > 0 and so.state not in ('done','sale')
            group by so.id
            having count(aisor) = 0""")
        for sale in self.env.cr.dictfetchall():
            self.env.cr.execute("""UPDATE sale_order SET total_residual = %s WHERE id = %s""", (0, sale['sale_id']))
        #Ventas sin facturas y activas
        self.env.cr.execute("""select so.id as sale_id, so.amount_total as amount_sale 
            from sale_order so 
            left join account_invoice_sale_order_rel aisor on aisor.sale_order_id = so.id 
            where so.residual_manual = false and so.amount_total > 0 and so.state in ('done','sale')
            group by so.id
            having count(aisor) = 0""")
        for sale in self.env.cr.dictfetchall():
            self.env.cr.execute("""UPDATE sale_order SET total_residual = %s WHERE id = %s""", ( sale['amount_sale'], sale['sale_id']))
        #Ventas con facturas
        #Facturas de una venta
        self.env.cr.execute("""SELECT 
                so.id as sale_id,
                so.amount_total as amount_total,
                STRING_AGG(distinct ai.id::text, ', ') as invoice_ids
            from 
                sale_order so 
            left JOIN 
                sale_order_line sol ON sol.order_id = so.id
            left JOIN 
                sale_order_line_invoice_rel solir ON solir.order_line_id = sol.id 
            left JOIN 
                account_invoice_line ail ON solir.invoice_line_id = ail.id
            inner JOIN 
                account_invoice ai ON ai.id = ail.invoice_id and ai.origin  NOT LIKE '%,%' and ai.state in ('paid','open')
            where so.amount_total > 0 and so.residual_manual = false 
            group by so.id, so.amount_total
            having count(solir) >= 1""")
        for sale in self.env.cr.dictfetchall():
            sql = """select 
                ai.number as invoice_id,
                CASE 
                    when ai.state = 'paid' THEN ai.amount_total
                    WHEN ai.state = 'open' THEN (ai.amount_total - ai.residual)
                    ELSE 0
                END AS total_residual
            FROM 
                account_invoice ai 
            left join sale_order so on so.id = %s 
            WHERE 
                ai.id in %s"""
            params = (sale['sale_id'], tuple(map(int, sale['invoice_ids'].split(', '))))
            self.env.cr.execute(sql, params)
            total_residual = 0
            for line in self.env.cr.dictfetchall():
                total_residual += line['total_residual']    
            self.env.cr.execute("""UPDATE sale_order SET total_residual = %s WHERE id = %s""", ( sale['amount_total'] - total_residual, sale['sale_id']))
        #Facturas de multiples ventas
        self.env.cr.execute("""select 
            ai.id,
            so.id as sale_id,
            so.amount_total as amount_sale,
            (so.amount_total / ai.amount_total) * ai.residual as total_residual,
            ai.amount_total as invoiced
            from account_invoice ai 
            inner join account_invoice_line ail on ail.invoice_id = ai.id 
            inner join sale_order_line_invoice_rel solir on solir.invoice_line_id = ail.id 
            inner join sale_order_line sol on sol.id = solir.order_line_id 
            inner join sale_order so on so.id = sol.order_id and so.residual_manual = false 
            where ai.origin LIKE '%,%' and ai.state = 'open' """)
        for sale in self.env.cr.dictfetchall():
            self.env.cr.execute("""UPDATE sale_order SET total_residual = %s, invoice_from_multiple_sales = true WHERE id = %s""", ( sale['total_residual'], sale['sale_id']))