"""
PDF Report Generation Utilities
Generates professional, printable reports for financial statements and student records
"""

from io import BytesIO
from datetime import datetime
from decimal import Decimal
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, 
    Image, PageTemplate, Frame, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from core.models.school_details import SchoolDetails


def get_school_name():
    """Get school name from settings"""
    try:
        school = SchoolDetails.objects.first()
        if school and school.school_name:
            return school.school_name
    except:
        pass
    return "EDEN PRIMARY SCHOOL"


class SchoolHeaderFooter:
    """Common header and footer for all reports"""
    
    @staticmethod
    def add_header(story, title, subtitle=""):
        """Add school header to report"""
        styles = getSampleStyleSheet()
        school_name = get_school_name()
        
        # School name - Bold, Dark Blue
        school_title = ParagraphStyle(
            'SchoolTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=32
        )
        story.append(Paragraph(school_name.upper(), school_title))
        
        # Report title - Professional Blue
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#2d5a8c'),
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=22
        )
        story.append(Paragraph(title, title_style))
        
        # Subtitle if provided
        if subtitle:
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#4a5568'),
                spaceAfter=2,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            )
            story.append(Paragraph(subtitle, subtitle_style))
        
        # Decorative line
        story.append(Spacer(1, 0.1 * inch))
        
        # Report date - Right aligned, subtle
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#718096'),
            spaceAfter=20,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        )
        story.append(Paragraph(f"<i>Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>", date_style))


class PaymentHistoryReport:
    """Generate professional payment history reports"""
    
    @staticmethod
    def generate_student_payment_pdf(student, payments, balance_info=None):
        """Generate professional payment history PDF for a student"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Add header
        SchoolHeaderFooter.add_header(story, "Payment History Report", f"Student: {student.full_name}")
        
        # ===== STUDENT INFORMATION SECTION =====
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.white,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#2d5a8c'),
            borderPadding=8,
            leftIndent=4,
            rightIndent=4
        )
        story.append(Paragraph("📋 STUDENT INFORMATION", section_header_style))
        
        student_data = [
            ['Student ID:', str(student.id), 'Date of Birth:', student.date_of_birth.strftime('%B %d, %Y')],
            ['Full Name:', student.full_name, 'Current Class:', str(student.current_class) if student.current_class else 'N/A'],
            ['Enrollment Date:', student.date_enrolled.strftime('%B %d, %Y'), 'Status:', 'Active' if student.is_active else 'Inactive'],
        ]
        
        student_table = Table(student_data, colWidths=[1.2*inch, 1.8*inch, 1.2*inch, 1.8*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4f8')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        story.append(student_table)
        story.append(Spacer(1, 0.25*inch))
        
        # ===== BALANCE SUMMARY =====
        if balance_info:
            story.append(Paragraph("💰 BALANCE SUMMARY", section_header_style))
            
            # Create a nice 2x2 grid for balance info
            balance = float(balance_info.get('current_balance', 0))
            status_color = colors.HexColor('#10b981') if balance <= 0 else colors.HexColor('#ef4444')
            status_bg = colors.HexColor('#ecfdf5') if balance <= 0 else colors.HexColor('#fef2f2')
            status_text = '✓ PAID' if balance <= 0 else '⚠ UNPAID'
            
            balance_data = [
                ['Term Fee:', f"${float(balance_info.get('term_fee', 0)):.2f}", 'Amount Paid:', f"${float(balance_info.get('amount_paid', 0)):.2f}"],
                ['Previous Arrears:', f"${float(balance_info.get('previous_arrears', 0)):.2f}", 'Current Balance:', f"${float(balance_info.get('current_balance', 0)):.2f}"],
            ]
            
            balance_table = Table(balance_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            balance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4f8')),
                ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f4f8')),
                ('BACKGROUND', (1, 1), (1, 1), status_bg),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
                ('TEXTCOLOR', (1, 1), (1, 1), status_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTSIZE', (1, 1), (1, 1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            story.append(balance_table)
            story.append(Spacer(1, 0.25*inch))
        
        # ===== PAYMENT TRANSACTIONS =====
        story.append(Paragraph("📝 PAYMENT TRANSACTIONS", section_header_style))
        
        if payments:
            payment_data = [
                ['Date', 'Amount', 'Payment Method', 'Reference Number', 'Notes']
            ]
            
            for payment in payments:
                payment_data.append([
                    payment.created_at.strftime('%m/%d/%Y'),
                    f"${payment.amount:.2f}",
                    payment.get_payment_method_display() if hasattr(payment, 'get_payment_method_display') else 'N/A',
                    payment.reference_number or 'Auto-Generated',
                    payment.notes[:25] + '...' if payment.notes and len(payment.notes) > 25 else (payment.notes or '-')
                ])
            
            payment_table = Table(payment_data, colWidths=[1.0*inch, 1.0*inch, 1.1*inch, 1.3*inch, 1.6*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a8c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ]))
            story.append(payment_table)
        else:
            no_payment_style = ParagraphStyle(
                'NoData',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#718096'),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique',
                backColor=colors.HexColor('#f0f4f8'),
                borderPadding=12
            )
            story.append(Paragraph("No payment transactions recorded.", no_payment_style))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#a0aec0'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        story.append(Paragraph("This is an official document from " + get_school_name() + ". For inquiries, contact the school administration.", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_fee_dashboard_pdf(current_term, students_data):
        """Generate professional fee dashboard PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch, leftMargin=0.6*inch, rightMargin=0.6*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Add header
        SchoolHeaderFooter.add_header(story, "Fee Collection Report", f"Term: {current_term}")
        
        # ===== SUMMARY STATISTICS =====
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.white,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#2d5a8c'),
            borderPadding=8,
            leftIndent=4,
            rightIndent=4
        )
        story.append(Paragraph("💰 FEE COLLECTION SUMMARY", section_header_style))
        
        # Calculate totals
        total_students = len(students_data)
        total_collected = sum(Decimal(str(s.get('amount_paid', 0))) for s in students_data)
        total_balance = sum(Decimal(str(s.get('current_balance', 0))) for s in students_data)
        total_term_fee = sum(Decimal(str(s.get('term_fee', 0))) for s in students_data)
        
        # Collection percentage
        collection_pct = (float(total_collected) / float(total_term_fee) * 100) if float(total_term_fee) > 0 else 0
        
        # Create 2x2 summary grid
        summary_data = [
            ['Total Students', str(total_students), 'Total Term Fees', f"${float(total_term_fee):,.2f}"],
            ['Total Collected', f"${float(total_collected):,.2f}", 'Collection Rate', f"{collection_pct:.1f}%"],
            ['Total Outstanding', f"${float(total_balance):,.2f}", 'Report Date', datetime.now().strftime('%B %d, %Y')],
        ]
        
        summary_table = Table(summary_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0eaf8')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e0eaf8')),
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#d1fae5')),  # Green for collections
            ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#fee2e2')),  # Red for outstanding
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#065f46')),
            ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#7f1d1d')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (1, 1), (1, 1), 11),
            ('FONTSIZE', (1, 2), (1, 2), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafb')]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ===== DETAILED STUDENT FEE REPORT =====
        story.append(Paragraph("📋 STUDENT FEE DETAILS", section_header_style))
        
        if students_data:
            fee_data = [
                ['Student Name', 'Class', 'Term Fee', 'Paid', 'Balance', 'Status']
            ]
            
            for student in students_data:
                balance = float(student.get('current_balance', 0))
                if balance <= 0:
                    status = '✅ PAID'
                    status_color = colors.HexColor('#10b981')
                else:
                    status = '⏳ PENDING'
                    status_color = colors.HexColor('#f59e0b')
                
                fee_data.append([
                    student.get('name', 'N/A')[:25],
                    str(student.get('class', 'N/A'))[:8],
                    f"${float(student.get('term_fee', 0)):,.2f}",
                    f"${float(student.get('amount_paid', 0)):,.2f}",
                    f"${balance:,.2f}",
                    status
                ])
            
            fee_table = Table(fee_data, colWidths=[1.8*inch, 0.9*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.0*inch])
            
            # Build table style with status coloring
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a8c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
                ('ALIGN', (5, 1), (5, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (2, 1), (4, -1), 'Helvetica-Bold'),
                ('FONTNAME', (5, 1), (5, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]
            
            # Color code status cells
            for idx, student in enumerate(students_data, 1):
                balance = float(student.get('current_balance', 0))
                if balance <= 0:
                    table_style.append(('BACKGROUND', (5, idx), (5, idx), colors.HexColor('#d1fae5')))
                    table_style.append(('TEXTCOLOR', (5, idx), (5, idx), colors.HexColor('#065f46')))
                else:
                    table_style.append(('BACKGROUND', (5, idx), (5, idx), colors.HexColor('#fef3c7')))
                    table_style.append(('TEXTCOLOR', (5, idx), (5, idx), colors.HexColor('#78350f')))
            
            fee_table.setStyle(TableStyle(table_style))
            story.append(fee_table)
        
        # Footer
        story.append(Spacer(1, 0.2*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#a0aec0'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        story.append(Paragraph("This is an official financial report generated from the Academy Flow system. For inquiries, contact the school administration.", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer


class ArrearsReport:
    """Generate professional arrears reports"""
    
    @staticmethod
    def generate_arrears_pdf(students_with_arrears, term=None):
        """Generate arrears collection report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Add header
        subtitle = f"Academic Term: {term}" if term else "Outstanding Balance Summary"
        SchoolHeaderFooter.add_header(story, "Arrears Collection Report", subtitle)
        
        # ===== SUMMARY STATISTICS =====
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.white,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#dc2626'),
            borderPadding=8,
            leftIndent=4,
            rightIndent=4
        )
        story.append(Paragraph("📊 SUMMARY STATISTICS", section_header_style))
        
        total_arrears = sum(Decimal(str(s.get('balance', 0))) for s in students_with_arrears)
        num_students = len(students_with_arrears)
        avg_arrears = float(total_arrears) / num_students if num_students > 0 else 0
        
        # Create summary boxes
        summary_data = [
            ['Total Students with Arrears', str(num_students)],
            ['Total Outstanding Balance', f"${float(total_arrears):,.2f}"],
            ['Average Arrears per Student', f"${avg_arrears:,.2f}"],
            ['Report Generated', datetime.now().strftime('%B %d, %Y')],
        ]
        
        summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fee2e2')),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fecaca')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#7f1d1d')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#ef4444')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ===== STUDENTS WITH ARREARS =====
        story.append(Paragraph("⚠️ STUDENTS WITH OUTSTANDING BALANCES", section_header_style))
        
        if students_with_arrears:
            arrears_data = [
                ['Student Name', 'ID', 'Class', 'Outstanding Balance', 'Severity']
            ]
            
            for student_info in students_with_arrears:
                balance = float(student_info.get('balance', 0))
                
                # Determine severity
                if balance > 10000:
                    severity = '🔴 CRITICAL'
                    severity_bg = colors.HexColor('#fee2e2')
                elif balance > 5000:
                    severity = '🟠 HIGH'
                    severity_bg = colors.HexColor('#fed7aa')
                else:
                    severity = '🟡 MEDIUM'
                    severity_bg = colors.HexColor('#fef3c7')
                
                arrears_data.append([
                    student_info.get('name', 'Unknown')[:30],
                    str(student_info.get('id', 'N/A')),
                    str(student_info.get('current_class', 'N/A')),
                    f"${balance:,.2f}",
                    severity
                ])
            
            arrears_table = Table(arrears_data, colWidths=[1.8*inch, 0.9*inch, 1.0*inch, 1.5*inch, 1.3*inch])
            
            # Color alternating rows based on severity
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('ALIGN', (4, 1), (4, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
                ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('FONTSIZE', (4, 1), (4, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
            ]
            
            # Add background colors for severity
            for idx, student_info in enumerate(students_with_arrears, 1):
                balance = float(student_info.get('balance', 0))
                if balance > 10000:
                    table_style.append(('BACKGROUND', (4, idx), (4, idx), colors.HexColor('#fee2e2')))
                elif balance > 5000:
                    table_style.append(('BACKGROUND', (4, idx), (4, idx), colors.HexColor('#fed7aa')))
                else:
                    table_style.append(('BACKGROUND', (4, idx), (4, idx), colors.HexColor('#fef3c7')))
            
            arrears_table.setStyle(TableStyle(table_style))
            story.append(arrears_table)
        else:
            no_data_style = ParagraphStyle(
                'NoData',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#15803d'),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique',
                backColor=colors.HexColor('#f0fdf4'),
                borderPadding=16
            )
            story.append(Paragraph("✓ Excellent! No outstanding balances. All students are current with their fees.", no_data_style))
        
        # ===== COLLECTION NOTES =====
        story.append(Spacer(1, 0.2*inch))
        notes_header_style = ParagraphStyle(
            'NotesHeader',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=8,
            fontName='Helvetica-Bold',
        )
        story.append(Paragraph("📝 COLLECTION NOTES", notes_header_style))
        
        notes_style = ParagraphStyle(
            'Notes',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=4,
            fontName='Helvetica',
            leftIndent=0.1*inch
        )
        story.append(Paragraph("• <b>CRITICAL (Red):</b> Balance exceeds 10,000 - Immediate action required", notes_style))
        story.append(Paragraph("• <b>HIGH (Orange):</b> Balance between 5,000-10,000 - Priority follow-up needed", notes_style))
        story.append(Paragraph("• <b>MEDIUM (Yellow):</b> Balance under 5,000 - Regular follow-up recommended", notes_style))
        
        # Footer
        story.append(Spacer(1, 0.2*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#a0aec0'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        story.append(Paragraph("This is an official document from " + get_school_name() + ". For inquiries, contact the school administration.", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer


def create_pdf_response(pdf_buffer, filename):
    """Helper function to create HTTP response for PDF download"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf_buffer.getvalue())
    return response
