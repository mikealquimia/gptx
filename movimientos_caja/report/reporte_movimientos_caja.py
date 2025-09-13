# -*- encoding: utf-8 -*-

from odoo import api, models
import logging

_logger = logging.getLogger(__name__)

class ReporteMovimientosCaja(models.AbstractModel):
    _name = 'report.movimientos_caja.reporte_movimientos_caja'

    def lineas(self, datos):
        totales = {}
        depositos = ''

        totales['num_ordenes'] = 0
        totales['num_facturas'] = 0
        totales['venta'] = 0
        totales['abono'] =0
        totales['saldo'] = 0
        totales['exencion'] = 0
        totales['pequenio_contribuyente'] = 0
        totales['depositos_caja_efectivo'] = 0
        totales['depositos_caja_cheques_propios'] = 0
        totales['depositos_caja_cheques_ajenos'] = 0
        totales['depositos_directos_transferencias'] = 0
        totales['depositos_caja_total'] = 0
        totales['directos_trans_efectivo'] = 0
        totales['directos_trans_cheques_propios'] = 0
        totales['directos_trans_cheques_ajenos'] = 0
        totales['directos_trans_total'] = 0
        totales['cantidad_depositada'] = 0
        global movimiento_efectivo_found
        global movimiento_cheque_ajeno_found
        global movimiento_cheque_propio_found

        lineas_ordenes = []
        companies_ids = []
        companies_names = ''
        journal_ids = [x for x in datos['diarios_id']]
        journals = self.env['account.journal'].search([
            ('id', 'in', journal_ids),
        ])

        global unique_company_id
        for journal in journals:
            unique_company_id = True
            for company in companies_ids:
                if journal.company_id.id == company:
                    unique_company_id = False
            if unique_company_id == True:
                companies_ids.append(journal.company_id.id)
                companies_names += journal.company_id.name

        bank_accounts = []
        temp_bank_accounts = []

        sales_orders = self.env['sale.order'].search([
            ('company_id', 'in', companies_ids),
            ('state', '=', 'sale'),
            ('confirmation_date', '<=', datos['fecha_movimientos']),
            ('confirmation_date', '>=', datos['fecha_movimientos']),
        ])

        for orden in sales_orders:
            if orden.invoice_count == 0:
                linea = {
                    'Orden': orden.name,
                    'Factura': '',
                    'Cliente': orden.partner_id.name,
                    'Venta': orden.amount_total,
                    'Abono': 0,
                    'Saldo': orden.amount_total,
                    'Exencion': 0,
                    'Moneda': orden.currency_id.symbol
                }
                totales['num_ordenes'] += 1

                #for linea_orden in orden.order_line:
                #if len(linea_orden.tax_id) == 0:
                #linea['Exencion'] += linea_orden.price_total

                totales['venta'] += orden.amount_total
                totales['saldo'] += orden.amount_total
                totales['exencion'] += linea['Exencion']
                lineas_ordenes.append(linea)

        lineas_facturas_sin_orden = lineas_ordenes

        bank_journals = self.env['account.journal'].search([
            ('company_id', 'in', companies_ids),
            ('type', '=', 'bank'),
            ('code', 'not in', ['CHQAJ', 'CHQPR', 'DEPTR'])
        ])


        #('code', 'not in', ['CHQAJ'], ['CHQPR'])

        for bank_journal in bank_journals:
            #TODO -  Remove once the journal types are fixed
            if bank_journal.name != 'Exencion IVA' and bank_journal.name != 'Impuestos' \
                    and bank_journal.name != 'Retencion IVA' and bank_journal.name != 'Cheques Ajenos' \
                    and bank_journal.name != 'Cheques Propios':
                bank_account = {
                    'Id': bank_journal.id,
                    'Name': bank_journal.name,
                    'Cash': 0,
                    'ChequesAjenos': 0,
                    'ChequesPropios': 0,
                    'DepositosTransferencias': 0
                }
                temp_bank_accounts.append(bank_account)

        propios_ajenos_journals =self.env['account.journal'].search([
            ('company_id', 'in', companies_ids),
            ('type', '=', 'bank'),
            ('code', 'in', ['CHQAJ', 'CHQPR'])
        ])

        temp_bank_cheques_accounts = []

        for cheques_journal in propios_ajenos_journals:
            # TODO -  Remove once the journal types are fixed
            if cheques_journal.name != 'Exencion IVA' and cheques_journal.name != 'Impuestos' \
                    and cheques_journal.name != 'Retencion IVA':
                bank_account = {
                    'Id': cheques_journal.id,
                    'Name': cheques_journal.name,
                    'Cash': 0,
                    'ChequesAjenos': 0,
                    'ChequesPropios': 0,
                    'DepositosTransferencias': 0
                }
                temp_bank_cheques_accounts.append(bank_account)


        lineas_movimiento = self.env['account.bank.statement.line'].search([
            ('date', '<=', datos['fecha_movimientos']),
            ('date', '>=', datos['fecha_movimientos']),
        ])
        lineas_movimientos_bancarios = []

        for linea_movimiento in lineas_movimiento:
            linea_movimiento_bancario = {
                'Journal_id': linea_movimiento.journal_id.id,
                'Amount': linea_movimiento.amount,
                'RefName': linea_movimiento.ref
            }
            lineas_movimientos_bancarios.append(linea_movimiento_bancario)

        facturas = self.env['account.invoice'].search([
            ('state', 'in', ['open', 'paid']),
            ('journal_id', 'in', journal_ids),
            ('date_invoice', '<=', datos['fecha_movimientos']),
            ('date_invoice', '>=', datos['fecha_movimientos']),
        ], order='date_invoice, number')

        included_facturas_ids = []

        for factura_movimiento_bancario in lineas_movimientos_bancarios:
            movimiento_efectivo_found = False
            movimiento_cheque_ajeno_found = False
            movimiento_cheque_propio_found = False

            for factura in facturas:

                if movimiento_efectivo_found is False:
                    for pagos in factura.payment_ids:
                        if pagos.journal_id.type == 'cash':
                            if pagos.journal_id.code != 'EXEIV' and pagos.journal_id.code != 'RETIV':
                                if factura_movimiento_bancario['RefName'] == factura.move_name:
                                    for i, item in enumerate(temp_bank_accounts):
                                        if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                            if pagos.journal_id.code != 'EXEIV' and pagos.journal_id.code != 'RETIV':
                                                temp_bank_accounts[i]['Cash'] += factura_movimiento_bancario['Amount']
                                                #totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                                movimiento_efectivo_found = True

                if movimiento_cheque_ajeno_found is False:
                    for pagos in factura.payment_ids:
                        if pagos.journal_id.type == 'bank':

                            if factura_movimiento_bancario['RefName'] == factura.move_name:
                                for i, item in enumerate(temp_bank_accounts):
                                    if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                        if pagos.journal_id.code == 'CHQAJ':
                                            #totales['depositos_caja_cheques_ajenos'] += pagos.amount
                                            temp_bank_accounts[i]['ChequesAjenos'] += factura_movimiento_bancario['Amount']
                                            totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                            movimiento_cheque_ajeno_found = True

                if movimiento_cheque_propio_found is False:
                    for pagos in factura.payment_ids:
                        if pagos.journal_id.type == 'bank':

                            if factura_movimiento_bancario['RefName'] == factura.move_name:
                                for i, item in enumerate(temp_bank_accounts):
                                    if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                        if pagos.journal_id.code == 'CHQPR':
                                            #totales['depositos_caja_cheques_ajenos'] += pagos.amount
                                            temp_bank_accounts[i]['ChequesPropios'] += factura_movimiento_bancario['Amount']
                                            totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                            movimiento_cheque_propio_found = True

        for factura in facturas:
            cliente = factura.partner_id.name
            nit = factura.partner_id.vat
            included_facturas_ids.append(factura.id)
            extento_iva = 0

            totales['num_facturas'] += 1

            tipo_cambio = 1
            if factura.currency_id.id != factura.company_id.currency_id.id:
                total = 0
                for l in factura.move_id.line_ids:
                    if l.account_id.id == factura.account_id.id:
                        total += l.debit - l.credit
                tipo_cambio = abs(total / factura.amount_total)

            tipo = 'FACT'
            if factura.type == 'out_refund':
                if factura.amount_untaxed >= 0:
                    tipo = 'NC'
                else:
                    tipo = 'ND'

            numero = factura.move_name
            # Por si es un diario de rango de facturas
            #if factura.journal_id.facturas_por_rangos:
                #numero = factura.name

            # Por si usa factura electrónica
            if 'firma_gface' in factura.fields_get() and factura.firma_gface:
                numero = factura.name

            # Por si usa tickets
            if 'requiere_resolucion' in factura.journal_id.fields_get() and factura.journal_id.requiere_resolucion:
                numero = factura.name

            for pagos in factura.payment_ids:

                if pagos.journal_id.type == 'cash':
                    if pagos.journal_id.code == 'EXEIV' or pagos.journal_id.code == 'RETIV':
                        extento_iva = pagos.amount
                    else:
                        totales['depositos_caja_efectivo'] += pagos.amount
                        totales['cantidad_depositada'] += pagos.amount

                if pagos.journal_id.type == 'bank':

                    if pagos.journal_id.code == 'EXEIV' or pagos.journal_id.code == 'RETIV':
                        extento_iva = pagos.amount

                    if pagos.journal_id.code == 'CHQAJ':
                        totales['depositos_caja_cheques_ajenos'] += pagos.amount
                        totales['cantidad_depositada'] += pagos.amount

                    if pagos.journal_id.code == 'CHQPR':
                        totales['depositos_caja_cheques_propios'] += pagos.amount
                        totales['cantidad_depositada'] += pagos.amount

                    for chq_banks in temp_bank_cheques_accounts:
                        if chq_banks['Id'] == pagos.journal_id.id:
                            for i, item in enumerate(temp_bank_cheques_accounts):
                                if item['Id'] == pagos.journal_id.id:
                                    if pagos.deposit_number:
                                        if depositos:
                                            depositos += '/' + pagos.deposit_number
                                        else:
                                            depositos += pagos.deposit_number

                    for bank_account in temp_bank_accounts:
                        if bank_account['Id'] == pagos.journal_id.id:
                            for i, item in enumerate(temp_bank_accounts):
                                if item['Id'] == pagos.journal_id.id:
                                    #temp_bank_accounts[i]['Cash'] += factura.amount_total
                                    #totales['cantidad_depositada'] += factura.amount_total
                                    totales['depositos_directos_transferencias'] += pagos.amount
                                    temp_bank_accounts[i]['DepositosTransferencias'] += pagos.amount
                                    if pagos.deposit_number:
                                        if depositos:
                                            depositos += '/' + pagos.deposit_number
                                        else:
                                            depositos += pagos.deposit_number

            if factura.origin:
                totales['num_ordenes'] += 1

            linea = {
                'Orden': factura.origin or '',
                'Factura': factura.move_name or '',
                'Cliente': factura.partner_id.name,
                'Venta': factura.amount_total,
                'Abono': 0,
                'Saldo': factura.residual,
                'Exencion': extento_iva,
                'Moneda': factura.currency_id.symbol
            }

            for linea_factura in factura.invoice_line_ids:
                precio = (linea_factura.price_unit * (1 - (linea_factura.discount or 0.0) / 100.0)) * tipo_cambio
                if tipo == 'NC':
                    precio = precio * -1

                nombre_producto = linea_factura.product_id.name

                if nombre_producto == 'Down payment':
                    linea['Abono'] = factura.amount_total
                    linea['Venta'] = factura.amount_total + factura.residual

            if factura.amount_total != factura.residual:
                if extento_iva > 0:
                    linea['Abono'] = (factura.amount_total - factura.residual) - extento_iva
                else:
                    for pagos in factura.payment_ids:
                        if pagos.amount > factura.amount_total:
                            linea['Abono'] = pagos.amount
                        else:
                            linea['Abono'] = factura.amount_total - factura.residual

            totales['venta'] += linea['Venta']
            totales['abono'] += linea['Abono']
            totales['saldo'] += linea['Saldo']
            totales['exencion'] += linea['Exencion']

            lineas_facturas_sin_orden.append(linea)

        pagos = self.env['account.payment'].search([
            ('state', '=', 'posted'),
            ('payment_date', '<=', datos['fecha_movimientos']),
            ('payment_date', '>=', datos['fecha_movimientos']),
        ])

        facturas_creditos_ids = []
        for pago in pagos:
            for pago_facturas in pago.invoice_ids:
                facturas_creditos_ids.append(pago_facturas.id)

        facturas_creditos = self.env['account.invoice'].search([
            ('id', 'in', facturas_creditos_ids),
            ('id', 'not in', included_facturas_ids),
            ('state', 'in', ['open', 'paid']),
            ('journal_id', 'in', journal_ids),
            ('residual', '=', 0)
        ], order='date_invoice, number')

        for factura_movimiento_bancario in lineas_movimientos_bancarios:
            movimiento_efectivo_found = False
            movimiento_cheque_ajeno_found = False
            movimiento_cheque_propio_found = False

            for factura in facturas_creditos:
                if movimiento_efectivo_found is False:
                    for pagos_credito_mov in factura.payment_ids:
                        if pagos_credito_mov.journal_id.type == 'cash':
                            if pagos_credito_mov.journal_id.code != 'EXEIV' and pagos_credito_mov.journal_id.code != 'RETIV':
                                if factura_movimiento_bancario['RefName'] == factura.move_name:
                                    for i, item in enumerate(temp_bank_accounts):
                                        if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                            if pagos_credito_mov.journal_id.code != 'EXEIV' and pagos_credito_mov.journal_id.code != 'RETIV':
                                                temp_bank_accounts[i]['Cash'] += factura_movimiento_bancario['Amount']
                                                #totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                                movimiento_efectivo_found = True

                if movimiento_cheque_ajeno_found is False:
                    for pagos_credito_mov in factura.payment_ids:
                        if pagos_credito_mov.journal_id.type == 'bank':

                            if factura_movimiento_bancario['RefName'] == factura.move_name:
                                for i, item in enumerate(temp_bank_accounts):
                                    if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                        if pagos_credito_mov.journal_id.code == 'CHQAJ':
                                            #totales['depositos_caja_cheques_ajenos'] += pagos.amount
                                            temp_bank_accounts[i]['ChequesAjenos'] += factura_movimiento_bancario['Amount']
                                            totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                            movimiento_cheque_ajeno_found = True

                if movimiento_cheque_propio_found is False:
                    for pagos_credito_mov in factura.payment_ids:
                        if pagos_credito_mov.journal_id.type == 'bank':

                            if factura_movimiento_bancario['RefName'] == factura.move_name:
                                for i, item in enumerate(temp_bank_accounts):
                                    if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                        if pagos_credito_mov.journal_id.code == 'CHQPR':
                                            #totales['depositos_caja_cheques_ajenos'] += pagos.amount
                                            temp_bank_accounts[i]['ChequesPropios'] += factura_movimiento_bancario['Amount']
                                            totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                            movimiento_cheque_propio_found = True

        lineas_credito = []

        for factura_credito in facturas_creditos:
            extento_iva_creditos = 0

            #for linea_factura_credito in factura_credito.invoice_line_ids:
                #if len(linea_factura_credito.invoice_line_tax_ids) == 0:
                    #linea_credito['Exencion'] = linea_factura_credito.amount_total

            for pagos_credito in factura_credito.payment_ids:
                if pagos_credito.payment_date == datos['fecha_movimientos']:
                    linea_credito = {
                        'Orden': factura_credito.origin or factura_credito.move_name or '',
                        'Factura': factura_credito.move_name or '',
                        'Cliente': factura_credito.partner_id.name,
                        'Valor': pagos_credito.amount,
                        'Exencion': 0,
                        'Moneda': factura_credito.currency_id.symbol
                    }
                    lineas_credito.append(linea_credito)

                    if pagos_credito.journal_id.type == 'cash':
                        if pagos_credito.journal_id.code == 'EXEIV' or pagos_credito.journal_id.code == 'RETIV':
                            extento_iva_creditos = pagos_credito.amount
                        else:
                            totales['depositos_caja_efectivo'] += pagos_credito.amount
                            totales['cantidad_depositada'] += pagos_credito.amount

                    if pagos_credito.journal_id.type == 'bank':
                        if pagos_credito.journal_id.code == 'EXEIV' or pagos_credito.journal_id.code == 'RETIV':
                            extento_iva_creditos = pagos_credito.amount

                        #totales['depositos_caja_cheques_ajenos'] += factura_credito.amount_total
                        if pagos_credito.journal_id.code == 'CHQAJ':
                            totales['depositos_caja_cheques_ajenos'] += pagos_credito.amount
                            totales['cantidad_depositada'] += pagos_credito.amount

                        if pagos_credito.journal_id.code == 'CHQPR':
                            totales['depositos_caja_cheques_propios'] += pagos_credito.amount
                            totales['cantidad_depositada'] += pagos_credito.amount

                        for chq_banks in temp_bank_cheques_accounts:
                            if chq_banks['Id'] == pagos_credito.journal_id.id:
                                for i, item in enumerate(temp_bank_cheques_accounts):
                                    if item['Id'] == pagos_credito.journal_id.id:
                                        if pagos_credito.deposit_number:
                                            if depositos:
                                                depositos += '/' + pagos_credito.deposit_number
                                            else:
                                                depositos += pagos_credito.deposit_number

                        for bank_account in temp_bank_accounts:
                            if bank_account['Id'] == pagos_credito.journal_id.id:
                                for i, item in enumerate(temp_bank_accounts):
                                    if item['Id'] == pagos_credito.journal_id.id:
                                        #temp_bank_accounts[i]['Cash'] += factura_credito.amount_total
                                        #totales['cantidad_depositada'] += factura_credito.amount_total
                                        totales['depositos_directos_transferencias'] += pagos_credito.amount
                                        temp_bank_accounts[i]['DepositosTransferencias'] += pagos_credito.amount
                                        if pagos_credito.deposit_number:
                                            if depositos:
                                                depositos += '/' + pagos_credito.deposit_number
                                            else:
                                                depositos += pagos_credito.deposit_number
            linea_credito['Exencion'] = extento_iva_creditos

        # Verfica si se han realizado pagos a creditos que posean exenciones
        update_lineas_credito = []

        for linea_update_credito in lineas_credito:
            exists_id = False
            factura_id = linea_update_credito['Factura']
            for linea_update in update_lineas_credito:
                exists_id = False
                valor = linea_update_credito['Valor']
                execion_valor = linea_update_credito['Exencion']
                if linea_update['Factura'] == factura_id:
                    exists_id = True
                    indexUpdate = update_lineas_credito.index(linea_update)
                    linea_actualizada = {
                        'Orden': linea_update['Orden'],
                        'Factura': factura_id,
                        'Cliente': linea_update['Cliente'],
                        'Valor': linea_update['Valor']+valor,
                        'Exencion': linea_update['Exencion']+execion_valor,
                        'Moneda': linea_update['Moneda']
                    }
                    update_lineas_credito[indexUpdate] = linea_actualizada

            if exists_id is False:
                update_lineas_credito.append(linea_update_credito)

        lineas_credito = update_lineas_credito


        facturas_abonos_ids = []
        for pago in pagos:
            for pago_facturas in pago.invoice_ids:
                facturas_abonos_ids.append(pago_facturas.id)

        facturas_abonos = self.env['account.invoice'].search([
            ('id', 'in', facturas_abonos_ids),
            ('id', 'not in', included_facturas_ids),
            ('state', 'in', ['open', 'paid']),
            ('journal_id', 'in', journal_ids),
            ('residual', '>', 0)
        ], order='date_invoice, number')

        for factura_movimiento_bancario in lineas_movimientos_bancarios:
            movimiento_efectivo_found = False
            movimiento_cheque_ajeno_found = False
            movimiento_cheque_propio_found = False

            for factura in facturas_abonos:

                if movimiento_efectivo_found is False:
                    for pagos in factura.payment_ids:
                        if pagos.journal_id.type == 'cash':
                            if pagos.journal_id.code != 'EXEIV' and pagos.journal_id.code != 'RETIV':
                                if factura_movimiento_bancario['RefName'] == factura.move_name:
                                    for i, item in enumerate(temp_bank_accounts):
                                        if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                            if pagos.journal_id.code != 'EXEIV' and pagos.journal_id.code != 'RETIV':
                                                temp_bank_accounts[i]['Cash'] += factura_movimiento_bancario['Amount']
                                                #totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                                movimiento_efectivo_found = True

                if movimiento_cheque_ajeno_found is False:
                    for pagos in factura.payment_ids:
                        if pagos.journal_id.type == 'bank':

                            if factura_movimiento_bancario['RefName'] == factura.move_name:
                                for i, item in enumerate(temp_bank_accounts):
                                    if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                        if pagos.journal_id.code == 'CHQAJ':
                                            #totales['depositos_caja_cheques_ajenos'] += pagos.amount
                                            temp_bank_accounts[i]['ChequesAjenos'] += factura_movimiento_bancario['Amount']
                                            totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                            movimiento_cheque_ajeno_found = True

                if movimiento_cheque_propio_found is False:
                    for pagos in factura.payment_ids:
                        if pagos.journal_id.type == 'bank':

                            if factura_movimiento_bancario['RefName'] == factura.move_name:
                                for i, item in enumerate(temp_bank_accounts):
                                    if item['Id'] == factura_movimiento_bancario['Journal_id']:
                                        if pagos.journal_id.code == 'CHQPR':
                                            #totales['depositos_caja_cheques_ajenos'] += pagos.amount
                                            temp_bank_accounts[i]['ChequesPropios'] += factura_movimiento_bancario['Amount']
                                            totales['cantidad_depositada'] += factura_movimiento_bancario['Amount']
                                            movimiento_cheque_propio_found = True

        lineas_abono = []

        for factura_abono in facturas_abonos:
            extento_iva_abonos = 0

            #for linea_factura_abono in factura_abono.invoice_line_ids:
            #    if len(linea_factura_abono.invoice_line_tax_ids) == 0:
            #        linea_abono['Exencion'] = linea_factura_abono.amount_total

            for pagos_abono in factura_abono.payment_ids:
                if pagos_abono.payment_date == datos['fecha_movimientos']:

                    linea_abono = {
                        'Orden': factura_abono.origin or factura_abono.move_name or '',
                        'Factura': factura_abono.move_name or '',
                        'Cliente': factura_abono.partner_id.name,
                        'Valor': pagos_abono.amount,
                        'Exencion': 0,
                        'Moneda': factura_abono.currency_id.symbol
                    }
                    lineas_abono.append(linea_abono)

                    if pagos_abono.journal_id.type == 'cash':
                        if pagos_abono.journal_id.code == 'EXEIV' or pagos_abono.journal_id.code == 'RETIV':
                            extento_iva_abonos = pagos_abono.amount
                        else:
                            totales['depositos_caja_efectivo'] += pagos_abono.amount
                            totales['cantidad_depositada'] += pagos_abono.amount

                    if pagos_abono.journal_id.type == 'bank':
                        #totales['cheques_ajenos'] += factura_abono.amount_total
                        if pagos_abono.journal_id.code == 'EXEIV' or pagos_abono.journal_id.code == 'RETIV':
                            extento_iva_abonos = pagos_abono.amount

                        if pagos_abono.journal_id.code == 'CHQAJ':
                            totales['depositos_caja_cheques_ajenos'] += pagos_abono.amount
                            totales['cantidad_depositada'] += pagos_abono.amount

                        if pagos_abono.journal_id.code == 'CHQPR':
                            totales['depositos_caja_cheques_propios'] += pagos_abono.amount
                            totales['cantidad_depositada'] += pagos_abono.amount

                        for chq_banks in temp_bank_cheques_accounts:
                            if chq_banks['Id'] == pagos_abono.journal_id.id:
                                for i, item in enumerate(temp_bank_cheques_accounts):
                                    if item['Id'] == pagos_abono.journal_id.id:
                                        if pagos_abono.deposit_number:
                                            if depositos:
                                                depositos += '/' + pagos_abono.deposit_number
                                            else:
                                                depositos += pagos_abono.deposit_number

                        for bank_account in temp_bank_accounts:
                            if bank_account['Id'] == pagos_abono.journal_id.id:
                                for i, item in enumerate(temp_bank_accounts):
                                    if item['Id'] == pagos_abono.journal_id.id:
                                        #temp_bank_accounts[i]['Cash'] += factura_abono.amount_total
                                        temp_bank_accounts[i]['DepositosTransferencias'] += pagos_abono.amount
                                        totales['depositos_directos_transferencias'] += pagos_abono.amount
                                        if pagos_abono.deposit_number:
                                            if depositos:
                                                depositos += '/' + pagos_abono.deposit_number
                                            else:
                                                depositos += pagos_abono.deposit_number


                linea_abono['Exencion'] = extento_iva_abonos

        # Verfica si se han realizado pagos a abonos que posean exenciones
        update_lineas_abono = []

        for linea_update_abono in lineas_abono:
            exists_id = False
            factura_id = linea_update_abono['Factura']
            for linea_update in update_lineas_abono:
                exists_id = False
                valor = linea_update_abono['Valor']
                execion_valor = linea_update_abono['Exencion']
                if linea_update['Factura'] == factura_id:
                    exists_id = True
                    indexUpdate = update_lineas_abono.index(linea_update)
                    linea_actualizada = {
                        'Orden': linea_update['Orden'],
                        'Factura': factura_id,
                        'Cliente': linea_update['Cliente'],
                        'Valor': linea_update['Valor'] + valor,
                        'Exencion': linea_update['Exencion'] + execion_valor,
                        'Moneda': linea_update['Moneda']
                    }
                    update_lineas_abono[indexUpdate] = linea_actualizada

            if exists_id == False:
                update_lineas_abono.append(linea_update_abono)

        lineas_abono = update_lineas_abono

        totales['depositos_caja_total'] = totales['depositos_caja_efectivo'] + totales[
            'depositos_caja_cheques_propios'] + totales['depositos_caja_cheques_ajenos'] + totales['depositos_directos_transferencias']




        return {'lineas': lineas_facturas_sin_orden, 'totales': totales, 'cuentas_bancarias': temp_bank_accounts,
                'lineas_credito': lineas_credito, 'lineas_abono': lineas_abono, 'empresas': companies_names, 'depositos': depositos}

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        diario = self.env['account.journal'].browse(data['form']['diarios_id'][0])

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'lineas': self.lineas,
            'direccion_diario': diario.direccion and diario.direccion.street,
        }