"""Generador de PDFs para facturas y recibos."""
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..domain.models import Venta


def generar_factura_pdf(venta: Venta, venta_id: int, output_dir: Optional[str] = None) -> str:
    """
    Genera un PDF de factura/recibo para una venta.
    
    Args:
        venta: Objeto Venta con todos los datos
        venta_id: ID de la venta
        output_dir: Directorio donde guardar el PDF (por defecto: ./facturas)
        
    Returns:
        str: Ruta completa al archivo PDF generado
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "reportlab no está instalado. Instálelo con: pip install reportlab"
        )
    
    # Directorio de salida
    if output_dir is None:
        output_dir = Path("facturas")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # Nombre del archivo
    numero_factura = venta.numero_factura or f"FACT-{venta_id:05d}"
    fecha_str = venta.fecha.strftime("%Y%m%d_%H%M%S") if venta.fecha else datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{numero_factura}_{fecha_str}.pdf"
    pdf_path = output_dir / filename
    
    # Crear documento con márgenes adecuados
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Estilos personalizados
    styles = getSampleStyleSheet()
    
    # Estilo para título principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#dc0000'),
        alignment=TA_CENTER,
        spaceAfter=20,
        spaceBefore=10
    )
    
    # Estilo para encabezados de sección
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#dc0000'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        spaceAfter=6
    )
    
    # Contenido
    story = []
    
    # ========== ENCABEZADO ==========
    story.append(Paragraph("FACTURA / RECIBO", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    # ========== INFORMACIÓN PRINCIPAL DE LA FACTURA ==========
    # Preparar fecha y hora
    fecha_hora = venta.fecha.strftime("%d/%m/%Y %H:%M:%S") if venta.fecha else datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Información principal - organizada en dos columnas claras
    info_data = []
    
    # Fila 1: Número de factura
    info_data.append([
        Paragraph('<b>Número de Factura:</b>', normal_style),
        Paragraph(numero_factura, normal_style)
    ])
    
    # Fila 2: ID de Venta
    info_data.append([
        Paragraph('<b>ID de Venta:</b>', normal_style),
        Paragraph(str(venta_id), normal_style)
    ])
    
    # Fila 3: Fecha y Hora
    info_data.append([
        Paragraph('<b>Fecha y Hora:</b>', normal_style),
        Paragraph(fecha_hora, normal_style)
    ])
    
    # Fila 4: ID de Cliente (si existe)
    if venta.cliente_id:
        info_data.append([
            Paragraph('<b>ID de Cliente:</b>', normal_style),
            Paragraph(str(venta.cliente_id), normal_style)
        ])
    else:
        info_data.append([
            Paragraph('<b>Cliente:</b>', normal_style),
            Paragraph('Consumidor Final', normal_style)
        ])
    
    # Crear tabla de información principal
    info_table = Table(info_data, colWidths=[6*cm, 9*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a1a')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#2a2a2a')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dc0000')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.8*cm))
    
    # ========== DETALLE DE PRODUCTOS ==========
    story.append(Paragraph("DETALLE DE PRODUCTOS", heading_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Encabezados de tabla de productos
    headers = ['Código', 'Producto', 'Cant.', 'P. Unit.', 'Subtotal']
    table_data = [headers]
    
    # Agregar productos
    for item in venta.items:
        table_data.append([
            item.codigo_producto,
            item.nombre_producto,
            str(item.cantidad),
            f"${item.precio_unitario:,.2f}",
            f"${item.calcular_subtotal():,.2f}"
        ])
    
    # Crear tabla de productos
    product_table = Table(table_data, colWidths=[2.5*cm, 6*cm, 1.5*cm, 2.5*cm, 2.5*cm])
    product_table.setStyle(TableStyle([
        # Encabezados
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc0000')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # Datos
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#121212')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Nombre alineado a la izquierda
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Números a la derecha
        
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dc0000')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        
        # Filas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#1a1a1a'), colors.HexColor('#121212')]),
    ]))
    
    story.append(product_table)
    story.append(Spacer(1, 1*cm))
    
    # ========== SECCIÓN DE TOTALES (REORGANIZADA Y CORREGIDA) ==========
    story.append(Paragraph("TOTALES", heading_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Tabla de totales parciales - ALINEADA CORRECTAMENTE
    totales_data = [
        [
            Paragraph('Subtotal:', normal_style),
            Paragraph(f"${venta.subtotal:,.2f}", normal_style)
        ],
        [
            Paragraph('Descuento:', normal_style),
            Paragraph(f"${venta.descuento_total:,.2f}", normal_style)
        ],
        [
            Paragraph('Impuestos:', normal_style),
            Paragraph(f"${venta.impuesto_total:,.2f}", normal_style)
        ],
    ]
    
    # Estilo para totales parciales
    totales_style = TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a1a')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#2a2a2a')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Números a la derecha
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dc0000')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Espaciado vertical adecuado
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),  # Padding horizontal para evitar superposición
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#1a1a1a'), colors.HexColor('#2a2a2a'), colors.HexColor('#1a1a1a')]),
    ])
    
    totales_table = Table(totales_data, colWidths=[5*cm, 5*cm])
    totales_table.setStyle(totales_style)
    
    story.append(totales_table)
    story.append(Spacer(1, 0.6*cm))  # Espaciado antes del total final
    
    # Total final - SEPARADO Y BIEN ESPACIADO
    total_final_style = ParagraphStyle(
        'TotalFinal',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.white,
        alignment=TA_RIGHT
    )
    
    total_final_data = [
        [
            Paragraph('<b>TOTAL A PAGAR:</b>', total_final_style),
            Paragraph(f"<b>${venta.total:,.2f}</b>", total_final_style)
        ]
    ]
    
    total_final_table = Table(total_final_data, colWidths=[5*cm, 5*cm])
    total_final_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dc0000')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Total alineado a la derecha
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),  # Más padding para evitar superposición
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),  # Padding generoso
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#ff0000')),  # Borde más grueso
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(total_final_table)
    story.append(Spacer(1, 1*cm))
    
    # ========== PIE DE PÁGINA ==========
    pie_style = ParagraphStyle(
        'Pie',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER
    )
    
    pie_text = f"Factura generada el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    story.append(Paragraph(pie_text, pie_style))
    
    # Construir PDF
    doc.build(story)
    
    return str(pdf_path)
