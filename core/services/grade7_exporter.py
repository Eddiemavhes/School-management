"""
Grade 7 Results Analysis Report PDF Exporter
Comprehensive academic analysis with data-driven recommendations
"""

from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, 
    HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class Grade7CompletionPDFExporter:
    """Comprehensive Grade 7 Results Analysis Report with Data-Driven Recommendations"""
    
    def __init__(self, school_name="School Name"):
        self.school_name = school_name
        
        # Premium Color Palette
        self.navy_blue = Color(30/255, 58/255, 138/255)      # #1E3A8A
        self.emerald_green = Color(5/255, 150/255, 105/255)  # #059669
        self.gold = Color(217/255, 119/255, 6/255)           # #D97706
        self.sky_blue = Color(14/255, 165/255, 233/255)      # #0EA5E9
        self.warm_gray = Color(107/255, 114/255, 128/255)    # #6B7280
        self.cream = Color(254/255, 243/255, 199/255)        # #FEF3C7
        self.white = Color(1, 1, 1)
        self.text_dark = Color(15/255, 23/255, 42/255)
        self.light_green = Color(236/255, 253/255, 245/255)
        self.light_red = Color(254/255, 242/255, 242/255)
        
        # Subtle backgrounds
        self.bg_light = Color(248/255, 250/255, 252/255)
        self.bg_lighter = Color(241/255, 245/255, 250/255)
        self.border_light = Color(226/255, 232/255, 240/255)
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
        # Subject list
        self.subjects = [
            'English',
            'Mathematics', 
            'General Science',
            'Social Studies',
            'Indigenous Language',
            'Agriculture'
        ]
    
    def _setup_styles(self):
        """Setup professional paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='Grade7CoverTitle',
            parent=self.styles['Heading1'],
            fontSize=42,
            textColor=self.navy_blue,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=48
        ))
        
        self.styles.add(ParagraphStyle(
            name='Grade7CoverSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.emerald_green,
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Grade7SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=20,
            textColor=self.white,
            spaceAfter=0,
            fontName='Helvetica-Bold',
            leading=24
        ))
        
        self.styles.add(ParagraphStyle(
            name='Grade7SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=15,
            textColor=self.navy_blue,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            leading=18
        ))
        
        self.styles.add(ParagraphStyle(
            name='Grade7BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.text_dark,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='Grade7HighlightText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.emerald_green,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
    
    def _create_section_header(self, title):
        """Create professional section header"""
        header_table = Table(
            [[Paragraph(title, self.styles['Grade7SectionHeader'])]], 
            colWidths=[7.2*inch]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.navy_blue),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, 0), (12, 8)),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ]))
        return header_table
    
    def _calculate_student_statistics(self, all_students):
        """Calculate overall statistics for all students"""
        total = len(all_students)
        
        # Count passes and failures for each student
        passed = 0
        failed = 0
        perfect_scores = 0
        
        for student in all_students:
            try:
                result = student.zimsec_results
            except:
                result = None
            
            if not result:
                continue
            
            # Get all subject scores
            scores = [
                result.english_units,
                result.mathematics_units,
                result.science_units,
                result.social_studies_units,
                result.indigenous_language_units,
                result.agriculture_units
            ]
            
            # Calculate aggregate (total units)
            aggregate = sum(s for s in scores if s is not None)
            
            # Count how many subjects have no failures (1-5 are passes, 6+ are failures)
            passed_subjects = sum(1 for s in scores if s and 1 <= s <= 5)
            
            # Student PASSES if aggregate < 36, FAILS if aggregate >= 36
            if aggregate < 36:
                passed += 1
                if passed_subjects == 6:  # All subjects passed
                    perfect_scores += 1
            else:
                failed += 1
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': pass_rate,
            'perfect_scores': perfect_scores,
            'perfect_percentage': (perfect_scores / total * 100) if total > 0 else 0
        }
    
    def _calculate_subject_statistics(self, all_students):
        """Calculate pass rates for each subject"""
        subject_stats = {}
        
        # Map subject names to ZimsecResults fields
        subject_fields = {
            'English': 'english_units',
            'Mathematics': 'mathematics_units',
            'General Science': 'science_units',
            'Social Studies': 'social_studies_units',
            'Indigenous Language': 'indigenous_language_units',
            'Agriculture': 'agriculture_units'
        }
        
        for subject, field_name in subject_fields.items():
            total = 0
            passed = 0
            
            for student in all_students:
                try:
                    result = student.zimsec_results
                    score = getattr(result, field_name, None)
                except:
                    score = None
                
                if score is not None:
                    total += 1
                    if 1 <= score <= 5:  # 1-5 is pass
                        passed += 1
            
            pass_rate = (passed / total * 100) if total > 0 else 0
            subject_stats[subject] = {
                'passed': passed,
                'failed': total - passed,
                'total': total,
                'pass_rate': pass_rate
            }
        
        return subject_stats
    
    def _calculate_class_statistics(self, classes_dict):
        """Calculate statistics per class"""
        class_stats = {}
        
        for class_name, students in classes_dict.items():
            total = len(students)
            passed = 0
            
            for student in students:
                try:
                    result = student.zimsec_results
                except:
                    result = None
                
                if result:
                    scores = [
                        result.english_units,
                        result.mathematics_units,
                        result.science_units,
                        result.social_studies_units,
                        result.indigenous_language_units,
                        result.agriculture_units
                    ]
                    # Calculate aggregate (total units)
                    aggregate = sum(s for s in scores if s is not None)
                    # Student PASSES if aggregate < 36
                    if aggregate < 36:
                        passed += 1
            
            pass_rate = (passed / total * 100) if total > 0 else 0
            class_stats[class_name] = {
                'total': total,
                'passed': passed,
                'failed': total - passed,
                'pass_rate': pass_rate
            }
        
        return class_stats
    
    def _get_achievement_distribution(self, all_students):
        """Categorize students by achievement level based on aggregate units"""
        passed = []  # aggregate < 36
        failed = []  # aggregate >= 36
        
        for student in all_students:
            try:
                result = student.zimsec_results
            except:
                result = None
            
            if not result:
                continue
            
            scores = [
                result.english_units,
                result.mathematics_units,
                result.science_units,
                result.social_studies_units,
                result.indigenous_language_units,
                result.agriculture_units
            ]
            
            # Calculate aggregate (total units)
            aggregate = sum(s for s in scores if s is not None)
            student_name = f"{student.surname}, {student.first_name}"
            
            # Student PASSES if aggregate < 36, FAILS if aggregate >= 36
            if aggregate < 36:
                passed.append(student_name)
            else:
                failed.append(student_name)
        
        return {
            'passed': passed,
            'failed': failed
        }
    
    def _get_subject_ranking(self, subject_stats):
        """Rank subjects by pass rate"""
        return sorted(
            subject_stats.items(),
            key=lambda x: x[1]['pass_rate'],
            reverse=True
        )
    
    def _generate_recommendations(self, subject_stats, class_stats, overall_stats):
        """Generate data-driven recommendations"""
        recommendations = {
            'immediate': [],
            'mid_term': [],
            'long_term': []
        }
        
        # Analyze mathematics and weak subjects
        weakest_subjects = sorted(
            subject_stats.items(),
            key=lambda x: x[1]['pass_rate']
        )[:2]
        
        for subject, stats in weakest_subjects:
            if stats['pass_rate'] < 80:
                recommendations['immediate'].append(
                    f"<b>{subject} Intervention:</b> Focus on improving {subject} teaching methods "
                    f"(current pass rate: {stats['pass_rate']:.1f}%)"
                )
        
        # Check class disparity
        class_list = list(class_stats.items())
        if len(class_list) > 1:
            class_list_sorted = sorted(class_list, key=lambda x: x[1]['pass_rate'])
            worst_class = class_list_sorted[0]
            best_class = class_list_sorted[-1]
            disparity = best_class[1]['pass_rate'] - worst_class[1]['pass_rate']
            
            if disparity > 15:
                recommendations['immediate'].append(
                    f"<b>{worst_class[0]} Support:</b> Investigate why {disparity:.1f}% performance gap exists "
                    f"({worst_class[1]['pass_rate']:.1f}% vs {best_class[1]['pass_rate']:.1f}%)"
                )
        
        # Long-term improvements
        best_subject = max(subject_stats.items(), key=lambda x: x[1]['pass_rate'])
        recommendations['long_term'].append(
            f"<b>Replicate Success:</b> Study {best_subject[0]} teaching methods "
            f"({best_subject[1]['pass_rate']:.1f}% success) for other subjects"
        )
        
        recommendations['long_term'].append(
            f"<b>Data Tracking System:</b> Implement regular assessment monitoring to identify "
            f"at-risk students earlier in the year"
        )
        
        return recommendations
    
    def _create_results_table(self, students_list, class_name):
        """Create detailed results table for a class"""
        # Header
        data = [['Student Name', 'English', 'Math', 'Science', 'Social Studies', 'Language', 'Agriculture', 'Aggregate', 'Status']]
        
        failed_students = []
        
        for student in students_list:
            try:
                result = student.zimsec_results
            except:
                result = None
            
            row = [f"{student.surname}, {student.first_name}"]
            total_units = 0
            
            # Map to subject fields in order
            scores = [
                result.english_units if result else None,
                result.mathematics_units if result else None,
                result.science_units if result else None,
                result.social_studies_units if result else None,
                result.indigenous_language_units if result else None,
                result.agriculture_units if result else None
            ]
            
            for score in scores:
                if score is not None:
                    row.append(str(score))
                    total_units += score
                else:
                    row.append('-')
            
            # Add aggregate
            row.append(str(total_units))
            
            # Student PASSES if aggregate < 36, FAILS if aggregate >= 36
            status = 'PASS' if total_units < 36 else 'FAIL'
            if status == 'FAIL':
                failed_students.append(f"{student.surname}, {student.first_name}")
            
            row.append(status)
            data.append(row)
        
        # Create table with better spacing
        table = Table(data, colWidths=[2.2*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.6*inch])
        
        # Style table - all left aligned
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.navy_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_light),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), (5, 3)),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.bg_lighter]),
        ]))
        
        return table, failed_students
    
    def export_to_buffer(self, students_by_class):
        """Generate comprehensive Grade 7 Results Analysis PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Flatten students for overall analysis
        all_students = []
        for students in students_by_class.values():
            all_students.extend(students)
        
        # ===== PAGE 1: TITLE & EXECUTIVE SUMMARY =====
        story.append(Spacer(1, 0.4*inch))
        story.append(Paragraph('ZIMSEC 2026 RESULTS', self.styles['Grade7CoverTitle']))
        story.append(Paragraph('COMPREHENSIVE ANALYSIS', self.styles['Grade7CoverTitle']))
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph(self.school_name, self.styles['Grade7CoverSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        report_date = datetime.now().strftime('%B %d, %Y')
        story.append(Paragraph(f'<b>Report Date:</b> {report_date}', self.styles['Grade7HighlightText']))
        story.append(Spacer(1, 0.4*inch))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(self._create_section_header('EXECUTIVE SUMMARY'))
        story.append(Spacer(1, 0.15*inch))
        
        # Calculate statistics
        overall_stats = self._calculate_student_statistics(all_students)
        subject_stats = self._calculate_subject_statistics(all_students)
        class_stats = self._calculate_class_statistics(students_by_class)
        
        # Summary metrics
        summary_data = [
            ['Total Students', f"{overall_stats['total']}"],
            ['Overall Pass Rate', f"{overall_stats['pass_rate']:.1f}% ({overall_stats['passed']}/{overall_stats['total']})"],
            ['Failed Students', f"{overall_stats['failed']} ({100-overall_stats['pass_rate']:.1f}%)"],
            ['Perfect Scores (All 6 Subjects)', f"{overall_stats['perfect_scores']} ({overall_stats['perfect_percentage']:.1f}%)"],
            ['Top Subject', max(subject_stats.items(), key=lambda x: x[1]['pass_rate'])[0]],
            ['Weakest Subject', min(subject_stats.items(), key=lambda x: x[1]['pass_rate'])[0]],
        ]
        
        summary_table = Table(summary_data, colWidths=[3.2*inch, 2.2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.bg_light),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_dark),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_light),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [self.white, self.bg_lighter]),
            ('PADDING', (0, 0), (-1, -1), (10, 8)),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        # ===== PAGES 2-3: STUDENT RESULTS BY CLASS =====
        first_class = True
        for class_name, students in students_by_class.items():
            if not first_class:
                story.append(PageBreak())
            first_class = False
            
            story.append(Spacer(1, 0.2*inch))
            stats = class_stats[class_name]
            header_text = f"{class_name} RESULTS ({len(students)} Students, {stats['pass_rate']:.0f}% Pass Rate)"
            story.append(self._create_section_header(header_text))
            story.append(Spacer(1, 0.15*inch))
            
            results_table, failed_in_class = self._create_results_table(students, class_name)
            story.append(results_table)
            
            if failed_in_class:
                story.append(Spacer(1, 0.15*inch))
                story.append(Paragraph('<b>FAILED STUDENTS:</b>', self.styles['Grade7SubsectionHeader']))
                story.append(Spacer(1, 0.05*inch))
                for i, student in enumerate(failed_in_class, 1):
                    story.append(Paragraph(f"{i}. {student}", self.styles['Grade7BodyText']))
        
        # ===== PAGE 4: SUBJECT PERFORMANCE ANALYSIS =====
        story.append(PageBreak())
        story.append(Spacer(1, 0.2*inch))
        story.append(self._create_section_header('SUBJECT PERFORMANCE ANALYSIS'))
        story.append(Spacer(1, 0.15*inch))
        
        # Subject ranking table
        subject_ranking = self._get_subject_ranking(subject_stats)
        subject_data = [['Subject', 'Pass Rate', 'Passed', 'Failed']]
        
        for rank, (subject, stats) in enumerate(subject_ranking, 1):
            subject_data.append([
                subject,
                f"{stats['pass_rate']:.1f}%",
                f"{stats['passed']}/{stats['total']}",
                f"{stats['failed']}/{stats['total']}",
            ])
        
        subject_table = Table(subject_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        subject_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.navy_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_light),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.bg_lighter]),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), (8, 6)),
        ]))
        story.append(subject_table)
        
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph('<b>KEY INSIGHTS:</b>', self.styles['Grade7SubsectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        best_subject = subject_ranking[0]
        worst_subject = subject_ranking[-1]
        
        analysis_text = f"""
        <b>• Strength:</b> {best_subject[0]} is the strongest subject with a {best_subject[1]['pass_rate']:.1f}% pass rate<br/>
        <b>• Challenge:</b> {worst_subject[0]} requires immediate attention with a {worst_subject[1]['pass_rate']:.1f}% pass rate<br/>
        <b>• Overall:</b> {len([s for s in subject_ranking if s[1]['pass_rate'] >= 77.5])}/6 subjects have pass rates above 77.5%
        """
        story.append(Paragraph(analysis_text, self.styles['Grade7BodyText']))
        
        # ===== PAGE 5: CLASS PERFORMANCE COMPARISON =====
        story.append(PageBreak())
        story.append(Spacer(1, 0.2*inch))
        story.append(self._create_section_header('CLASS PERFORMANCE COMPARISON'))
        story.append(Spacer(1, 0.15*inch))
        
        class_data = [['Class', 'Total Students', 'Passed', 'Failed', 'Pass Rate']]
        for class_name, stats in class_stats.items():
            class_data.append([
                class_name,
                str(stats['total']),
                str(stats['passed']),
                str(stats['failed']),
                f"{stats['pass_rate']:.0f}%"
            ])
        
        class_table = Table(class_data, colWidths=[1.8*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.2*inch])
        class_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.navy_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_light),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.bg_lighter]),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), (8, 6)),
        ]))
        story.append(class_table)
        
        story.append(Spacer(1, 0.25*inch))
        story.append(Paragraph('<b>PERFORMANCE INSIGHTS:</b>', self.styles['Grade7SubsectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        # Analyze class performance
        class_list = list(class_stats.items())
        class_list_sorted = sorted(class_list, key=lambda x: x[1]['pass_rate'], reverse=True)
        best_class = class_list_sorted[0]
        worst_class = class_list_sorted[-1]
        disparity = best_class[1]['pass_rate'] - worst_class[1]['pass_rate']
        
        class_analysis = f"""
        <b>• Best Performing:</b> {best_class[0]} with {best_class[1]['pass_rate']:.0f}% pass rate<br/>
        <b>• Needs Support:</b> {worst_class[0]} with {worst_class[1]['pass_rate']:.0f}% pass rate<br/>
        <b>• Performance Gap:</b> {disparity:.0f}% difference between best and worst performing classes
        """
        story.append(Paragraph(class_analysis, self.styles['Grade7BodyText']))
        
        # ===== PAGE 6: STUDENT ACHIEVEMENT LEVELS =====
        story.append(PageBreak())
        story.append(Spacer(1, 0.2*inch))
        story.append(self._create_section_header('STUDENT ACHIEVEMENT DISTRIBUTION'))
        story.append(Spacer(1, 0.15*inch))
        
        achievement = self._get_achievement_distribution(all_students)
        
        achievement_data = [
            ['Achievement Level', 'Students', 'Percentage', 'Notes'],
            ['PASS (< 36 Units)', str(len(achievement['passed'])), f"{len(achievement['passed'])/len(all_students)*100:.1f}%", 'Aggregate units below 36'],
            ['FAIL (≥ 36 Units)', str(len(achievement['failed'])), f"{len(achievement['failed'])/len(all_students)*100:.1f}%", 'Aggregate units 36 or above'],
        ]
        
        achievement_table = Table(achievement_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 2*inch])
        achievement_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.navy_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_light),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.white, self.bg_lighter]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), (6, 4)),
        ]))
        story.append(achievement_table)
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph('<b>STUDENTS WHO PASSED:</b>', self.styles['Grade7SubsectionHeader']))
        story.append(Spacer(1, 0.05*inch))
        
        if achievement['passed']:
            for i, student in enumerate(achievement['passed'][:20], 1):
                story.append(Paragraph(f"{i}. {student}", self.styles['Grade7BodyText']))
        else:
            story.append(Paragraph("No students passed.", self.styles['Grade7BodyText']))
        
        # ===== PAGE 7: RECOMMENDATIONS =====
        story.append(PageBreak())
        story.append(Spacer(1, 0.2*inch))
        story.append(self._create_section_header('RECOMMENDATIONS FOR SCHOOL IMPROVEMENT'))
        story.append(Spacer(1, 0.15*inch))
        
        recommendations = self._generate_recommendations(subject_stats, class_stats, overall_stats)
        
        story.append(Paragraph('<b>IMMEDIATE ACTIONS:</b>', self.styles['Grade7SubsectionHeader']))
        story.append(Spacer(1, 0.05*inch))
        for rec in recommendations['immediate']:
            story.append(Paragraph(rec, self.styles['Grade7BodyText']))
        
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph('<b>MID-TERM STRATEGIES:</b>', self.styles['Grade7SubsectionHeader']))
        story.append(Spacer(1, 0.05*inch))
        mid_term_text = f"""
        • <b>Subject Balance:</b> Maintain strength in {best_subject[0]} while improving {worst_subject[0]}<br/>
        • <b>Early Identification:</b> Implement systems to identify at-risk students earlier in the year<br/>
        • <b>Curriculum Review:</b> Evaluate why {worst_subject[0]} consistently underperforms
        """
        story.append(Paragraph(mid_term_text, self.styles['Grade7BodyText']))
        
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph('<b>LONG-TERM PLANNING:</b>', self.styles['Grade7SubsectionHeader']))
        story.append(Spacer(1, 0.05*inch))
        long_term_text = f"""
        • <b>Professional Development:</b> Train teachers in differentiated instruction<br/>
        • <b>Resource Allocation:</b> Ensure equal access to learning materials across all classes<br/>
        • <b>Data Tracking:</b> Implement regular assessment monitoring throughout the year
        """
        story.append(Paragraph(long_term_text, self.styles['Grade7BodyText']))
        
        # ===== PAGE 8: FINAL SUMMARY =====
        story.append(PageBreak())
        story.append(Spacer(1, 0.2*inch))
        story.append(self._create_section_header('FINAL SUMMARY & NEXT STEPS'))
        story.append(Spacer(1, 0.15*inch))
        
        story.append(Paragraph('<b>OVERALL PERFORMANCE:</b>', self.styles['Grade7SubsectionHeader']))
        story.append(Spacer(1, 0.05*inch))
        overall_text = f"""
        • <b>Positive:</b> {overall_stats['pass_rate']:.1f}% pass rate, {overall_stats['perfect_percentage']:.0f}% perfect scores<br/>
        • <b>Areas for Improvement:</b> {worst_subject[0]}, {worst_class[0]} performance
        """
        story.append(Paragraph(overall_text, self.styles['Grade7BodyText']))
        
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph('<b>PRIORITY AREAS FOR 2027:</b>', self.styles['Grade7SubsectionHeader']))
        story.append(Spacer(1, 0.05*inch))
        priority_text = f"""
        1. Raise {worst_subject[0]} pass rate from {worst_subject[1]['pass_rate']:.1f}% to at least 80%<br/>
        2. Eliminate the {disparity:.0f}% performance gap between classes<br/>
        3. Maintain {best_subject[0]} excellence while improving other subjects
        """
        story.append(Paragraph(priority_text, self.styles['Grade7BodyText']))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f'<b>Report Prepared:</b> {report_date}', self.styles['Grade7BodyText']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
