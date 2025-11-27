"""
Beautiful, Professional PDF Reports - Contemporary Design
Matches the modern, beautiful UI of forms and dashboards
"""

from io import BytesIO
from datetime import datetime
from decimal import Decimal
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    KeepTogether, PageTemplate, Frame, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from core.models.school_details import SchoolDetails


def get_school_name():
    """Get school name from database"""
    try:
        school = SchoolDetails.objects.first()
        if school and school.school_name:
            return school.school_name
    except:
        pass
    return "EDEN PRIMARY SCHOOL"


class BeautifulPDFReport:
    """Beautiful, contemporary PDF reports matching modern UI standards"""
    
    # Modern elegant color palette - light and fresh
    PRIMARY = '#3b82f6'      # Bright, friendly blue
    PRIMARY_DARK = '#1e40af' # Deep blue for contrast
    ACCENT = '#06b6d4'       # Cyan accent (modern feel)
    SUCCESS = '#10b981'      # Green
    WARNING = '#f59e0b'      # Amber
    DANGER = '#ef4444'       # Red
    LIGHT = '#f0f9ff'        # Very light blue
    LIGHT_GRAY = '#f3f4f6'   # Light gray
    BORDER = '#e0e7ff'       # Light indigo border
    TEXT_DARK = '#1f2937'    # Dark text
    TEXT_LIGHT = '#6b7280'   # Muted text
    WHITE = '#ffffff'        # White
    
    @staticmethod
    def build_pdf(title, subtitle, sections, filename="report"):
        """Build beautiful, contemporary PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.4*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch,
        )
        story = []
        school_name = get_school_name()
        
        # ===== BEAUTIFUL HEADER =====
        # School name as a proper title (not a bar header)
        school_style = ParagraphStyle(
            'SchoolName',
            fontSize=18,
            textColor=colors.HexColor(BeautifulPDFReport.PRIMARY),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=22
        )
        story.append(Paragraph(school_name.upper(), school_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Title with strong styling
        title_style = ParagraphStyle(
            'Title',
            fontSize=20,
            textColor=colors.HexColor(BeautifulPDFReport.PRIMARY),
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=24
        )
        story.append(Paragraph(title, title_style))
        
        # Subtitle with accent cyan color
        if subtitle:
            subtitle_style = ParagraphStyle(
                'Subtitle',
                fontSize=10,
                textColor=colors.HexColor(BeautifulPDFReport.ACCENT),
                spaceAfter=16,
                alignment=TA_CENTER,
                fontName='Helvetica',
                leading=12
            )
            story.append(Paragraph(subtitle, subtitle_style))
        else:
            story.append(Spacer(1, 0.08*inch))
        
        # Add sections
        for section_title, section_data, section_type in sections:
            if section_type == 'info_card':
                BeautifulPDFReport._add_info_card(story, section_title, section_data)
            elif section_type == 'table':
                BeautifulPDFReport._add_data_table(story, section_title, section_data)
            elif section_type == 'stat_grid':
                BeautifulPDFReport._add_stat_grid(story, section_data)
        
        # Footer
        story.append(Spacer(1, 0.25*inch))
        footer_style = ParagraphStyle(
            'Footer',
            fontSize=7.5,
            textColor=colors.HexColor(BeautifulPDFReport.TEXT_LIGHT),
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=9
        )
        story.append(Paragraph(
            f"© {datetime.now().year} {school_name} | Official School Document",
            footer_style
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def _add_info_card(story, title, data):
        """Add beautiful information card section with improved styling"""
        # Card header with bright blue
        header_data = [[title]]
        header_table = Table(header_data, colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(BeautifulPDFReport.PRIMARY)),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor(BeautifulPDFReport.WHITE)),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 11),
            ('PADDING', (0, 0), (0, 0), 10),
            ('LEFTPADDING', (0, 0), (0, 0), 12),
            ('ALIGNMENT', (0, 0), (0, 0), 'LEFT'),
        ]))
        story.append(header_table)
        
        # Card content with very light background
        content_table = Table(data, colWidths=[2.8*inch, 4.7*inch])
        content_table.setStyle(TableStyle([
            # Very light blue/white background
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
            # Alternating row backgrounds - subtle difference
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [
                colors.HexColor('#f0f9ff'),
                colors.HexColor('#f9fafb')
            ]),
            # Text colors - strong labels, dark values
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0369a1')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#374151')),
            # Font styling
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            # Light borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1e7f0')),
            # Better padding
            ('PADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 11),
            ('RIGHTPADDING', (0, 0), (-1, -1), 11),
            ('TOPPADDING', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ]))
        story.append(content_table)
        story.append(Spacer(1, 0.22*inch))
    
    @staticmethod
    def _add_stat_grid(story, stats):
        """Add statistics grid with beautiful cards"""
        # Create 2-column layout
        for i in range(0, len(stats), 2):
            row_data = [stats[i], stats[i+1] if i+1 < len(stats) else None]
            
            # Filter out None values
            row_data = [s for s in row_data if s]
            
            stat_table = Table([row_data], colWidths=[3.75*inch for _ in row_data])
            
            # Apply beautiful styling with light background
            style_list = [
                ('BACKGROUND', (0, 0), (len(row_data)-1, 0), colors.HexColor('#f0f9ff')),
                ('TEXTCOLOR', (0, 0), (len(row_data)-1, 0), colors.HexColor(BeautifulPDFReport.TEXT_DARK)),
                ('ALIGN', (0, 0), (len(row_data)-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (len(row_data)-1, 0), 'MIDDLE'),
                ('GRID', (0, 0), (len(row_data)-1, 0), 0.5, colors.HexColor('#d1e7f0')),
                ('FONTSIZE', (0, 0), (len(row_data)-1, 0), 10),
                ('PADDING', (0, 0), (len(row_data)-1, 0), 14),
                ('TOPPADDING', (0, 0), (len(row_data)-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (len(row_data)-1, 0), 12),
            ]
            
            stat_table.setStyle(TableStyle(style_list))
            story.append(stat_table)
        
        story.append(Spacer(1, 0.15*inch))
    
    @staticmethod
    def _add_data_table(story, title, data):
        """Add beautiful data table with enhanced styling"""
        # Table header - more prominent with bright blue
        header_table = Table([[title]], colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(BeautifulPDFReport.PRIMARY)),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor(BeautifulPDFReport.WHITE)),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 11),
            ('PADDING', (0, 0), (0, 0), 10),
            ('LEFTPADDING', (0, 0), (0, 0), 12),
        ]))
        story.append(header_table)
        
        # Data table
        if len(data) > 1:
            headers = data[0]
            rows = data[1:]
            num_cols = len(headers)
            col_width = 7.5 / num_cols
            
            table = Table(data, colWidths=[col_width*inch for _ in range(num_cols)])
            
            # Beautiful table styling with light theme
            table_style = [
                # Header row - bright blue
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(BeautifulPDFReport.WHITE)),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9.5),
                ('PADDING', (0, 0), (-1, 0), 10),
                ('ALIGNMENT', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                # Data rows with very light backgrounds
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor(BeautifulPDFReport.TEXT_DARK)),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
                    colors.HexColor('#ffffff'),
                    colors.HexColor('#f9fafb')
                ]),
                # Light borders
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1e7f0')),
                # Padding
                ('PADDING', (0, 1), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 9),
                ('RIGHTPADDING', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]
            
            table.setStyle(TableStyle(table_style))
            story.append(table)
        
        story.append(Spacer(1, 0.18*inch))


class PaymentHistoryReport(BeautifulPDFReport):
    """Generate beautiful payment history reports"""
    
    @staticmethod
    def generate_student_payment_pdf(student, payments, balance_info=None):
        """Generate modern payment history PDF"""
        sections = []
        
        # Student Information Card
        student_data = [
            ['Student ID:', str(student.id)],
            ['Full Name:', student.full_name],
            ['Date of Birth:', student.date_of_birth.strftime('%B %d, %Y')],
            ['Current Class:', str(student.current_class) if student.current_class else 'N/A'],
        ]
        sections.append(('Student Information', student_data, 'info_card'))
        
        # Balance Summary Card
        if balance_info:
            balance_data = [
                ['Term Fee:', f"${float(balance_info.get('term_fee', 0)):,.2f}"],
                ['Amount Paid:', f"${float(balance_info.get('amount_paid', 0)):,.2f}"],
                ['Previous Arrears:', f"${float(balance_info.get('previous_arrears', 0)):,.2f}"],
                ['Current Balance:', f"${float(balance_info.get('current_balance', 0)):,.2f}"],
            ]
            sections.append(('Balance Summary', balance_data, 'info_card'))
        
        # Payment Transactions Table
        if payments:
            table_data = [['Date', 'Amount', 'Method', 'Reference']]
            for payment in payments:
                table_data.append([
                    payment.created_at.strftime('%m/%d/%Y'),
                    f"${payment.amount:,.2f}",
                    payment.get_payment_method_display() if hasattr(payment, 'get_payment_method_display') else 'N/A',
                    payment.reference_number or 'Auto',
                ])
            sections.append(('Payment Transactions', table_data, 'table'))
        
        buffer = BeautifulPDFReport.build_pdf(
            'Payment History Report',
            f'Student: {student.full_name}',
            sections
        )
        return buffer
    
    @staticmethod
    def generate_fee_dashboard_pdf(current_term, students_data):
        """Generate beautiful fee dashboard PDF"""
        sections = []
        
        # Calculate statistics
        total_students = len(students_data)
        total_collected = sum(Decimal(str(s.get('amount_paid', 0))) for s in students_data)
        total_balance = sum(Decimal(str(s.get('current_balance', 0))) for s in students_data)
        total_term_fee = sum(Decimal(str(s.get('term_fee', 0))) for s in students_data)
        collection_pct = (float(total_collected) / float(total_term_fee) * 100) if float(total_term_fee) > 0 else 0
        
        # Summary statistics
        summary_data = [
            ['Total Students:', str(total_students)],
            ['Total Term Fees:', f"${float(total_term_fee):,.2f}"],
            ['Total Collected:', f"${float(total_collected):,.2f}"],
            ['Collection Rate:', f"{collection_pct:.1f}%"],
            ['Outstanding Balance:', f"${float(total_balance):,.2f}"],
        ]
        sections.append(('Fee Collection Summary', summary_data, 'info_card'))
        
        # Student Details Table
        if students_data:
            table_data = [['Student Name', 'Class', 'Term Fee', 'Paid', 'Balance', 'Status']]
            for student in students_data:
                balance = float(student.get('current_balance', 0))
                status = '✓ PAID' if balance <= 0 else '○ PENDING'
                table_data.append([
                    student.get('name', 'N/A')[:18],
                    str(student.get('class', 'N/A'))[:10],
                    f"${float(student.get('term_fee', 0)):,.0f}",
                    f"${float(student.get('amount_paid', 0)):,.0f}",
                    f"${balance:,.0f}",
                    status
                ])
            sections.append(('Student Fee Details', table_data, 'table'))
        
        buffer = BeautifulPDFReport.build_pdf(
            'Fee Collection Report',
            f'Term: {current_term}',
            sections
        )
        return buffer


class ArrearsReport(BeautifulPDFReport):
    """Generate beautiful arrears reports"""
    
    @staticmethod
    def generate_arrears_pdf(students_with_arrears, term=None):
        """Generate beautiful arrears collection report"""
        sections = []
        
        # Summary
        total_arrears = sum(Decimal(str(s.get('balance', 0))) for s in students_with_arrears)
        num_students = len(students_with_arrears)
        avg_arrears = float(total_arrears) / num_students if num_students > 0 else 0
        
        summary_data = [
            ['Students with Arrears:', str(num_students)],
            ['Total Outstanding:', f"${float(total_arrears):,.2f}"],
            ['Average Arrears:', f"${avg_arrears:,.2f}"],
            ['Report Date:', datetime.now().strftime('%B %d, %Y')],
        ]
        sections.append(('Arrears Summary', summary_data, 'info_card'))
        
        # Arrears List
        if students_with_arrears:
            table_data = [['Student Name', 'ID', 'Class', 'Outstanding', 'Priority']]
            for student in students_with_arrears:
                balance = float(student.get('balance', 0))
                if balance > 10000:
                    priority = '🔴 CRITICAL'
                elif balance > 5000:
                    priority = '🟠 HIGH'
                else:
                    priority = '🟡 MEDIUM'
                
                table_data.append([
                    student.get('name', 'Unknown')[:18],
                    str(student.get('id', 'N/A')),
                    str(student.get('current_class', 'N/A')),
                    f"${balance:,.2f}",
                    priority
                ])
            sections.append(('Students with Outstanding Balances', table_data, 'table'))
        
        buffer = BeautifulPDFReport.build_pdf(
            'Arrears Collection Report',
            f'Term: {term}' if term else 'Outstanding Balance Summary',
            sections
        )
        return buffer


def create_pdf_response(pdf_buffer, filename):
    """Helper function to create HTTP response for PDF download"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf_buffer.getvalue())
    return response
