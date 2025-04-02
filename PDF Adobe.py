# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 14:22:34 2025

@author: andre_trierveiler
"""

import logging
import os
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.pdfops.export_pdf_operation import ExportPDFOperation
from adobe.pdfservices.operation.pdfops.options.export_pdf_options import ExportPDFTargetFormat

# Configurar credenciais
credentials = ServicePrincipalCredentials.create_from_file("pdfservices-api-credentials.json")

# Criar operação de exportação
export_pdf_operation = ExportPDFOperation.create_new(ExportPDFTargetFormat.DOCX)

# Configurar o arquivo de entrada
source = CloudAsset.create_from_file("input.pdf")
export_pdf_operation.set_input(source)

# Executar a operação
result = export_pdf_operation.execute(credentials)
result.save_as("output.docx")