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
        print("\n\n\n\n\n START PROCESS \n\n\n\n")
        # Ventas menores o iguales a cero
        self.env.cr.execute("""
            SELECT id FROM sale_order
            WHERE residual_manual = false AND amount_total <= 0
        """)
        for sale in self.env.cr.dictfetchall():
            self.env.cr.execute("""
                UPDATE sale_order SET total_residual = 0 WHERE id = %s
            """, (sale['id'],))
        print("Ventas menores o iguales a cero: ")

        # Ventas anuladas o cotizaciones sin facturas
        self.env.cr.execute("""
            SELECT so.id as sale_id
            FROM sale_order so
            LEFT JOIN account_invoice_sale_order_rel aisor
            ON aisor.sale_order_id = so.id
            WHERE so.residual_manual = false
              AND so.amount_total > 0
              AND so.state NOT IN ('done','sale')
            GROUP BY so.id
            HAVING count(aisor) = 0
        """)
        for sale in self.env.cr.dictfetchall():
            self.env.cr.execute("""
                UPDATE sale_order SET total_residual = 0 WHERE id = %s
            """, (sale['sale_id'],))
        print("Ventas anuladas o cotizaciones sin facturas: ")

        # Ventas activas sin facturas
        self.env.cr.execute("""
            SELECT so.id as sale_id, so.amount_total as amount_sale
            FROM sale_order so
            LEFT JOIN account_invoice_sale_order_rel aisor
            ON aisor.sale_order_id = so.id
            WHERE so.residual_manual = false
              AND so.amount_total > 0
              AND so.state IN ('done','sale')
            GROUP BY so.id, so.amount_total
            HAVING count(aisor) = 0
        """)
        for sale in self.env.cr.dictfetchall():
            self.env.cr.execute("""
                UPDATE sale_order SET total_residual = %s WHERE id = %s
            """, (sale['amount_sale'], sale['sale_id']))
        print("Ventas activas sin facturas: ")

        # Ventas con facturas individuales
        self.env.cr.execute("""
            SELECT so.id as sale_id,
                   so.amount_total as amount_total,
                   STRING_AGG(DISTINCT ai.id::text, ',') as invoice_ids
            FROM sale_order so
            LEFT JOIN sale_order_line sol ON sol.order_id = so.id
            LEFT JOIN sale_order_line_invoice_rel solir ON solir.order_line_id = sol.id
            LEFT JOIN account_invoice_line ail ON solir.invoice_line_id = ail.id
            INNER JOIN account_invoice ai ON ai.id = ail.invoice_id
            WHERE so.amount_total > 0
              AND so.residual_manual = false
              AND (ai.origin IS NULL OR ai.origin NOT LIKE '%,%')
              AND ai.state IN ('paid','open')
            GROUP BY so.id, so.amount_total
            HAVING count(solir) >= 1
        """)
        for sale in self.env.cr.dictfetchall():
            invoice_ids = sale['invoice_ids']
            if not invoice_ids:
                continue
            invoice_ids_tuple = tuple(map(int, invoice_ids.split(',')))
            sql = """
                SELECT
                    CASE
                        WHEN state = 'paid' THEN amount_total
                        WHEN state = 'open' THEN (amount_total - residual_signed)
                        ELSE 0
                    END AS total_residual
                FROM account_invoice
                WHERE id IN %s
            """
            self.env.cr.execute(sql, (invoice_ids_tuple,))
            total_residual = sum(row['total_residual'] for row in self.env.cr.dictfetchall())
            self.env.cr.execute("""
                UPDATE sale_order SET total_residual = %s WHERE id = %s
            """, (sale['amount_total'] - total_residual, sale['sale_id']))
        print("Ventas con facturas individuales: ")

        # Facturas de múltiples ventas
        self.env.cr.execute("""
            SELECT
                so.id as sale_id,
                ai.id as invoice_id,
                so.amount_total as amount_sale,
                ai.amount_total as invoice_total,
                ai.residual_signed as invoice_residual
            FROM account_invoice ai
            INNER JOIN account_invoice_line ail ON ail.invoice_id = ai.id
            INNER JOIN sale_order_line_invoice_rel solir ON solir.invoice_line_id = ail.id
            INNER JOIN sale_order_line sol ON sol.id = solir.order_line_id
            INNER JOIN sale_order so ON so.id = sol.order_id AND so.residual_manual = false
            WHERE ai.origin LIKE '%,%' AND ai.state = 'open'
        """)
        for sale in self.env.cr.dictfetchall():
            total_residual = (sale['amount_sale'] / max(sale['invoice_total'], 1)) * sale['invoice_residual']
            self.env.cr.execute("""
                UPDATE sale_order
                SET total_residual = %s, invoice_from_multiple_sales = true
                WHERE id = %s
            """, (total_residual, sale['sale_id']))
        print("Facturas de múltiples ventas: ")