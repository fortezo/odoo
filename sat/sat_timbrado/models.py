# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools, release,api
from xml.dom import minidom
from qrcode import *

import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning

import os
from time import gmtime, strftime,time,sleep
import pytz, datetime
from datetime import timedelta
import tempfile
import base64
import json
import sys
import base64
import binascii
import logging

import urllib2
import urllib

from lxml import etree as ET

from M2Crypto import RSA
import hashlib

_logger = logging.getLogger(__name__)

openssl_path = ''
xsltproc_path = ''
xmlstarlet_path = ''
xslt = ''
all_paths = tools.config["addons_path"].split(",")
for my_path in all_paths:
    if os.path.isdir(os.path.join(my_path, 'cfdi_config', 'depends_app')):
        openssl_path = my_path and os.path.join(my_path, 'cfdi_config', 'depends_app', u'openssl_win') or ''
        xsltproc_path = my_path and os.path.join(my_path, 'cfdi_config', 'depends_app', u'openssl_win') or ''
        xslt = my_path and os.path.join(my_path, 'cfdi_config', 'sat', u'cadenaoriginal_3_2.xslt') or ''

def exec_command_pipe(*args):
    # Agregue esta funcion, ya que con la nueva funcion original, de tools no funciona
# TODO: Hacer separacion de argumentos, no por espacio, sino tambien por "
# ", como tipo csv, pero separator espace & delimiter "
    cmd = ' '.join(args).encode('utf-8').strip()
    
    return os.popen2(cmd, 'b')

if os.name == "nt":
    app_xsltproc = 'xsltproc.exe'
    app_openssl = 'openssl.exe'
    app_xmlstarlet = 'xmlstarlet.exe'
else:
    app_xsltproc = 'xsltproc'
    app_openssl = 'openssl'
    app_xmlstarlet = 'xmlstarlet'

app_openssl_fullpath = os.path.join(openssl_path, app_openssl)
if not os.path.isfile(app_openssl_fullpath):
    app_openssl_fullpath = tools.find_in_path(app_openssl)
    #if not os.path.isfile(app_openssl_fullpath):
        #app_openssl_fullpath = False
        #_logger.warning('Install openssl "sudo apt-get install openssl" to use l10n_mx_facturae_lib module.')

app_xsltproc_fullpath = os.path.join(xsltproc_path, app_xsltproc) or False
try:
    if not os.path.isfile(app_xsltproc_fullpath):
        app_xsltproc_fullpath = tools.find_in_path(app_xsltproc) or False
        if not os.path.isfile(app_xsltproc_fullpath):
            app_xsltproc_fullpath = False
            _logger.warning('Install xsltproc "sudo apt-get install xsltproc" to use l10n_mx_facturae_lib module.')
except Exception, e:
    _logger.warning("Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module.")

app_xmlstarlet_fullpath = os.path.join(xmlstarlet_path, app_xmlstarlet)
if not os.path.isfile( app_xmlstarlet_fullpath ):
    app_xmlstarlet_fullpath = tools.find_in_path( app_xmlstarlet )
    if not app_xmlstarlet_fullpath:
        app_xmlstarlet_fullpath = False
        _logger.warning('Install xmlstarlet "sudo apt-get install xmlstarlet" to use l10n_mx_facturae_lib module.')

def library_openssl_xsltproc_xmlstarlet(self, cr, uid, ids, context=None):
    if context is None:
        context = {}
    msj = ''
    app_openssl_fullpath = os.path.join(openssl_path, app_openssl)
    if not os.path.isfile(app_openssl_fullpath):
        app_openssl_fullpath = tools.find_in_path(app_openssl)
        if not os.path.isfile(app_openssl_fullpath):
            app_openssl_fullpath = False
            _logger.warning('Install openssl "sudo apt-get install openssl" to use l10n_mx_facturae_lib module.')
            msj += 'Install openssl "sudo apt-get install openssl" to use l10n_mx_facturae_lib module.'
    
    app_xsltproc_fullpath = os.path.join(xsltproc_path, app_xsltproc) or False
    if not os.path.isfile(app_xsltproc_fullpath):
        app_xsltproc_fullpath = tools.find_in_path(app_xsltproc) or False
        try:
            if not os.path.isfile(app_xsltproc_fullpath):
                app_xsltproc_fullpath = False
                _logger.warning("Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module.")
                msj =  "Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module."
        except Exception, e:
            _logger.warning("Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module.")
            msj +=  "Install xsltproc 'sudo apt-get install xsltproc' to use l10n_mx_facturae_lib module."

    app_xmlstarlet_fullpath = os.path.join(xmlstarlet_path, app_xmlstarlet)
    if not os.path.isfile( app_xmlstarlet_fullpath ):
        app_xmlstarlet_fullpath = tools.find_in_path( app_xmlstarlet )
        if not app_xmlstarlet_fullpath:
            app_xmlstarlet_fullpath = False
            _logger.warning('Install xmlstarlet "sudo apt-get install xmlstarlet" to use l10n_mx_facturae_lib module.')
            msj += 'Install xmlstarlet "sudo apt-get install xmlstarlet" to use l10n_mx_facturae_lib module.'
    return msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath

class res_company_get_cfdi(osv.Model):
    _name = 'acount.invoice.getcfdi'
    _auto = False
    _columns = {
        'name': fields.integer('factura',),
        'amount_total': fields.float(
            'Total',digits=dp.get_precision('Account'),
        store=True, readonly=True
        ),
    }
    def _get_certificate_str(self, fname_cer_pem=""):
        """
        @param fname_cer_pem : Path and name the file .pem
        """
        fcer = open(fname_cer_pem, "r")
        lines = fcer.readlines()
        fcer.close()
        cer_str = ""
        loading = False
        for line in lines:
            if 'END CERTIFICATE' in line:
                loading = False
            if loading:
                cer_str += line
            if 'BEGIN CERTIFICATE' in line:
                loading = True
        return cer_str

    def _cancel_cfdi(self,ids_):

        return True
    def _get_cfdi(self,ids_):
        

        print 'CFDI --------------------------------------------'
        for inv in ids_:
                #declare

            context=None
            invoice_obj = ids_.env['account.invoice']
            reseptor_obj = self.pool.get('res.partner',False)
            itimbre = ids_.env['res.company.facturae.certificate']
            certificate_lib = self.pool.get('facturae.certificate.library')
                #findata
            invoice = invoice_obj.browse(inv.id)[0]
            if invoice.type=='in_invoice':
                return ids_.write({'state': 'open'})
            if invoice.type=='in_refund':
                return ids_.write({'state': 'open'})

            
            certificado_id = itimbre.search([('company_id', '=', invoice.company_id.id)])[0]
            itimbre_fiels = itimbre.browse(certificado_id.id)[0]
                
            
                

            if itimbre_fiels.serial_number==False:
                raise except_orm(_('Error del CFDI!'), _("La Empresa no tiene Configurado los Sellos del SAT"))

            traslados = ''
            detalles = ''
            totalImpuestosTrasladados = 0
            for invoice_line in invoice.invoice_line:
                detalles += '<cfdi:Concepto cantidad="'+str(invoice_line.quantity)+'" unidad="PZ" descripcion="'+invoice_line.name.strip().replace('"','&#34;').replace(u"´",'&#180;').replace(u"Ó",'&#211;').replace(u"ó",'&#243;').replace(u'Ñ','&#209;').replace(u'Á','&#193;').replace(u'Ú','&#218;').replace(u'Í','&#205;').replace(u'É','&#201;').replace("'",'&#39;')+'" valorUnitario="'+str(invoice_line.price_unit)+'" importe="'+str(invoice_line.price_subtotal)+'" />'
            for line_tax in invoice.tax_line:
                #tax_obj = ids_.env['account.tax']
                #tax_search_id = tax_obj.search([('name', '=', str(line_tax.name))])[0]
                #print tax_search_id
                #tax_fields = tax_obj.browse(tax_search_id.id)[0]
                totalImpuestosTrasladados += line_tax.tax_amount 
                #if tax_fields.description==False:
                #    raise except_orm(_('Error del CFDI!'), _("El impuesto no tiene Codigo"))

                if (line_tax.tax_amount)==False:
                    raise except_orm(_('Error del CFDI!'), _("El importe de impuesto incorrecto"))
                if (abs(line_tax.tax_amount/line_tax.base*100))==False:
                    raise except_orm(_('Error del CFDI!'), _("El tasa de impuestos incorrecta"))


                traslados +='<cfdi:Traslado impuesto="'+line_tax.name+'" tasa="'+str("%.2f" % (abs(line_tax.tax_amount/line_tax.base*100)))+'" importe="'+str("%.2f" % (line_tax.tax_amount))+'" />'
            city = ''
            state_id = ''
            country_id = ''
            _zip = ''
            calle =''



            if invoice.company_id.partner_id.razon_social==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque la razon social de la empresa"))
            if invoice.company_id.partner_id.vat==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque el RFC de la empresa"))
            if invoice.company_id.partner_id.street==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque la calle de la empresa"))
            if invoice.company_id.partner_id.city==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque la ciudad de la empresa"))
            if invoice.company_id.partner_id.country_id.name==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque el paiz de la empresa"))
            if invoice.company_id.partner_id.state_id.name==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque el estado de la empresa"))
            if invoice.company_id.partner_id.zip==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque el codigo postal de la empresa"))
                

            #Cliente-------------------------------------------
            if invoice.partner_id.vat==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque el RFC al cliente"))
            if invoice.partner_id.razon_social==False:
                raise except_orm(_('Error del CFDI!'), _("Coloque el Nombre al cliente"))

            if invoice.partner_id.state_id.name!=False:
                state_id = 'estado="'+invoice.partner_id.state_id.name+'"'
            if invoice.partner_id.country_id.name!=False:
                country_id = 'pais="'+invoice.partner_id.country_id.name+'"'
            if invoice.partner_id.zip!=False:
                _zip = 'codigoPostal="'+invoice.partner_id.zip+'"'
            if invoice.partner_id.city!=False:
                city = 'municipio="'+invoice.partner_id.city+'"'
            if invoice.partner_id.street!=False:
                calle = 'calle="'+invoice.partner_id.street+'"'
            x = datetime.datetime.today() - timedelta(hours=6)
            #/------------------------------------------------------
            if traslados =='':
                traslados = '<cfdi:Traslado impuesto="IVA" tasa="16" importe="0" />';
            xml_string = '''<?xml version="1.0"?>
                    <cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd" version="3.2" serie="F" folio="@invoice['internal_number']" fecha="@x.isoformat()" sello="@sello" formaDePago="pago en una sola exhibicion" noCertificado="@itimbre_fiels.serial_number" certificado="@certificado" subTotal="@invoice.amount_untaxed" total="@invoice.amount_total" tipoDeComprobante="@tipoDeComprobante" metodoDePago="@metodoDePago" LugarExpedicion="@lugarexpedicion" TipoCambio="1" Moneda="@invoice.currency_id.name">
                        <cfdi:Emisor rfc="@invoice.company_id.partner_id.vat" nombre="@invoice.company_id.partner_id.name">
                            <cfdi:DomicilioFiscal calle="@invoice.company_id.partner_id.street" municipio="@invoice.company_id.partner_id.city" pais="@invoice.company_id.partner_id.country_id.name" estado="@invoice.company_id.partner_id.state_id.name" codigoPostal="@invoice.company_id.partner_id.zip" />
                            <cfdi:RegimenFiscal Regimen="@invoice.company_id.partner_id.regimen_fiscal" />
                        </cfdi:Emisor>
                        <cfdi:Receptor rfc="@invoice.partner_id.vat"  nombre="@invoice.partner_id.name">
                            <cfdi:Domicilio @calle @city @state_id @country_id @_zip/>
                        </cfdi:Receptor>
                        <cfdi:Conceptos>
                        @detalles
                        </cfdi:Conceptos>
                        <cfdi:Impuestos totalImpuestosTrasladados="@totalImpuestosTrasladados">
                            <cfdi:Traslados>
                                @traslados
                            </cfdi:Traslados>
                        </cfdi:Impuestos>
                    </cfdi:Comprobante>
                    '''
            #declaracion vacia del metodo de pago
            metodoDePago = ''
            #se saca los pagos de la factura para concatenarlos
            for pago in invoice.payment_ids:
                metodoDePago += pago.journal_id.name+','
            #se veridican los datos del metodo de pago
            if metodoDePago=='':
                xml_string = xml_string.replace('@metodoDePago','no definido')
            else:
                xml_string = xml_string.replace('@metodoDePago',metodoDePago)

            if invoice.type=='out_invoice':
                xml_string = xml_string.replace('@tipoDeComprobante','ingreso')
            if invoice.type=='out_refund':
                xml_string = xml_string.replace('@tipoDeComprobante','egreso')
                    
            xml_string = xml_string.replace('@invoice.company_id.partner_id.street', str(invoice.company_id.partner_id.street))

            xml_string = xml_string.replace('@invoice.company_id.partner_id.regimen_fiscal', str(invoice.company_id.partner_id.regimen_fiscal.name).strip())
            xml_string = xml_string.replace('@invoice.company_id.partner_id.vat', str(invoice.company_id.partner_id.vat).strip())
            xml_string = xml_string.replace('@invoice.company_id.partner_id.name', str(invoice.company_id.partner_id.razon_social).strip())
            xml_string = xml_string.replace('@invoice.company_id.partner_id.city', str(invoice.company_id.partner_id.city).strip())
            xml_string = xml_string.replace('@invoice.partner_id.vat', str(invoice.partner_id.vat).strip())
            xml_string = xml_string.replace('@invoice.partner_id.name', str(invoice.partner_id.razon_social).strip())
            xml_string = xml_string.replace('@country_id', str(country_id.encode('ascii', 'ignore')).strip())
            xml_string = xml_string.replace('@state_id', str(state_id).strip())
            xml_string = xml_string.replace('@city', str(city).strip())
            xml_string = xml_string.replace('@calle', calle.strip())
            xml_string = xml_string.replace('@_zip', str(_zip).strip())
            xml_string = xml_string.replace('@detalles', str(detalles).strip())
            xml_string = xml_string.replace('@totalImpuestosTrasladados', str(totalImpuestosTrasladados).strip())
            xml_string = xml_string.replace('@traslados', str(traslados).strip())
            xml_string = xml_string.replace('@invoice.company_id.partner_id.country_id.name', str(invoice.company_id.partner_id.country_id.name.encode('ascii', 'ignore')).strip())
            xml_string = xml_string.replace('@invoice.company_id.partner_id.state_id.name', str(invoice.company_id.partner_id.state_id.name).strip())
            xml_string = xml_string.replace('@invoice.company_id.partner_id.zip', str(invoice.company_id.partner_id.zip).strip())
            xml_string = xml_string.replace("@invoice['internal_number']", str(invoice['internal_number']).strip())
            xml_string = xml_string.replace('@x.isoformat()', str(x.isoformat()).strip())
            xml_string = xml_string.replace('@itimbre_fiels.serial_number', str(itimbre_fiels.serial_number).strip())
            xml_string = xml_string.replace('@invoice.amount_untaxed', str(invoice.amount_untaxed).strip())
            xml_string = xml_string.replace('@invoice.amount_total', str(invoice.amount_total).strip())
            xml_string = xml_string.replace('@lugarexpedicion', str(invoice.company_id.partner_id.city).strip()+' '+str(invoice.company_id.partner_id.country_id.name.encode('ascii', 'ignore')).strip()+' '+str(invoice.company_id.partner_id.state_id.name)+' '+str(invoice.company_id.partner_id.zip))
            xml_string = xml_string.replace('@invoice.currency_id.name', str(invoice.currency_id.name).strip())

            
            xdoc = ET.fromstring(xml_string)
            xsl_root = ET.parse(xslt)
            xsl = ET.XSLT(xsl_root)
            cadena_original = xsl(xdoc)


            fname_key_pem = certificate_lib.binary2file(False, False, False,itimbre_fiels.certificate_key_file_pem, 'ccopenerp_' + (itimbre_fiels.serial_number or '') + '__certificate__','.key.pem')
            fname_pem = certificate_lib.binary2file(False, False, False,itimbre_fiels.certificate_file_pem, 'ccopenerp_' + (itimbre_fiels.serial_number or '') + '__certificate__','.pem')

            keys = RSA.load_key(fname_key_pem)
            cert = self._get_certificate_str(fname_pem)
            digest = hashlib.new('sha1', str(cadena_original)).digest()
            sello = base64.b64encode(keys.sign(digest, "sha1"))



            xml_string = xml_string.replace('@sello', sello.strip())
            xml_string = xml_string.replace('@certificado', cert.strip())

            print 'cer:'+xml_string
            print '------------------------------------'
            #coneccion con itimbre
            #params       = {'user':itimbre_fiels.itimbre_usuario, 'pass':itimbre_fiels.itimbre_id, 'RFC':invoice.company_id.partner_id.vat, 'xmldata':xml_string};
            #request      = {'id':inv.id,'method':'cfd2cfdi', 'params':params};
            post_data    = {'type':'CFDI_TIMBRE','data':xml_string,'uid':itimbre_fiels.itimbre_usuario,'ref':inv.id};
            #data_to_send = json.dumps(request)
            #post_data    = {'q':data_to_send};
                
            data = urllib.urlencode(post_data)
            req = urllib2.Request("http://timbres_service.fortezo.com.mx", data)
            response = urllib2.urlopen(req)
                
                
            result = json.loads(response.read())

            if(result['cfdi']['xml']):
                xml_r = str(result['cfdi']['xml'])
                xdoc_2 = ET.fromstring(xml_r)

                for elem in xdoc_2.xpath('//t:TimbreFiscalDigital',namespaces={'t':'http://www.sat.gob.mx/TimbreFiscalDigital'}):
                    qrstr = "?re="+invoice.partner_id.vat+"&rr="+invoice.company_id.partner_id.vat+"&tt="+str(invoice.amount_total)+"&id="+elem.attrib.get('UUID')+"" ## Cadena de Texto
                    data = '' 
                    try:
                        qr = QRCode(version=1, error_correction=ERROR_CORRECT_L)
                        qr.add_data(qrstr)
                        qr.make() ## Generar el codigo QR
                        im = qr.make_image()
                        fname=tempfile.NamedTemporaryFile(suffix='.png',delete=False)
                        im.save(fname.name)
                        f = open(fname.name, "r")
                        data = f.read()
                        f.close()
                    except:
                        raise except_orm(_('Error del CFDI!'), _('Error al generar el codigo QR'))
                    return ids_.write({
                            'cfdi_qr':base64.encodestring(data),
                            'cfdi_xml':base64.encodestring(xml_r),
                            'cfdi_SelloSAT':elem.attrib.get('selloSAT'),
                            'cfdi_SelloCFDI':elem.attrib.get('selloCFD'),
                            'cfdi_NumSerieCerSAT':elem.attrib.get('noCertificadoSAT'),
                            'cfdi_SerieFolioFiscal':elem.attrib.get('UUID'),
                            'cfdi_NumSerieCer':itimbre_fiels.serial_number,
                            'cfdi_CadenaOri':str(cadena_original),
                            'state': 'open',
                            'cfdi_Fecha':x.isoformat()})

            raise except_orm(_('Error del CFDI!'), _(result['cfdi']['error']))
        return True
        
    def validar(self, cr, uid, ids, context=None):
        print 'CFDI --------------------------------------------'
        invoice_obj = self.pool.get('account.invoice',False)
        reseptor_obj = self.pool.get('res.partner',False)
        itimbre = self.pool.get('res.company.facturae.certificate')
        certificate_lib = self.pool.get('facturae.certificate.library')

        fiels = self.browse(cr, uid, ids, context=context)[0]
        invoice = invoice_obj.browse(cr, uid, fiels.name, context=context)[0]
        reseptor = reseptor_obj.browse(cr, uid, invoice.partner_id.id, context=context)[0]
        certificado_id = itimbre.search(cr, uid, [('company_id', '=', invoice.company_id.id)],context = context)[0]
        #self.search(cr, uid, [('company_id', '=', invoice.company_id)
        itimbre_fiels = itimbre.browse(cr, uid, certificado_id, context=context)[0]
        
        
        traslados = ''
        detalles = ''
        totalImpuestosTrasladados = 0.0
        for invoice_line in invoice.invoice_line:
            detalles += '<cfdi:Concepto cantidad="'+str(invoice_line.quantity)+'" unidad="PZ" descripcion="'+invoice_line.name.strip().replace('"','&#34;').replace(u"´",'&#180;').replace(u"Ó",'&#211;').replace(u"ó",'&#243;').replace(u'Ñ','&#209;').replace(u'Á','&#193;').replace(u'Ú','&#218;').replace(u'Í','&#205;').replace(u'É','&#201;').replace("'",'&#39;')+'" valorUnitario="'+str(invoice_line.price_unit)+'" importe="'+str(invoice_line.price_subtotal)+'" />'
        
        for line_tax in invoice.tax_line:
            tax_obj = self.pool.get('account.tax',False)
            tax_search_id = tax_obj.search(cr, uid, [('name', '=', line_tax.name)],context = context)[0]
            tax_fields = tax_obj.browse(cr, uid, tax_search_id, context=context)[0]
            totalImpuestosTrasladados += line_tax.tax_amount 
            traslados +='<cfdi:Traslado impuesto="'+tax_fields.description+'" tasa="'+str("%.2f" % (abs(line_tax.tax_amount/line_tax.base*100)))+'" importe="'+str("%.2f" % (line_tax.tax_amount))+'" />'
        #print itimbre_fiels.itimbre_usuario

        city = ''
        state_id = ''
        country_id = ''
        _zip = ''

        if invoice.partner_id.state_id.name!=False:
            state_id = 'estado="'+invoice.partner_id.state_id.name+'"'
        if invoice.partner_id.country_id.name!=False:
            country_id = 'pais="'+invoice.partner_id.country_id.name+'"'
        if invoice.partner_id.zip!=False:
            _zip = 'codigoPostal="'+invoice.partner_id.zip+'"'
        if invoice.partner_id.city!=False:
            city = 'municipio="'+invoice.partner_id.city+'"'
        if invoice.partner_id.street!=False:
            calle = 'calle="'+invoice.partner_id.street+'"'


        x = datetime.datetime.today() - timedelta(hours=6)
        _time = strftime("%H:%M:%S")
        xml_string = '''<?xml version="1.0"?>
            <cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd" version="3.2" serie="F" folio="@invoice['internal_number']" fecha="@x.isoformat()" sello="@sello" formaDePago="efectibo" noCertificado="@itimbre_fiels.serial_number" certificado="@certificado" subTotal="@invoice.amount_untaxed" total="@invoice.amount_total" tipoDeComprobante="ingreso" metodoDePago="no identificado" LugarExpedicion="@lugarexpedicion" TipoCambio="1" Moneda="@invoice.currency_id.name">
                <cfdi:Emisor rfc="@invoice.company_id.partner_id.vat" nombre="@invoice.company_id.partner_id.name">
                    <cfdi:DomicilioFiscal calle="@invoice.company_id.partner_id.street" municipio="@invoice.company_id.partner_id.city" pais="@invoice.company_id.partner_id.country_id.name" estado="@invoice.company_id.partner_id.state_id.name" codigoPostal="@invoice.company_id.partner_id.zip" />
                    <cfdi:RegimenFiscal Regimen="moral" />
                </cfdi:Emisor>
                <cfdi:Receptor rfc="@invoice.partner_id.vat" nombre="@invoice.partner_id.name">
                    <cfdi:Domicilio @calle @city @state_id @country_id @_zip/>
                </cfdi:Receptor>
                <cfdi:Conceptos>
                @detalles
                </cfdi:Conceptos>
                <cfdi:Impuestos totalImpuestosTrasladados="@totalImpuestosTrasladados">
                    <cfdi:Traslados>
                        @traslados
                    </cfdi:Traslados>
                </cfdi:Impuestos>
            </cfdi:Comprobante>
            '''
        
         
        xml_string = xml_string.replace('@calle', calle)
        xml_string = xml_string.replace('@invoice.company_id.partner_id.street', str(invoice.company_id.partner_id.street))
        xml_string = xml_string.replace('@invoice.company_id.partner_id.vat', str(invoice.company_id.partner_id.vat))
        xml_string = xml_string.replace('@invoice.company_id.partner_id.name', str(invoice.company_id.partner_id.name))
        xml_string = xml_string.replace('@invoice.company_id.partner_id.city', str(invoice.company_id.partner_id.city))
        xml_string = xml_string.replace('@invoice.partner_id.vat', str(invoice.partner_id.vat))
        xml_string = xml_string.replace('@invoice.partner_id.name', str(invoice.partner_id.name))
        xml_string = xml_string.replace('@country_id', str(country_id.encode('ascii', 'ignore')))
        xml_string = xml_string.replace('@state_id', str(state_id))
        xml_string = xml_string.replace('@city', str(city))
        xml_string = xml_string.replace('@_zip', str(_zip))
        xml_string = xml_string.replace('@detalles', str(detalles))
        xml_string = xml_string.replace('@totalImpuestosTrasladados', str(totalImpuestosTrasladados))
        xml_string = xml_string.replace('@traslados', str(traslados))
        xml_string = xml_string.replace('@invoice.company_id.partner_id.country_id.name', str(invoice.company_id.partner_id.country_id.name.encode('ascii', 'ignore')))
        xml_string = xml_string.replace('@invoice.company_id.partner_id.state_id.name', str(invoice.company_id.partner_id.state_id.name))
        xml_string = xml_string.replace('@invoice.company_id.partner_id.zip', str(invoice.company_id.partner_id.zip))
        xml_string = xml_string.replace("@invoice['internal_number']", str(invoice['internal_number']))
        xml_string = xml_string.replace('@x.isoformat()', str(x.isoformat()))
        xml_string = xml_string.replace('@itimbre_fiels.serial_number', str(itimbre_fiels.serial_number))
        xml_string = xml_string.replace('@invoice.amount_untaxed', str(invoice.amount_untaxed))
        xml_string = xml_string.replace('@invoice.amount_total', str(invoice.amount_total))
        xml_string = xml_string.replace('@lugarexpedicion', str(invoice.company_id.partner_id.city)+' '+str(invoice.company_id.partner_id.country_id.name.encode('ascii', 'ignore'))+' '+str(invoice.company_id.partner_id.state_id.name)+' '+str(invoice.company_id.partner_id.zip))
        xml_string = xml_string.replace('@invoice.currency_id.name', str(invoice.currency_id.name))

        print xml_string
        xdoc = ET.fromstring(xml_string)
        xsl_root = ET.parse(xslt)
        xsl = ET.XSLT(xsl_root)
        cadena_original = xsl(xdoc)


        fname_key_pem = certificate_lib.binary2file(cr, uid, ids,
                        itimbre_fiels.certificate_key_file_pem, 'ccopenerp_' + (
                        itimbre_fiels.serial_number or '') + '__certificate__',
                        '.key.pem')
        fname_pem = certificate_lib.binary2file(cr, uid, ids,
                        itimbre_fiels.certificate_file_pem, 'ccopenerp_' + (
                        itimbre_fiels.serial_number or '') + '__certificate__',
                        '.pem')

        keys = RSA.load_key(fname_key_pem)
        cert = self._get_certificate_str(fname_pem)
        digest = hashlib.new('sha1', str(cadena_original)).digest()
        sello = base64.b64encode(keys.sign(digest, "sha1"))



        xml_string = xml_string.replace('@sello', sello)
        xml_string = xml_string.replace('@certificado', cert)

        #print 'cer:'+xml_string
        print '------------------------------------'
        #coneccion con itimbre
        params       = {'user':itimbre_fiels.itimbre_usuario, 'pass':itimbre_fiels.itimbre_id, 'RFC':invoice.company_id.partner_id.vat, 'xmldata':xml_string};
        request      = {'id':fiels.name, 'method':'cfd2cfdi', 'params':params};
        
        data_to_send = json.dumps(request)
        post_data    = {'q':data_to_send};
        
        data = urllib.urlencode(post_data)
        req = urllib2.Request("https://portalws.itimbre.com/itimbre.php", data)
        response = urllib2.urlopen(req)
        
        
        result = json.loads(response.read())

        if(result['result']['retcode']==1):
            xml_r = str(result['result']['data'])
            xdoc_2 = ET.fromstring(xml_r)

            for elem in xdoc_2.xpath('//t:TimbreFiscalDigital',namespaces={'t':'http://www.sat.gob.mx/TimbreFiscalDigital'}):
                return invoice_obj.write(cr, uid, fiels.name, {
                    'cfdi_SelloSAT':elem.attrib.get('selloSAT'),
                    'cfdi_SelloCFDI':elem.attrib.get('selloCFD'),
                    'cfdi_NumSerieCerSAT':elem.attrib.get('noCertificadoSAT'),
                    'cfdi_SerieFolioFiscal':result['result']['UUID'],
                    'cfdi_NumSerieCer':itimbre_fiels.serial_number,
                    'cfdi_CadenaOri':str(cadena_original),
                    'state': 'open',
                    'cfdi_Fecha':x.isoformat()}, context=context)

        raise except_orm(_('Error del CFDI!'), _(result['result']['error']))
        
        
        #print json.dumps(post_data)
        

    def default_get(self, cr, uid, fields, context=None):
        invoice_obj = self.pool.get('account.invoice')
        fiels = invoice_obj.browse(cr, uid, context.get('active_id'), context=context)[0]

        return {'name':context.get('active_id'),'amount_total':fiels.amount_total}
        
        

class res_company_facturae_certificate(osv.Model):
    _name = 'res.company.facturae.certificate'

    _rec_name = 'serial_number'

    _columns = {
        'itimbre_usuario': fields.char(
            'Usuario Itimbre',
        ),
        'itimbre_id': fields.char(
            'ID',
        ),
        'company_id': fields.many2one('res.company', 'Company', required=True,
            help='Company where you add this certificate'),
        'certificate_file': fields.binary('Certificate File',
            filters='*.cer,*.certificate,*.cert', required=True,
            help='This file .cer is proportionate by the SAT'),
        'PFX_file': fields.binary('Archivo PFX',),
        'certificate_key_file': fields.binary('Certificate Key File',
            filters='*.key', required=True, help='This file .key is \
            proportionate by the SAT'),
        'certificate_password': fields.char('Certificate Password', size=64,
            invisible=False, required=True, help='This password is \
            proportionate by the SAT'),
        'certificate_file_pem': fields.binary('Certificate File PEM',
            filters='*.pem,*.cer,*.certificate,*.cert', help='This file is \
            generated with the file.cer'),
        'certificate_key_file_pem': fields.binary('Certificate Key File PEM',
            filters='*.pem,*.key', help='This file is generated with the \
            file.key'),
        'date_start': fields.date('Date Start', required=False, help='Date \
            start the certificate before the SAT'),
        'date_end': fields.date('Date End', required=True, help='Date end of \
            validity of the certificate'),
        'serial_number': fields.char('Serial Number', size=64, required=True,
            help='Number of serie of the certificate'),
        'fname_xslt': fields.char('File XML Parser (.xslt)', size=256,
            required=False, help='Folder in server with XSLT file',
        # TODO, translate to english and later translate to spanish, que
        # parsea al XML.\nPuedes ser la ruta completa o suponiendo el
        # prefijo del "root_path\"\nDejar vacio para que el sistema tome el
        # que esta por default.'
        ),
        'active': fields.boolean('Active', help='Indicate if this certificate \
            is active'),
    }

    _defaults = {
        'active': lambda *a: True,
        #'fname_xslt': lambda *a: os.path.join('addons', 'l10n_mx_facturae', 'SAT', 'cadenaoriginal_2_0_l.xslt'),
        #'date_start': lambda *a: strftime('%Y-%m-%d'),
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company'\
            )._company_default_get(cr, uid, 'res.company.facturae.certificate',
            context=c),
    }

    def get_certificate_info(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        certificate = self.browse(cr, uid, ids, context=context)[0]
        cer_der_b64str = certificate.certificate_file
        key_der_b64str = certificate.certificate_key_file
        password = certificate.certificate_password
        data = self.onchange_certificate_info(
            cr, uid, ids, cer_der_b64str, key_der_b64str, password, context=context)
        if data['warning']:
            raise osv.except_osv(data['warning'][
                                 'title'], data['warning']['message'])
        return self.write(cr, uid, ids, data['value'], context)

    def onchange_certificate_info(self, cr, uid, ids, cer_der_b64str = None,
        key_der_b64str = None, password = None, context = None):
        """
        @param cer_der_b64str : File .cer in Base 64
        @param key_der_b64str : File .key in Base 64
        @param password : Password inserted in the certificate configuration
        """
        if context is None:
            contex={}
        certificate_lib = self.pool.get('facturae.certificate.library')
        value = {}
        warning = {}
        certificate_file_pem = False
        certificate_key_file_pem = False
        invoice_obj = self.pool.get('account.invoice')
        if cer_der_b64str and key_der_b64str and password:
            fname_cer_der = certificate_lib.b64str_to_tempfile(cr, uid, ids,
                cer_der_b64str, file_suffix='.der.cer',
                file_prefix='openerp__' + (False or '') + '__ssl__', context=context )
            fname_key_der = certificate_lib.b64str_to_tempfile(cr, uid, ids,
                key_der_b64str, file_suffix='.der.key',
                file_prefix='openerp__' + (False or '') + '__ssl__', context=context)
            fname_password = certificate_lib.b64str_to_tempfile(cr, uid, ids, 
                base64.encodestring(password), file_suffix='der.txt', 
                file_prefix='openerp__' + (False or '') + '__ssl__', context=context)
            fname_tmp = certificate_lib.b64str_to_tempfile(cr, uid, ids,
                '', file_suffix='tmp.txt', file_prefix='openerp__' + (
                False or '') + '__ssl__', context=context)

            cer_pem = certificate_lib._transform_der_to_pem(
                fname_cer_der, fname_tmp, type_der='cer')
            cer_pem_b64 = base64.encodestring(cer_pem)

            key_pem = certificate_lib._transform_der_to_pem(
                fname_key_der, fname_tmp, fname_password, type_der='key')
            key_pem_b64 = base64.encodestring(key_pem)

            # date_fmt_return='%Y-%m-%d %H:%M:%S'
            date_fmt_return = '%Y-%m-%d'
            serial = False
            try:
                serial = certificate_lib._get_param_serial(cr, uid, ids,
                    fname_cer_der, fname_tmp, type='DER')
                value.update({
                    'serial_number': serial,
                })
            except:
                pass
            date_start = False
            date_end = False
            try:
                dates = certificate_lib._get_param_dates(cr, uid, ids, fname_cer_der,
                    fname_tmp, date_fmt_return=date_fmt_return, type='DER')
                date_start = dates.get('startdate', False)
                date_end = dates.get('enddate', False)
                value.update({
                    'date_start': date_start,
                    'date_end': date_end,
                })

            except:
                pass
            os.unlink(fname_cer_der)
            os.unlink(fname_key_der)
            os.unlink(fname_password)
            os.unlink(fname_tmp)

            if not key_pem_b64 or not cer_pem_b64:
                warning = {
                    'title': _('Warning!'),
                    'message': _('You certificate file, key file or password is incorrect.\nVerify uppercase and lowercase')
                }
                value.update({
                    'certificate_file_pem': False,
                    'certificate_key_file_pem': False,
                })
            else:
                value.update({
                    'certificate_file_pem': cer_pem_b64,
                    'certificate_key_file_pem': key_pem_b64,
                })
        return {'value': value, 'warning': warning}

    '''
    _sql_constraints = [
        ('number_start', 'CHECK (number_start < number_end )',\
            'El numero inicial (Desde), tiene que ser menor al final (Hasta)!'),
        ('number_end', 'CHECK (number_end > number_start )',\
            'El numero final (Hasta), tiene que ser mayor al inicial (Desde)!'),
        ('approval_number_uniq', 'UNIQUE (approval_number)',
            'El numero de aprobacion tiene que ser unico'),
    ]

    def _check_numbers_range(self, cr, uid, ids, context=None):
        approval = self.browse(cr, uid, ids[0], context=context)
        query = """SELECT approval_1.id AS id1, approval_2.id AS \
            id2--approval_1.number_start, approval_1.number_end,
            approval_2.number_start, approval_2.number_end, *
            FROM ir_sequence_approval approval_1
            INNER JOIN (
                SELECT *
                FROM ir_sequence_approval
               ) approval_2
               ON approval_2.sequence_id = approval_1.sequence_id
              AND approval_2.id <> approval_1.id
            WHERE approval_1.sequence_id = %d
              AND ( approval_1.number_start between approval_2.number_start \
                and approval_2.number_end )
            LIMIT 1
        """%( approval.sequence_id.id )
        cr.execute( query )
        res = cr.dictfetchone()
        if res:
            return False
        return True

    _constraints = [
        (_check_numbers_range, 'Error ! Hay rangos de numeros solapados entre \
            aprobaciones.', ['sequence_id', 'number_start', 'number_end'])
    ]
    '''


class res_company(osv.Model):
    _inherit = 'res.company'

    def ____get_current_certificate(self, cr, uid, ids, field_names=None, arg=False, context=None):
        if context is None:
            context = {}
        if not field_names:
            field_names = []
        res = {}
        for id in ids:
            if "tiny" in release.name:
                res[id] = False
                field_names = [field_names]
            else:
                res[id] = {}.fromkeys(field_names, False)
        certificate_obj = self.pool.get('res.company.facturae.certificate')
        date = context.get('date', False) or strftime('%Y-%m-%d')
        for company in self.browse(cr, uid, ids, context=context):
            certificate_ids = certificate_obj.search(cr, uid, [
                ('company_id', '=', company.id),
                ('date_start', '<=', date),
                ('date_end', '>=', date),
                ('active', '=', True),
            ], limit=1)
            certificate_id = certificate_ids and certificate_ids[0] or False
            for f in field_names:
                if f == 'certificate_id':
                    if "tiny" in release.name:
                        res[company.id] = certificate_id
                    else:
                        res[company.id][f] = certificate_id
        return res

    def _get_current_certificate(self, cr, uid, ids, field_names=False, arg=False, context=None):
        if context is None:
            context = {}
        res = {}.fromkeys(ids, False)
        certificate_obj = self.pool.get('res.company.facturae.certificate')

        date = strftime('%Y-%m-%d')

        if 'date_work' in context:
            # Si existe este key, significa, que no viene de un function, si no
            # de una invocacion de factura
            date = context['date_work']
            if not date:
                # Si existe el campo, pero no esta asignado, significa que no fue por un function, y que no se requiere la current_date
                # print "NOTA: Se omitio el valor de date"
                return res
        for company in self.browse(cr, uid, ids, context=context):
            current_company = company
            certificate_ids = certificate_obj.search(cr, uid, [
                ('company_id', '=', company.id),
                ('date_start', '<=', date),
                ('date_end', '>=', date),
                ('active', '=', True),
            ], limit=1)
            certificate_id = certificate_ids and certificate_ids[0] or False
            res[current_company.id] = certificate_id
        return res

    """
    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        if not default:
            default = {}
        default = default.copy()
        default['certificate_ids'] = False
        return super(res_company, self).copy(cr, uid, id, default, context=context)
    """

    _columns = {
        'certificate_ids': fields.one2many('res.company.facturae.certificate',
            'company_id', 'Certificates', help='Certificates configurated in \
            this company'),
        'certificate_id': fields.function(_get_current_certificate, method=True,
            type='many2one', relation='res.company.facturae.certificate',
            string='Certificate Current', help='Serial Number of the \
            certificate active and inside of dates in this company'),
        #'cif_file': fields.binary('Cedula de Identificacion Fiscal'),
        'invoice_out_sequence_id': fields.many2one('ir.sequence',
            'Invoice Out Sequence', help="The sequence used for invoice out \
            numbers."),
        'invoice_out_refund_sequence_id': fields.many2one('ir.sequence',
            'Invoice Out Refund Sequence', help="The sequence used for \
            invoice out refund numbers."),
    }
class facturae_certificate_library(osv.Model):
    _name = 'facturae.certificate.library'
    _auto = False
    # Agregar find subpath

    def b64str_to_tempfile(self, cr, uid, ids, b64_str=None, file_suffix=None, file_prefix=None, context=None):
        """
        @param b64_str : Text in Base_64 format for add in the file
        @param file_suffix : Sufix of the file
        @param file_prefix : Name of file in TempFile
        """
        if context is None:
            context = {}
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(b64_str or ''))
        f.close()
        os.close(fileno)
        return fname

    def _read_file_attempts(self, file_obj, max_attempt=12, seconds_delay=0.5):
        """
        @param file_obj : Object with the path of the file, more el mode
            of the file to create (read, write, etc)
        @param max_attempt : Max number of attempt
        @param seconds_delay : Seconds valid of delay
        """
        fdata = False
        cont = 1
        while True:
            sleep(seconds_delay)
            try:
                fdata = file_obj.read()
            except:
                pass
            if fdata or max_attempt < cont:
                break
            cont += 1
        return fdata

    def _transform_der_to_pem(self, fname_der, fname_out,
        fname_password_der=None, type_der='cer'):
        """
        @param fname_der : File.cer configurated in the company
        @param fname_out : Information encrypted in Base_64from certificate
            that is send
        @param fname_password_der : File that contain the password configurated
            in this Certificate
        @param type_der : cer or key
        """
        if not app_openssl_fullpath:
            raise osv.except_osv(_("Error!"), _(
                "Failed to find in path '%s' app. This app is required for sign Mexican Electronic Invoice"%(app_openssl) ))
        cmd = ''
        result = ''
        if type_der == 'cer':
            cmd = '"%s" x509 -inform DER -outform PEM -in "%s" -pubkey -out "%s"' % (
                app_openssl_fullpath, fname_der, fname_out)
        elif type_der == 'key':
            cmd = '"%s" pkcs8 -inform DER -outform PEM -in "%s" -passin file:%s -out "%s"' % (
                app_openssl_fullpath, fname_der, fname_password_der, fname_out)
        if cmd:
             # provisionalmente, porque no funcionaba en win32

            args = tuple(cmd.split(' '))

            #input, output = tools.exec_command_pipe(*args)
            input, output = exec_command_pipe(*args)
            result = self._read_file_attempts(open(fname_out, "r"))
            input.close()
            output.close()
        return result

    def _get_param_serial(self, cr, uid, ids, fname, fname_out=None, type='DER', context=None):
        """
        @param fname : File.PEM with the information of the certificate
        @param fname_out : File.xml that is send
        """
        if context is None:
            context = {}
        result = self._get_params(cr, uid, ids, fname, params=['serial'], 
                                    fname_out=fname_out, type=type)
        result = result and result.replace('serial=', '').replace(
            '33', 'B').replace('3', '').replace('B', '3').replace(
            ' ', '').replace('\r', '').replace('\n', '').replace('\r\n', '') or ''
        return result

    def _transform_xml(self, cr, uid, ids, fname_xml, fname_xslt, fname_out, context=None):
        """
        @param fname_xml : Path and name of the XML of Facturae
        @param fname_xslt : Path where is located the file 'Cadena Original'.xslt
        @param fname_out : Path and name of the file.xml that is send to sign
        """
        if context is None:
            context = {}
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if not app_xsltproc_fullpath:
            raise osv.except_osv(_("Error!"), _(
                "Failed to find in path '%s' app. This app is required for sign Mexican Electronic Invoice"%(app_xsltproc) ))
        cmd = '"%s" "%s" "%s" >"%s"' % (
            app_xsltproc_fullpath, fname_xslt, fname_xml, fname_out)
        args = tuple(cmd.split(' '))
        input, output = exec_command_pipe(*args)
        result = self._read_file_attempts(open(fname_out, "r"))
        input.close()
        output.close()
        return result

    def _get_param_dates(self, cr, uid, ids, fname, fname_out=None,
        date_fmt_return='%Y-%m-%d %H:%M:%S', type='DER', context=None):
        """
        @param fname : File.cer with the information of the certificate
        @params fname_out : Path and name of the file.txt with info encrypted
        @param date_fmt_return : Format of the date used
        @param type : Type of file
        """
        if context is None:
            context = {}
        result_dict = self._get_params_dict(cr, uid, ids, fname, params=[
                                    'dates'], fname_out=fname_out, type=type)
        translate_key = {
            'notAfter': 'enddate',
            'notBefore': 'startdate',
        }
        result2 = {}
        if result_dict:
            date_fmt_src = "%b %d %H:%M:%S %Y GMT"
            for key in result_dict.keys():
                date = result_dict[key]
                date_obj = time.strptime(date, date_fmt_src)
                date_fmt = strftime(date_fmt_return, date_obj)
                result2[translate_key[key]] = date_fmt
        return result2

    def _get_params_dict(self, cr, uid, ids, fname, params=None, fname_out=None, type='DER', context=None):
        """
        @param fname : File.cer with the information of the certificate
        @param params : List of params used for this function
        @param fname_out : Path and name of the file.txt with info encrypted
        @param type : Type of file
        """
        if context is None:
            context = {}
        result = self._get_params(cr, uid, ids, fname, params, fname_out, type)
        result = result.replace('\r\n', '\n').replace(
            '\r', '\n')  # .replace('\n', '\n)
        result = result.rstrip('\n').lstrip('\n').rstrip(' ').lstrip(' ')
        result_list = result.split('\n')
        params_dict = {}
        for result_item in result_list:
            if result_item:
                key, value = result_item.split('=')
                params_dict[key] = value
        return params_dict

    def _get_params(self, cr, uid, ids, fname, params=None, fname_out=None, type='DER', context=None):
        """
        @params: list [noout serial startdate enddate subject issuer dates]
        @type: str DER or PEM
        """
        if context is None:
            context = {}
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if not app_openssl_fullpath:
            raise osv.except_osv(_("Error!"), _(
                "Failed to find in path '%s' app. This app is required for sign Mexican Electronic Invoice"%(app_openssl) ))
        cmd_params = ' -'.join(params)
        cmd_params = cmd_params and '-' + cmd_params or ''
        cmd = '"%s" x509 -inform "%s" -in "%s" -noout "%s" -out "%s"' % (
            app_openssl_fullpath, type, fname, cmd_params, fname_out)
        args = tuple(cmd.split(' '))
        # input, output = tools.exec_command_pipe(*args)
        input, output = exec_command_pipe(*args)
        result = self._read_file_attempts(output)
        input.close()
        output.close()
        return result

    def _sign(self, cr, uid, ids, fname, fname_xslt, fname_key, fname_out, encrypt='sha1',
        type_key='PEM', context=None):
        """
         @params fname : Path and name of the XML of Facturae
         @params fname_xslt : Path where is located the file 'Cadena Original'.xslt
         @params fname_key : Path and name of the file.pem with data of the key
         @params fname_out : Path and name of the file.txt with info encrypted
         @params encrypt : Type of encryptation for file
         @params type_key : Type of KEY
        """
        if context is None:
            context = {}
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = \
                    library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        result = ""
        cmd = ''
        if type_key == 'PEM':
            if not app_xsltproc_fullpath:
                raise osv.except_osv(_("Error!"), _(
                    "Failed to find in path '%s' app. This app is required for sign Mexican Electronic Invoice"%(app_xsltproc) ))
            cmd = '"%s" "%s" "%s" | "%s" dgst -%s -sign "%s" | "%s" enc -base64 -A -out "%s"' % (
                app_xsltproc_fullpath, fname_xslt, fname, app_openssl_fullpath,
                    encrypt, fname_key, app_openssl_fullpath, fname_out)
        elif type_key == 'DER':
            # TODO: Dev for type certificate DER
            pass
        if cmd:
            input, output = exec_command_pipe(cmd)
            result = self._read_file_attempts(open(fname_out, "r"))
            input.close()
            output.close()
        return result

    def check_xml_scheme(self, cr, uid, ids, fname_xml, fname_scheme, fname_out, type_scheme="xsd",
                            context=None):
        #xmlstarlet val -e --xsd cfdv2.xsd cfd_example.xml
        if context is None:
            context = {}
        msj, app_xsltproc_fullpath, app_openssl_fullpath, app_xmlstarlet_fullpath = library_openssl_xsltproc_xmlstarlet(cr, uid, ids, context)
        if app_xmlstarlet_fullpath:
            cmd = ''
            if type_scheme == 'xsd':
                cmd = '"%s" val -e --%s "%s" "%s" 1>"%s" 2>"%s"'%(app_xmlstarlet_fullpath, type_scheme, fname_scheme, fname_xml, fname_out+"1", fname_out)
            if cmd:
                args = tuple( cmd.split(' ') )
                input, output = exec_command_pipe(*args)
                result = self._read_file_attempts( open(fname_out, "r") )
                input.close()
                output.close()
        else:
            _logger.warning("Failed to find in path 'xmlstarlet' app. Can't validate xml structure. You should make a manual check to xml file.")
            result = ""
        return result

    # Funciones en desuso
    def binary2file(self, cr=False, uid=False, ids=[], binary_data=False,
        file_prefix="", file_suffix=""):
        """
        @param binary_data : Field binary with the information of certificate
            of the company
        @param file_prefix : Name to be used for create the file with the
            information of certificate
        @file_suffix : Sufix to be used for the file that create in this function
        """
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open(fname, 'wb')
        f.write(base64.decodestring(binary_data))
        f.close()
        os.close(fileno)
        return fname

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

