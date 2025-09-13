# -*- encoding: UTF-8 -*-

from odoo import api, models, fields, _
import xml.etree.cElementTree as ET
from datetime import datetime, timedelta
from datetime import date, datetime, timedelta
from lxml import etree
import datetime as dt
import dateutil.parser
from dateutil.tz import gettz
from dateutil import parser
import json
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging
import base64
import requests
from json import loads
from random import randint
import re

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def set_data_for_invoice_special(self):

        xmlns = "http://www.sat.gob.gt/dte/fel/0.2.0"
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        schemaLocation = "http://www.sat.gob.gt/dte/fel/0.2.0"
        version = "0.1"
        ns = "{xsi}"
        DTE= "dte"
        #cno = "http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0"
        cno = "http://www.sat.gob.gt/face2/ComplementoFacturaEspecial/0.1.0"
        code_est = self.journal_id.code_est if self.journal_id.code_est else "1"
        root = ET.Element("{" + xmlns + "}GTDocumento", Version="0.1", attrib={"{" + xsi + "}schemaLocation" : schemaLocation})
        doc = ET.SubElement(root, "{" + xmlns + "}SAT", ClaseDocumento="dte")
        dte = ET.SubElement(doc, "{" + xmlns + "}DTE", ID="DatosCertificados")
        dem = ET.SubElement(dte, "{" + xmlns + "}DatosEmision", ID="DatosEmision")
        #fecha_emision = dt.datetime.now(gettz("America/Guatemala")).isoformat()   #dt.datetime.now().isoformat()
        fecha_emision = dt.datetime.now(gettz("America/Guatemala")).__format__('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        dge = ET.SubElement(dem, "{" + xmlns + "}DatosGenerales", CodigoMoneda="GTQ",  FechaHoraEmision=fecha_emision, Tipo="FESP")
        emi = ET.SubElement(dem, "{" + xmlns + "}Emisor", AfiliacionIVA="GEN", CodigoEstablecimiento=code_est, CorreoEmisor=self.company_id.email, NITEmisor=self.company_id.vat, NombreComercial=self.company_id.name, NombreEmisor=self.company_id.company_registry)
        dire = ET.SubElement(emi, "{" + xmlns + "}DireccionEmisor")
        ET.SubElement(dire, "{" + xmlns + "}Direccion").text = self.company_id.street #"4 Avenida 19-26 zona 10"
        ET.SubElement(dire, "{" + xmlns + "}CodigoPostal").text = "01009"
        ET.SubElement(dire, "{" + xmlns + "}Municipio").text = self.company_id.city or "Guatemala"
        ET.SubElement(dire, "{" + xmlns + "}Departamento").text = "Guatemala"
        ET.SubElement(dire, "{" + xmlns + "}Pais").text = "GT"

        dpi_numero = False
        if self.partner_id.vat:
            vat = self.partner_id.vat
            vat = re.sub(r'\ |\?|\.|\!|\/|\;|\:|\-', '', vat)
            vat = vat.upper()
        else:
            vat = "CF"
            if self.amount_total >= 2500:
                if self.partner_id.dpi_numero:
                    vat = self.partner_id.dpi_numero
                    dpi_numero = True
                else:
                    if not self.partner_id.vat:
                        raise UserError('El contacto a facturar no tiene DPI ni NIT, para poder validar la factura debe agregar por lo menos un dato')
                
        if dpi_numero == False:
            rece = ET.SubElement(dem, "{" + xmlns + "}Receptor", CorreoReceptor=self.partner_id.email or "", IDReceptor=vat, NombreReceptor=self.partner_id.name)
        if dpi_numero == True:
            rece = ET.SubElement(dem, "{" + xmlns + "}Receptor", CorreoReceptor=self.partner_id.email or "", IDReceptor=vat, NombreReceptor=self.partner_id.name, TipoEspecial="CUI")
        
        direc = ET.SubElement(rece, "{" + xmlns + "}DireccionReceptor")
        ET.SubElement(direc, "{" + xmlns + "}Direccion").text = self.partner_id.street or "Ciudad"
        ET.SubElement(direc, "{" + xmlns + "}CodigoPostal").text = "01009"
        ET.SubElement(direc, "{" + xmlns + "}Municipio").text = "Guatemala"
        ET.SubElement(direc, "{" + xmlns + "}Departamento").text = "Guatemala"
        ET.SubElement(direc, "{" + xmlns + "}Pais").text = "GT"

        invoice_line = self.invoice_line_ids
        items = ET.SubElement(dem, "{" + xmlns + "}Items")
        tax_in_ex = 1
        cnt = 0
        #LineasFactura
        for line in invoice_line:
            cnt += 1
            p_type = 0
            BoS = "B"
            if line.product_id.type == 'service':
                p_type = 1
                BoS = "S"
            for tax in line.invoice_line_tax_ids:
                if tax.price_include:
                    tax_in_ex = 0

            # Item
            item = ET.SubElement(items, "{" + xmlns + "}Item", BienOServicio=BoS, NumeroLinea=str(cnt))
            line_price = line.quantity * line.price_unit
            line_price = round(line_price, 2)
            ET.SubElement(item, "{" + xmlns + "}Cantidad").text = str(line.quantity)
            ET.SubElement(item, "{" + xmlns + "}UnidadMedida").text = "UND"
            ET.SubElement(item, "{" + xmlns + "}Descripcion").text = line.name or " "
            ET.SubElement(item, "{" + xmlns + "}PrecioUnitario").text = str(line.price_unit)
            ET.SubElement(item, "{" + xmlns + "}Precio").text = str(line_price)
            ET.SubElement(item, "{" + xmlns + "}Descuento").text = str(round((line.discount * (line.quantity * line.price_unit))/100,2))

            if line.invoice_line_tax_ids:
               tax = "IVA"
            else:
                raise UserError(_("Las líneas de Factura deben de llevar impuesto (IVA)."))

            impuestos = ET.SubElement(item, "{" + xmlns + "}Impuestos")
            impuesto = ET.SubElement(impuestos, "{" + xmlns + "}Impuesto")
            price_tax = line.price_total - line.price_subtotal
            ET.SubElement(impuesto, "{" + xmlns + "}NombreCorto").text = tax
            ET.SubElement(impuesto, "{" + xmlns + "}CodigoUnidadGravable").text = "1"
            ET.SubElement(impuesto, "{" + xmlns + "}MontoGravable").text = str(round(line.price_subtotal,2))
            ET.SubElement(impuesto, "{" + xmlns + "}MontoImpuesto").text = str(round(price_tax,2))
            ET.SubElement(item, "{" + xmlns + "}Total").text = str(round(line.price_total,2))
        #Totales
        totales = ET.SubElement(dem, "{" + xmlns + "}Totales")
        timpuestos = ET.SubElement(totales, "{" + xmlns + "}TotalImpuestos")
        tim = ET.SubElement(timpuestos, "{" + xmlns + "}TotalImpuesto", NombreCorto="IVA", TotalMontoImpuesto=str(round(self.amount_tax,2)))
        ET.SubElement(totales, "{" + xmlns + "}GranTotal").text = str(round(self.amount_total,2))

        #Complementos
        #dte_fecha = self.date_invoice
        #dte_fecha = datetime.strptime(dte_fecha, '%Y-%m-%d %H:%M:%S')
        #racion_de_6h = timedelta(hours=6)
        #dte_fecha = dte_fecha - racion_de_6h
        #formato2 = "%Y-%m-%d"
        #dte_fecha = dte_fecha.strftime(formato2)
        complementos = ET.SubElement(dem, "{" + xmlns + "}Complementos")
        complemento = ET.SubElement(complementos, "{" + xmlns + "}Complemento", IDComplemento=str(randint(1,99999)), NombreComplemento="FacturaEspecial", URIComplemento=cno)
        retenciones = ET.SubElement(complemento, "{" + cno + "}RetencionesFacturaEspecial", Version="1")
        ET.SubElement(retenciones, "{" + cno + "}RetencionISR").text = str(round(self.retencion,2))
        ET.SubElement(retenciones, "{" + cno + "}RetencionIVA").text = str(round(self.amount_tax,2))
        ET.SubElement(retenciones, "{" + cno + "}TotalMenosRetenciones").text = str(round(self.amount_untaxed - self.retencion,2))
        #Adenda
        ade = ET.SubElement(doc, "{" + xmlns + "}Adenda")
        ET.SubElement(ade, "CAJERO").text = "1"
        ET.SubElement(ade, "VENDEDOR").text = "1"
        ET.SubElement(ade, "Subtotal").text = str(round(self.amount_untaxed,2))
        ET.SubElement(ade, "Fuente").text = self.user_id.name
        date_due = self.date_due
        date_due = datetime.strptime(date_due, '%Y-%m-%d')
        formato2 = "%d-%m-%Y"
        date_due = date_due.strftime(formato2)
        ET.SubElement(ade, "FechaVencimiento").text = date_due

        cont = ET.tostring(root, encoding="UTF-8", method='xml')
        buscar = "ns0"
        rmpl = "dte"
        cont = cont.decode('utf_8')
        cont = cont.replace(buscar, rmpl)
        cont = cont.encode('utf_8')
        dat = base64.b64encode(cont)
        return dat

    @api.multi
    def send_data_api_special(self, xml_data=None):
        api = self.env['api.data.configuration'].search([])[0]
        if not api:
            return False
        XML = xml_data
        url = api.url_firma
        ran = str(randint(1,99999))
        data_send = {'llave': api.key_firma,
                     'archivo': XML,
                     'codigo': ran,
                     'alias': api.user,
                     'es_anulacion': 'N'}

        response = requests.request("POST", url, data=data_send)
        rp = response.json()

        dt = rp["archivo"]
        url = api.url_certificado  
        payload = {
            'nit_emisor': self.company_id.vat,
            'correo_copia': self.company_id.email,
            'xml_dte': dt,
            }

        ident = str(randint(1111111,9999999))
        headers = {
            'usuario': api.user,
            'llave': api.key_certificado,
            'content-type': "application/json",
            'identificador': ident,
            }
        #print ("AQUI")
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

        #print(response.text)
        rp = response.json()
        uuid = rp["uuid"]
        serie = rp["serie"]
        numero_dte = rp["numero"]
        dte_fecha = rp["fecha"]
        cantidad_errores = rp["cantidad_errores"]
        descripcion_errores = rp["descripcion_errores"]
        #resulta_codigo = tree_res.find('ERROR').attrib['Codigo']
        #resulta_descripcion = tree_res.find('ERROR').text
        if cantidad_errores>0:
            raise UserError(_("You cannot validate an invoice\n Error No:%s\n %s."% (cantidad_errores,descripcion_errores)))
            #message = _("You cannot validate an invoice\n Error No:%s\n %s.") % (cantidad_errores,descripcion_errores)
            #self.message_post(body=message)
            #raise UserError(_("En este momento no se puede enviar la factura al servicio web.\n Favor de contactar al administrador."))
        return uuid, serie, numero_dte, dte_fecha
