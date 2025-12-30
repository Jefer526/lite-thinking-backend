"""
Generación de reportes PDF para Inventario
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime


def generar_pdf_inventario(inventarios):
    """
    Genera un PDF con el reporte de inventario
    
    Args:
        inventarios: QuerySet de Inventario
    
    Returns:
        BytesIO con el PDF generado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#417690'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    title = Paragraph("REPORTE DE INVENTARIO", title_style)
    elements.append(title)
    
    # Fecha
    fecha_style = ParagraphStyle(
        'Fecha',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT
    )
    fecha = Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fecha_style)
    elements.append(fecha)
    elements.append(Spacer(1, 0.3*inch))
    
    # Datos de la tabla
    data = [['Código', 'Producto', 'Cantidad', 'Ubicación', 'Estado']]
    
    for inv in inventarios:
        data.append([
            inv.producto.codigo,
            inv.producto.nombre[:40],  # Limitar longitud
            str(inv.cantidad_actual),
            inv.ubicacion or 'N/A',
            inv.estado_stock
        ])
    
    # Crear tabla
    table = Table(data, colWidths=[1*inch, 3*inch, 1*inch, 1.5*inch, 1*inch])
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#417690')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Datos
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Cantidad centrada
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Estado centrado
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    
    # Resumen
    elements.append(Spacer(1, 0.3*inch))
    total_productos = inventarios.count()
    total_unidades = sum(inv.cantidad_actual for inv in inventarios)
    
    resumen_style = ParagraphStyle(
        'Resumen',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10
    )
    
    elements.append(Paragraph(f"<b>Total de Productos:</b> {total_productos}", resumen_style))
    elements.append(Paragraph(f"<b>Total de Unidades:</b> {total_unidades}", resumen_style))
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer