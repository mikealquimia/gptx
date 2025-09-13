# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
from datetime import datetime
from PIL import Image
from io import BytesIO
import time
import xlwt
import base64
import io
import os
import PIL

class AsistenteMovimientosCaja(models.TransientModel):
    _name = 'movimientos_caja.asistente_movimientos_caja'

    name = fields.Char('Nombre archivo', size=32)
    diarios_id = fields.Many2many("account.journal", string="Diarios", required=True)
    fecha_movimientos = fields.Date(string="Fecha de movimientos", required=True, default=lambda self: time.strftime('%Y-%m-%d'))
    name = fields.Char('Nombre archivo', size=32)
    archivo = fields.Binary('Archivo', filters='.xls')

    @api.multi
    def print_report_excel(self):
        #output = io.BytesIO()
        user = self.env['res.users'].browse(self.env.uid)
        partner = self.env['res.partner'].browse(user.partner_id.id)

        for w in self:
            dict = {}
            dict['fecha_movimientos'] = w['fecha_movimientos']
            dict['diarios_id'] = [x.id for x in w.diarios_id]
            fecha_documento = datetime.strptime(w['fecha_movimientos'], '%Y-%m-%d')
            fecha_documento_dia = fecha_documento.strftime("%d")
            fecha_documento_diasemana = fecha_documento.strftime("%w")
            fecha_documento_mes = fecha_documento.strftime("%m")

            fecha_documento_diasemana = self.letter_name_values('weekday', int(fecha_documento_diasemana))
            fecha_documento_mes = self.letter_name_values('month', int(fecha_documento_mes))
            label_fecha_documento = fecha_documento_diasemana + ', ' + fecha_documento_mes + ' ' + \
                                    fecha_documento_dia + ' del ' + fecha_documento.strftime("%Y")

            res = self.env['report.movimientos_caja.reporte_movimientos_caja'].lineas(dict)
            lineas = res['lineas']
            lineas_credito = res['lineas_credito']
            lineas_abono = res['lineas_abono']
            totales = res['totales']
            bank_accounts = res['cuentas_bancarias']
            empresas = res['empresas']
            depositos = res['depositos']

            libro = xlwt.Workbook()
            hoja = libro.add_sheet('reporte')

            if partner.image == False:
                #img = Image.open("/media/guate2006/TI10712600F1/gtr_projects/Linux_projects/gtr_projects/odoo-11/addons/movimientos_caja/static/images/logo.jpg")
                img = Image.open("/odoo/odoo-server/addons/movimientos_caja/static/images/logo.jpg")
                pixel_data = img.load()
                if img.mode == "RGBA":
                    # If the image has an alpha channel, convert it to white
                    # Otherwise we'll get weird pixels
                    for y in list(range(img.size[1])):  # For each row ...
                        for x in list(range(img.size[0])):  # Iterate through each column ...
                            # Check if it's opaque
                            if pixel_data[x, y][3] < 255:
                                # Replace the pixel data with the colour white
                                pixel_data[x, y] = (255, 255, 255, 255)

                image_parts = img.split()
                r = image_parts[0]
                g = image_parts[1]
                b = image_parts[2]
                img = Image.merge("RGB", (r, g, b))
                fo = BytesIO()
                basewidth = 650
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(fo, format='bmp')
                hoja.insert_bitmap_data(fo.getvalue(), 1, 1)

            if partner.image:
                #partner_image = partner.image
                #image_parts = partner_image.split()
                #img = Image.open("/media/guate2006/TI10712600F1/gtr_projects/Linux_projects/gtr_projects/odoo-11/addons/movimientos_caja/static/images/logo.jpg")
                img = Image.open("/odoo/odoo-server/addons/movimientos_caja/static/images/logo.jpg")

                image_parts = img.split()
                r = image_parts[0]
                g = image_parts[1]
                b = image_parts[2]
                img = Image.merge("RGB", (r, g, b))
                pixel_data = img.load()
                if img.mode == "RGBA":
                    # If the image has an alpha channel, convert it to white
                    # Otherwise we'll get weird pixels
                    for y in list(range(img.size[1])):  # For each row ...
                        for x in list(range(img.size[0])):  # Iterate through each column ...
                            # Check if it's opaque
                            if pixel_data[x, y][3] < 255:
                                # Replace the pixel data with the colour white
                                pixel_data[x, y] = (255, 255, 255, 255)

                fo = BytesIO()
                basewidth = 650
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
                img.save(fo, format='bmp')
                hoja.insert_bitmap_data(fo.getvalue(), 1, 1)

            number_format = '"Q"###,##0.00'
            xlwt.add_palette_colour("custom_colour", 0x21)
            libro.set_colour_RGB(0x21, 200, 200, 200)
            orden_factura_name_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin; align: horiz center;')

            orden_factura_name_style_bold = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                                          left thin, right thin, top thin, bottom thin; align: horiz center; font: bold on;')
            simple_bold = xlwt.easyxf('font: bold on;')
            table_headers_style = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour; font: bold on; align: horiz center;\
                                                borders: top_color black, bottom_color black, right_color black, left_color black,\
                                                left thin, right thin, top thin, bottom thin;')

            data_row = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin')
            data_row.num_format_str = number_format

            data_row_bold = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                                          left thin, right thin, top thin, bottom thin; font: bold on;')
            data_row_bold.num_format_str = number_format

            data_row_red = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin; font: color red')
            data_row_red.num_format_str = number_format

            totals_row = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left medium, right medium, top medium, bottom medium;')
            totals_row.num_format_str = number_format

            style_total_no_currency = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                                            left medium, right medium, top medium, bottom medium;')

            total_deposit = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left medium, right medium, top medium, bottom medium; font: bold on;')
            total_deposit.num_format_str = number_format

            signature_style = xlwt.easyxf('borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left no_line, right no_line, top no_line, bottom thin; font: bold on, italic on;')

            single_simbol = xlwt.easyxf('align: horiz right;')

            deposit_style = xlwt.easyxf('align: vert top, horiz left; font: bold on;')

            style_simple_currency_data = xlwt.easyxf('align: horiz right;')
            style_simple_currency_data.num_format_str = number_format

            simple_bold_style_dollar = xlwt.easyxf('font: bold on;')
            simple_bold_style_dollar.num_format_str = '$###,##0.00'

            style_header_labels_small = xlwt.easyxf('font: bold on, height 180;')

            hoja.write(4, 0, 'Movimientos de Caja')
            hoja.write(4, 4, 'Sucursal', style=simple_bold)
            hoja.write(4, 5, empresas)
            #hoja.write(4, 8, fecha_documento.strftime("%A, %B %d, %Y"))
            hoja.write(4, 8, label_fecha_documento)
            hoja.write(5, 1, 'MOVIMIENTO DEL DIA', style=simple_bold)
            hoja.write(5, 5, 'Retención', style=simple_bold)
            hoja.write(5, 8, 'CRÉDITOS PAGADOS CAJA', style=simple_bold)
            hoja.write(5, 11, 'Retención', style=simple_bold)

            #HEADERS
            hoja.write(6, 0, 'Orden', style=table_headers_style)
            hoja.write(6, 1, 'Factura', style=table_headers_style)
            hoja.write(6, 2, 'Cliente', style=table_headers_style)
            hoja.write(6, 3, 'Venta', style=table_headers_style)
            hoja.write(6, 4, 'Abono', style=table_headers_style)
            hoja.write(6, 5, 'Saldo', style=table_headers_style)
            hoja.write(6, 6, 'Exención', style=table_headers_style)

            hoja.write(6, 8, 'Orden', style=table_headers_style)
            hoja.write(6, 9, 'Cliente', style=table_headers_style)
            hoja.write(6, 10, 'Valor', style=table_headers_style)
            hoja.write(6, 11, 'Exención', style=table_headers_style)

            hoja.col(1).width = 256 * 20
            hoja.col(2).width = 256 * 30
            hoja.col(9).width = 256 * 30

            y = 7

            #ROWS DATA
            for linea in lineas:
                row_currency_format = linea['Moneda']
                number_format = '"' + row_currency_format + '"###,##0.00'
                data_row.num_format_str = number_format
                data_row_red.num_format_str = number_format
                if linea['Venta'] < linea['Abono']:
                    hoja.write(y, 0, linea['Orden'], style=orden_factura_name_style_bold)
                    hoja.write(y, 1, linea['Factura'], style=orden_factura_name_style_bold)
                    hoja.write(y, 2, linea['Cliente'], style=data_row_bold)
                    hoja.write(y, 3, linea['Venta'], style=data_row_bold)
                    hoja.write(y, 4, linea['Abono'], style=data_row_bold)
                    hoja.write(y, 5, linea['Saldo'], style=data_row_bold)
                    hoja.write(y, 6, linea['Exencion'], style=data_row_bold)
                else:
                    hoja.write(y, 0, linea['Orden'], style=orden_factura_name_style)
                    hoja.write(y, 1, linea['Factura'], style=orden_factura_name_style)
                    hoja.write(y, 2, linea['Cliente'], style=data_row)
                    hoja.write(y, 3, linea['Venta'], style=data_row)
                    hoja.write(y, 4, linea['Abono'], style=data_row)
                    hoja.write(y, 5, linea['Saldo'], style=data_row_red)
                    hoja.write(y, 6, linea['Exencion'], style=data_row)
                y += 1

            index_left = 7

            totales_creditos = {
                'Ordenes': 0,
                'Valor': 0,
                'Exencion': 0
            }

            totals_row.num_format_str = number_format

            for linea_credito in lineas_credito:
                row_currency_format = linea_credito['Moneda']
                number_format = '"' + row_currency_format + '"###,##0.00'
                data_row.num_format_str = number_format
                hoja.write(index_left, 8, linea_credito['Orden'], style=orden_factura_name_style)
                hoja.write(index_left, 9, linea_credito['Cliente'], style=data_row)
                hoja.write(index_left, 10, linea_credito['Valor'], style=data_row)
                hoja.write(index_left, 11, linea_credito['Exencion'], style=data_row)
                totales_creditos['Ordenes'] += 1
                totales_creditos['Valor'] += linea_credito['Valor']
                totales_creditos['Exencion'] += linea_credito['Exencion']
                index_left += 1


            #Totals Creditos Pagados
            hoja.write(index_left, 8, totales_creditos['Ordenes'], style=style_total_no_currency)
            hoja.write(index_left, 9, '', style=style_total_no_currency)
            hoja.write(index_left, 10, totales_creditos['Valor'], style=totals_row)
            hoja.write(index_left, 11, totales_creditos['Exencion'], style=totals_row)

            index_left += 2
            hoja.write(index_left, 9, 'ABONOS', style=style_header_labels_small)
            hoja.write(index_left, 11, 'Retención', style=style_header_labels_small)
            index_left += 1
            hoja.write(index_left, 8, 'Orden', style=table_headers_style)
            hoja.write(index_left, 9, 'Cliente', style=table_headers_style)
            hoja.write(index_left, 10, 'Valor', style=table_headers_style)
            hoja.write(index_left, 11, 'Exención', style=table_headers_style)
            #hoja.write(y, 11, 'Caja', style=table_headers_style)

            totales_abonos = {
                'Ordenes': 0,
                'Valor': 0,
                'Exencion': 0
            }

            index_left += 1
            for linea_abono in lineas_abono:
                row_currency_format = linea_abono['Moneda']
                number_format = '"' + row_currency_format + '"###,##0.00'
                data_row.num_format_str = number_format
                hoja.write(index_left, 8, linea_abono['Orden'], style=data_row)
                hoja.write(index_left, 9, linea_abono['Cliente'], style=data_row)
                hoja.write(index_left, 10, linea_abono['Valor'], style=data_row)
                hoja.write(index_left, 11, linea_abono['Exencion'], style=data_row)
                totales_abonos['Ordenes'] += 1
                totales_abonos['Valor'] += linea_abono['Valor']
                totales_abonos['Exencion'] += linea_abono['Exencion']
                index_left += 1

            totals_row.num_format_str = number_format
            style_simple_currency_data.num_format_str = number_format
            # Totals Abonos realizados
            hoja.write(index_left, 8, totales_abonos['Ordenes'], style=style_total_no_currency)
            hoja.write(index_left, 9, '', style=style_total_no_currency)
            hoja.write(index_left, 10, totales_abonos['Valor'], style=totals_row)
            hoja.write(index_left, 11, totales_abonos['Exencion'], style=totals_row)
            #y += 10

            #Totales facturas
            y +=2
            hoja.write(y, 0, totales['num_facturas'], style=style_total_no_currency)
            hoja.write(y, 1, '', style=totals_row)
            hoja.write(y, 2, '', style=totals_row)
            hoja.write(y, 3, totales['venta'], style=totals_row)
            hoja.write(y, 4, totales['abono'], style=totals_row)
            hoja.write(y, 5, totales['saldo'], style=totals_row)
            hoja.write(y, 6, totales['exencion'], style=totals_row)

            detail_row = y +1
            summary_row = y +2

            y += 2
            hoja.write(y, 1, 'Detalle de Valores Recibidos', style=table_headers_style)
            hoja.write(y, 2, 'Efectivo', style=table_headers_style)
            hoja.write(y, 3, 'Cheques Propios', style=table_headers_style)
            hoja.write(y, 4, 'Cheques Ajenos', style=table_headers_style)
            hoja.write(y, 5, 'Dep. Directos y Transf.', style=table_headers_style)
            hoja.write(y, 6, 'Total', style=table_headers_style)
            y += 1
            hoja.write(y, 1, 'Depósito Caja', style=data_row)
            hoja.write(y, 2, totales['depositos_caja_efectivo'], style=data_row)
            hoja.write(y, 3, totales['depositos_caja_cheques_propios'], style=data_row)
            hoja.write(y, 4, totales['depositos_caja_cheques_ajenos'], style=data_row)
            hoja.write(y, 5, totales['depositos_directos_transferencias'], style=data_row)
            hoja.write(y, 6, totales['depositos_caja_total'], style=data_row)
            y += 1
            hoja.write(y, 1, 'Dólares    (Depósito)', style=simple_bold)
            hoja.write(y, 2, 0.00, style=simple_bold_style_dollar)
            hoja.write(y, 3, 'Tipo de Cambio', style=simple_bold)
            hoja.write(y, 4, 0.00, style=style_simple_currency_data)
            hoja.write(y, 5, '-', style=style_simple_currency_data)
            y += 1
            for bank_account in bank_accounts:
                hoja.write(y, 1, bank_account['Name'], style=data_row)
                hoja.write(y, 2, bank_account['Cash'], style=data_row)
                hoja.write(y, 3, bank_account['ChequesPropios'], style=data_row)
                hoja.write(y, 4, bank_account['ChequesAjenos'], style=data_row)
                hoja.write(y, 5, bank_account['DepositosTransferencias'], style=data_row)
                hoja.write(y, 6, bank_account['Cash']+bank_account['ChequesPropios']+bank_account['ChequesAjenos']+bank_account['DepositosTransferencias'], style=data_row)
                y +=1

            signature_row = y + 2

            hoja.write(signature_row, 1, 'f)', style=signature_style)
            hoja.write_merge(signature_row, signature_row, 3, 4, 'f)', style=signature_style)
            signature_row += 1
            hoja.write(signature_row, 1, 'Elaborado por:', style=simple_bold)
            hoja.write_merge(signature_row, signature_row, 3, 4, 'Verificado por:', style=simple_bold)

            Total_retenciones_exenciones = totales['exencion'] + totales_creditos['Exencion'] + totales_abonos['Exencion']

            Total_recibido = totales["venta"] + totales_creditos['Valor'] + totales_abonos['Valor'] - totales["saldo"] - Total_retenciones_exenciones - totales['depositos_directos_transferencias']
            #Total Details
            index_left += 2

            hoja.write_merge(index_left, index_left, 8, 9, 'Total Venta del día')
            hoja.write(index_left, 10, totales["venta"], style=data_row)
            index_left += 1
            hoja.write_merge(index_left, index_left, 8, 9, '(+) Créditos Pagados')
            hoja.write(index_left, 10, totales_creditos['Valor'], style=data_row)
            index_left += 1
            hoja.write_merge(index_left, index_left, 8, 9, '(+) Abonos')
            hoja.write(index_left, 10, totales_abonos['Valor'], style=data_row)
            index_left += 1
            hoja.write_merge(index_left, index_left, 8, 9, '(-) Cuentas por Cobrar')
            hoja.write(index_left, 10, totales["saldo"], style=data_row)
            index_left += 1
            hoja.write_merge(index_left, index_left, 8, 9, '(-) Retenciones y Exenciones')
            hoja.write(index_left, 10, Total_retenciones_exenciones, style=data_row)
            index_left += 1
            hoja.write_merge(index_left, index_left, 8, 9, '(-) Depositos Directos y Transferencias')
            hoja.write(index_left, 10, totales['depositos_directos_transferencias'], style=data_row)
            index_left += 1
            hoja.write_merge(index_left, index_left, 8, 9, 'TOTAL RECIBIDO')
            hoja.write(index_left, 10, Total_recibido, style=data_row)
            index_left += 2
            hoja.write(index_left, 9, 'Cantidad Depositada')
            hoja.write(index_left, 10, totales['cantidad_depositada'], style=style_simple_currency_data)
            index_left += 1
            hoja.write(index_left, 8, '(+)', style=single_simbol)
            hoja.write(index_left, 9, 'Equivalente por $. Recibidos')
            diferencia = Total_recibido - totales['cantidad_depositada']
            index_left += 1
            hoja.write(index_left, 9, 'Diferencia')
            hoja.write(index_left, 10, diferencia, style=data_row_red)
            index_left += 1
            hoja.write_merge(index_left, index_left+3, 8, 11, 'Depositos:\n ' + depositos, style=deposit_style)

            f = io.BytesIO()
            libro.save(f)
            datos = base64.b64encode(f.getvalue())

            self.write({'archivo': datos, 'name': 'movimientos_caja.xls'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'movimientos_caja.asistente_movimientos_caja',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def letter_name_values(self, type_value, int_value):
        if type_value == 'weekday':
            switcher = {
                0: "Domingo",
                1: "Lunes",
                2: "Martes",
                3: "Miércoles",
                4: "Jueves",
                5: "Viernes",
                6: "Sábado"
            }
            letter_value = switcher.get(int_value, 'Día inválido')

        if type_value == 'month':
            switcher = {
                1: "Enero",
                2: "Febrero",
                3: "Marzo",
                4: "Abril",
                5: "Mayo",
                6: "Junio",
                7: "Julio",
                8: "Agosto",
                9: "Septiembre",
                10: "Octubre",
                11: "Noviembre",
                12: "Diciembre"
            }
            letter_value = switcher.get(int_value, 'Mes inválido')
        return letter_value

    @api.model
    def _get_report_values(self, docids, data=None):
        return self.get_report_values(docids, data)

    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))


        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
        }
