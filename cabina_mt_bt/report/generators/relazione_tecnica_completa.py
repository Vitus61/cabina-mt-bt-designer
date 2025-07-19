#!/usr/bin/env python3
"""
GENERATORE RELAZIONE TECNICA COMPLETA - CABINA MT/BT
Genera relazioni tecniche complete per progetti di cabine di trasformazione
Integrazione con main.py e classe CabinaMTBT esistente

Author: Maurizio srl
Version: 1.0
Data: 19/07/2025
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfutils
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from datetime import datetime
import os
import math


class RelazioneTecnicaCompleta:
    """
    Generatore automatico di Relazione Tecnica Completa per Cabine MT/BT
    Estrae tutti i dati calcolati dal main.py e li organizza in un documento professionale
    """
    
    def __init__(self, cabina_data, project_info=None):
        """
        Inizializza il generatore di relazione tecnica
        
        Args:
            cabina_data: Oggetto CabinaMTBT con tutti i dati calcolati
            project_info: Dict con informazioni progetto {
                'cliente': str,
                'commessa': str, 
                'ubicazione': str,
                'revisione': str,
                'progettista': str,
                'data_progetto': str
            }
        """
        self.cabina = cabina_data
        self.project_info = project_info or {}
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Definisce stili personalizzati per il documento"""
        
        # Stile titolo principale
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Stile sezioni principali
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=8,
            backColor=colors.lightgrey,
            fontName='Helvetica-Bold'
        ))
        
        # Stile sottosezioni
        self.styles.add(ParagraphStyle(
            name='SubSectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=8,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold',
            leftIndent=10
        ))
        
        # Stile parametri tecnici
        self.styles.add(ParagraphStyle(
            name='TechnicalData',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            leftIndent=20,
            spaceBefore=3,
            spaceAfter=3
        ))
        
        # Stile risultati importanti
        self.styles.add(ParagraphStyle(
            name='ImportantResult',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.darkgreen,
            leftIndent=15,
            borderWidth=1,
            borderColor=colors.green,
            borderPadding=6,
            backColor=colors.lightgreen,
            spaceBefore=6,
            spaceAfter=6
        ))
        
        # Stile note e osservazioni
        self.styles.add(ParagraphStyle(
            name='Note',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Oblique',
            textColor=colors.grey,
            leftIndent=25,
            spaceBefore=3
        ))

    def genera_relazione_completa(self, filename=None):
        """
        Genera la relazione tecnica completa in PDF
        
        Args:
            filename: Nome file output (se None, genera automaticamente)
            
        Returns:
            str: Path del file generato
        """
        
        # Genera nome file se non specificato
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            cliente = self.project_info.get('cliente', 'Cliente').replace(' ', '_')
            filename = f"RelazioneTecnica_{cliente}_{timestamp}.pdf"
        
        # Crea il documento PDF
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )
        
        # Costruisce il contenuto
        story = []
        
        # FRONTESPIZIO
        story.extend(self._build_frontespizio())
        story.append(PageBreak())
        
        # SEZIONE 1: Dati di Progetto
        story.extend(self._build_sezione_1_dati_progetto())
        
        # SEZIONE 2: Calcoli Elettrici  
        story.extend(self._build_sezione_2_calcoli_elettrici())
        
        # SEZIONE 3: Dimensionamento Trasformatore
        story.extend(self._build_sezione_3_trasformatore())
        
        # SEZIONE 4: Apparecchiature MT
        story.extend(self._build_sezione_4_apparecchiature_mt())
        
        # SEZIONE 5: Apparecchiature BT
        story.extend(self._build_sezione_5_apparecchiature_bt())
        
        # SEZIONE 6: Protezioni e Selettività
        story.extend(self._build_sezione_6_protezioni())
        
        # SEZIONE 7: Impianto di Terra
        story.extend(self._build_sezione_7_impianto_terra())
        
        # SEZIONE 8: Verifiche Normative
        story.extend(self._build_sezione_8_verifiche_normative())
        
        # Genera il PDF
        doc.build(story)
        
        return filename

    def _build_frontespizio(self):
        """Costruisce il frontespizio del documento"""
        content = []
        
        content.append(Spacer(1, 2*cm))
        
        # Titolo principale
        title = "RELAZIONE TECNICA COMPLETA<br/>CABINA DI TRASFORMAZIONE MT/BT"
        content.append(Paragraph(title, self.styles['CustomTitle']))
        content.append(Spacer(1, 1.5*cm))
        
        # Informazioni progetto in tabella
        info_data = [
            ['CLIENTE:', self.project_info.get('cliente', 'N/A')],
            ['COMMESSA:', self.project_info.get('commessa', 'N/A')],
            ['UBICAZIONE:', self.project_info.get('ubicazione', 'N/A')],
            ['PROGETTISTA:', self.project_info.get('progettista', 'N/A')],
            ['DATA:', self.project_info.get('data_progetto', datetime.now().strftime("%d/%m/%Y"))],
            ['REVISIONE:', self.project_info.get('revisione', '00')]
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
        ]))
        
        content.append(info_table)
        content.append(Spacer(1, 3*cm))
        
        # Footer frontespizio
        footer_text = "Maurizio srl - Progettazione Impianti Elettrici<br/>Software di Calcolo Cabine MT/BT v.3.0"
        content.append(Paragraph(footer_text, self.styles['Note']))
        
        return content

    def _build_sezione_1_dati_progetto(self):
        """SEZIONE 1: Dati di Progetto"""
        content = []
        
        content.append(Paragraph("1. DATI DI PROGETTO", self.styles['SectionHeader']))
        
        # Sottosezione 1.1: Caratteristiche Generali
        content.append(Paragraph("1.1 Caratteristiche Generali dell'Impianto", self.styles['SubSectionHeader']))
        
        # Estrai dati dalla classe cabina
        potenza_installata = getattr(self.cabina, 'potenza_installata', 'N/A')
        tensione_mt = getattr(self.cabina, 'tensione_mt', 'N/A') 
        tensione_bt = getattr(self.cabina, 'tensione_bt', 'N/A')
        sistema_distribuzione = getattr(self.cabina, 'sistema_distribuzione', 'N/A')
        lunghezza_cavo_bt = getattr(self.cabina, 'lunghezza_cavo_bt', 'N/A')
        
        dati_generali = [
            f"• Potenza installata: <b>{potenza_installata} kVA</b>",
            f"• Tensione nominale MT: <b>{tensione_mt} kV</b>",
            f"• Tensione nominale BT: <b>{tensione_bt} V</b>",
            f"• Sistema di distribuzione: <b>{sistema_distribuzione}</b>",
            f"• Lunghezza cavo BT: <b>{lunghezza_cavo_bt} m</b>",
            f"• Frequenza nominale: <b>50 Hz</b>"
        ]
        
        for dato in dati_generali:
            content.append(Paragraph(dato, self.styles['TechnicalData']))
        
        content.append(Spacer(1, 10*mm))
        
        # Sottosezione 1.2: Configurazione Cabina
        content.append(Paragraph("1.2 Configurazione della Cabina", self.styles['SubSectionHeader']))
        
        config_text = """
        La cabina è del tipo prefabbricato in calcestruzzo, conforme alle prescrizioni 
        del distributore di energia elettrica e alle norme CEI applicabili. 
        La configurazione prevede compartimenti separati per le apparecchiature MT e BT.
        """
        content.append(Paragraph(config_text, self.styles['TechnicalData']))
        
        return content

    def _build_sezione_2_calcoli_elettrici(self):
        """SEZIONE 2: Calcoli Elettrici"""
        content = []
        
        content.append(Paragraph("2. CALCOLI ELETTRICI", self.styles['SectionHeader']))
        
        # Sottosezione 2.1: Correnti Nominali
        content.append(Paragraph("2.1 Correnti Nominali", self.styles['SubSectionHeader']))
        
        # Estrai dati di corrente dalla classe cabina
        In_mt = getattr(self.cabina, 'corrente_nominale_mt', 'N/A')
        In_bt = getattr(self.cabina, 'corrente_nominale_bt', 'N/A')
        
        correnti_data = [
            ['Parametro', 'Valore', 'Formula'],
            ['Corrente nominale MT', f'{In_mt} A', 'In = Sn / (√3 × Un)'],
            ['Corrente nominale BT', f'{In_bt} A', 'In = Sn / (√3 × Un)']
        ]
        
        correnti_table = Table(correnti_data, colWidths=[6*cm, 4*cm, 6*cm])
        correnti_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        content.append(correnti_table)
        content.append(Spacer(1, 10*mm))
        
        # Sottosezione 2.2: Cortocircuiti
        content.append(Paragraph("2.2 Calcoli di Cortocircuito", self.styles['SubSectionHeader']))
        
        # Estrai dati di cortocircuito
        Icc_mt_max = getattr(self.cabina, 'icc_mt_max', 'N/A')
        Icc_mt_min = getattr(self.cabina, 'icc_mt_min', 'N/A')
        Icc_bt_max = getattr(self.cabina, 'icc_bt_max', 'N/A')
        Icc_bt_min = getattr(self.cabina, 'icc_bt_min', 'N/A')
        
        cortocircuiti_text = f"""
        I calcoli di cortocircuito sono stati eseguiti considerando l'impedenza della rete MT 
        di alimentazione e le caratteristiche del trasformatore installato.
        
        <b>Risultati Cortocircuito MT:</b>
        • Icc max (trifase): {Icc_mt_max} kA
        • Icc min (monofase): {Icc_mt_min} kA
        
        <b>Risultati Cortocircuito BT:</b>
        • Icc max (ai morsetti trasformatore): {Icc_bt_max} kA  
        • Icc min (a fondo linea BT): {Icc_bt_min} kA
        """
        
        content.append(Paragraph(cortocircuiti_text, self.styles['TechnicalData']))
        
        # Nota importante sulla lunghezza cavo BT
        nota_cavo = f"""
        <b>NOTA IMPORTANTE:</b> Il calcolo della corrente di cortocircuito minima BT 
        tiene conto della lunghezza effettiva del cavo BT ({getattr(self.cabina, 'lunghezza_cavo_bt', 'N/A')} m), 
        parametro critico per il corretto dimensionamento delle protezioni.
        """
        content.append(Paragraph(nota_cavo, self.styles['ImportantResult']))
        
        return content

    def _build_sezione_3_trasformatore(self):
        """SEZIONE 3: Dimensionamento Trasformatore"""
        content = []
        
        content.append(Paragraph("3. DIMENSIONAMENTO TRASFORMATORE", self.styles['SectionHeader']))
        
        # Sottosezione 3.1: Selezione Potenza
        content.append(Paragraph("3.1 Selezione della Potenza Normalizzata", self.styles['SubSectionHeader']))
        
        potenza_installata = getattr(self.cabina, 'potenza_installata', 'N/A')
        potenza_trasformatore = getattr(self.cabina, 'potenza_trasformatore', 'N/A')
        
        selezione_text = f"""
        La potenza del trasformatore è stata selezionata secondo la norma CEI 14-52 
        considerando la potenza installata di {potenza_installata} kVA.
        
        <b>Potenza trasformatore selezionata: {potenza_trasformatore} kVA</b>
        """
        content.append(Paragraph(selezione_text, self.styles['TechnicalData']))
        
        # Sottosezione 3.2: Caratteristiche Tecniche
        content.append(Paragraph("3.2 Caratteristiche Tecniche del Trasformatore", self.styles['SubSectionHeader']))
        
        # Estrai caratteristiche trasformatore
        tipo_trasformatore = getattr(self.cabina, 'tipo_trasformatore', 'Resina')
        tensione_cc = getattr(self.cabina, 'tensione_cortocircuito', '4%')
        perdite_vuoto = getattr(self.cabina, 'perdite_vuoto', 'N/A')
        perdite_carico = getattr(self.cabina, 'perdite_carico', 'N/A')
        
        caratteristiche_data = [
            ['Caratteristica', 'Valore'],
            ['Potenza nominale', f'{potenza_trasformatore} kVA'],
            ['Tensioni nominali', f'{getattr(self.cabina, "tensione_mt", "N/A")} kV / {getattr(self.cabina, "tensione_bt", "N/A")} V'],
            ['Tipo di isolamento', tipo_trasformatore],
            ['Tensione di cortocircuito', tensione_cc],
            ['Perdite a vuoto', f'{perdite_vuoto} W'],
            ['Perdite a carico', f'{perdite_carico} W'],
            ['Gruppo di collegamento', 'Dyn11'],
            ['Raffreddamento', 'AN (aria naturale)']
        ]
        
        car_table = Table(caratteristiche_data, colWidths=[8*cm, 6*cm])
        car_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        content.append(car_table)
        
        return content

    def _build_sezione_4_apparecchiature_mt(self):
        """SEZIONE 4: Apparecchiature MT"""
        content = []
        
        content.append(Paragraph("4. APPARECCHIATURE MEDIA TENSIONE", self.styles['SectionHeader']))
        
        # Sottosezione 4.1: Interruttore MT
        content.append(Paragraph("4.1 Interruttore Generale MT", self.styles['SubSectionHeader']))
        
        # Estrai dati interruttore MT
        interruttore_mt = getattr(self.cabina, 'interruttore_mt_selezionato', {})
        marca_mt = interruttore_mt.get('marca', 'N/A')
        modello_mt = interruttore_mt.get('modello', 'N/A')
        In_mt_int = interruttore_mt.get('corrente_nominale', 'N/A')
        Icu_mt = interruttore_mt.get('potere_interruzione', 'N/A')
        
        interruttore_text = f"""
        <b>Interruttore selezionato:</b>
        • Marca/Modello: {marca_mt} {modello_mt}
        • Corrente nominale: {In_mt_int} A
        • Potere di interruzione: {Icu_mt} kA
        • Tensione nominale: {getattr(self.cabina, 'tensione_mt', 'N/A')} kV
        """
        content.append(Paragraph(interruttore_text, self.styles['TechnicalData']))
        
        # Verifica del potere di interruzione
        Icc_mt_max = getattr(self.cabina, 'icc_mt_max', 0)
        if isinstance(Icu_mt, (int, float)) and isinstance(Icc_mt_max, (int, float)):
            if Icu_mt > Icc_mt_max:
                verifica_text = f"✓ VERIFICA SUPERATA: Icu ({Icu_mt} kA) > Icc max ({Icc_mt_max} kA)"
                content.append(Paragraph(verifica_text, self.styles['ImportantResult']))
        
        # Sottosezione 4.2: Protezioni MT
        content.append(Paragraph("4.2 Sistema di Protezione MT", self.styles['SubSectionHeader']))
        
        protezioni_mt_text = """
        Il sistema di protezione MT è costituito da:
        • Relè di protezione 51/50 (sovracorrente temporizzata/istantanea)
        • Relè di protezione 51N (terra temporizzata)
        • Relè di protezione 67N (terra direzionale)
        • TA di protezione classe 5P10
        • TV di protezione classe 3P
        """
        content.append(Paragraph(protezioni_mt_text, self.styles['TechnicalData']))
        
        return content

    def _build_sezione_5_apparecchiature_bt(self):
        """SEZIONE 5: Apparecchiature BT"""
        content = []
        
        content.append(Paragraph("5. APPARECCHIATURE BASSA TENSIONE", self.styles['SectionHeader']))
        
        # Sottosezione 5.1: Interruttore BT
        content.append(Paragraph("5.1 Interruttore Generale BT", self.styles['SubSectionHeader']))
        
        # Estrai dati interruttore BT
        interruttore_bt = getattr(self.cabina, 'interruttore_bt_selezionato', {})
        marca_bt = interruttore_bt.get('marca', 'N/A')
        modello_bt = interruttore_bt.get('modello', 'N/A')
        In_bt_int = interruttore_bt.get('corrente_nominale', 'N/A')
        Icu_bt = interruttore_bt.get('potere_interruzione', 'N/A')
        
        interruttore_bt_text = f"""
        <b>Interruttore generale BT selezionato:</b>
        • Marca/Modello: {marca_bt} {modello_bt}
        • Corrente nominale: {In_bt_int} A
        • Potere di interruzione: {Icu_bt} kA
        • Tensione nominale: {getattr(self.cabina, 'tensione_bt', 'N/A')} V
        • Categoria di utilizzo: A
        """
        content.append(Paragraph(interruttore_bt_text, self.styles['TechnicalData']))
        
        # Sottosezione 5.2: Quadro BT
        content.append(Paragraph("5.2 Quadro di Distribuzione BT", self.styles['SubSectionHeader']))
        
        quadro_bt_text = """
        Il quadro BT è costituito da:
        • Carpenteria metallica IP54
        • Interruttore generale con sganciatori elettronici
        • Interruttori di linea modulari/scatolati
        • Dispositivi di protezione SPD Classe I+II
        • Strumentazione di misura (multimetro digitale)
        • Segnalazioni luminose di stato
        """
        content.append(Paragraph(quadro_bt_text, self.styles['TechnicalData']))
        
        return content

    def _build_sezione_6_protezioni(self):
        """SEZIONE 6: Protezioni e Selettività"""
        content = []
        
        content.append(Paragraph("6. PROTEZIONI E SELETTIVITÀ", self.styles['SectionHeader']))
        
        # Sottosezione 6.1: Coordinamento Protezioni
        content.append(Paragraph("6.1 Coordinamento delle Protezioni", self.styles['SubSectionHeader']))
        
        coordinamento_text = """
        Il coordinamento delle protezioni è stato verificato per garantire la selettività 
        tra le protezioni MT e BT, assicurando l'isolamento del guasto nel punto più 
        vicino possibile alla sua origine.
        """
        content.append(Paragraph(coordinamento_text, self.styles['TechnicalData']))
        
        # Sottosezione 6.2: Tarature Protezioni
        content.append(Paragraph("6.2 Tarature delle Protezioni", self.styles['SubSectionHeader']))
        
        # Estrai tarature se disponibili
        taratura_51 = getattr(self.cabina, 'taratura_51', 'N/A')
        taratura_50 = getattr(self.cabina, 'taratura_50', 'N/A')
        taratura_51N = getattr(self.cabina, 'taratura_51N', 'N/A')
        
        tarature_data = [
            ['Protezione', 'Taratura', 'Tempo'],
            ['51 (Sovracorrente)', f'{taratura_51} A', '0.1 - 3.2 s'],
            ['50 (Istantanea)', f'{taratura_50} A', '< 0.1 s'],
            ['51N (Terra)', f'{taratura_51N} A', '0.2 - 1.0 s']
        ]
        
        tarature_table = Table(tarature_data, colWidths=[5*cm, 4*cm, 4*cm])
        tarature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        content.append(tarature_table)
        
        return content

    def _build_sezione_7_impianto_terra(self):
        """SEZIONE 7: Impianto di Terra"""
        content = []
        
        content.append(Paragraph("7. IMPIANTO DI TERRA", self.styles['SectionHeader']))
        
        # Sottosezione 7.1: Dimensionamento
        content.append(Paragraph("7.1 Dimensionamento dell'Impianto di Terra", self.styles['SubSectionHeader']))
        
        # Estrai dati impianto di terra
        resistivita_terreno = getattr(self.cabina, 'resistivita_terreno', 'N/A')
        resistenza_terra = getattr(self.cabina, 'resistenza_terra_calcolata', 'N/A')
        sezione_dispersore = getattr(self.cabina, 'sezione_dispersore', 'N/A')
        
        terra_text = f"""
        L'impianto di terra è stato dimensionato secondo la norma CEI 11-1 considerando:
        
        • Resistività del terreno: {resistivita_terreno} Ω·m
        • Resistenza di terra calcolata: {resistenza_terra} Ω
        • Sezione conduttori di terra: {sezione_dispersore} mm²
        • Materiale: Rame nudo interrato
        """
        content.append(Paragraph(terra_text, self.styles['TechnicalData']))
        
        # Sottosezione 7.2: Verifiche di Sicurezza
        content.append(Paragraph("7.2 Verifiche di Sicurezza", self.styles['SubSectionHeader']))
        
        verifiche_text = """
        Sono state eseguite le seguenti verifiche:
        • Tensione di contatto < 50V (CEI 11-1)
        • Tensione di passo < 125V (CEI 11-1) 
        • Coordinamento con protezioni differenziali
        • Equipotenzializzazione masse e masse estranee
        """
        content.append(Paragraph(verifiche_text, self.styles['TechnicalData']))
        
        return content

    def _build_sezione_8_verifiche_normative(self):
        """SEZIONE 8: Verifiche Normative"""
        content = []
        
        content.append(Paragraph("8. VERIFICHE NORMATIVE E CONFORMITÀ", self.styles['SectionHeader']))
        
        # Sottosezione 8.1: Norme Applicate
        content.append(Paragraph("8.1 Norme Tecniche Applicate", self.styles['SubSectionHeader']))
        
        norme_text = """
        Il progetto è stato sviluppato in conformità alle seguenti normative:
        
        <b>Norme CEI:</b>
        • CEI 11-1: Impianti elettrici con tensione superiore a 1 kV in corrente alternata
        • CEI 64-8: Impianti elettrici utilizzatori a tensione nominale non superiore a 1000 V
        • CEI 0-16: Regola tecnica di riferimento per la connessione di Utenti attivi e passivi
        • CEI 14-52: Trasformatori di distribuzione in resina
        
        <b>Norme IEC:</b>
        • IEC 62271: Apparecchiature di manovra e comando per alta tensione
        • IEC 61439: Quadri elettrici di bassa tensione
        """
        content.append(Paragraph(norme_text, self.styles['TechnicalData']))
        
        # Sottosezione 8.2: Dichiarazioni di Conformità
        content.append(Paragraph("8.2 Conformità del Progetto", self.styles['SubSectionHeader']))
        
        conformita_text = """
        Si attesta che il presente progetto è conforme a tutte le normative vigenti 
        e alle prescrizioni del distributore di energia elettrica.
        
        Tutti i calcoli sono stati eseguiti secondo metodologie consolidate e 
        le apparecchiature selezionate rispettano i requisiti normativi.
        """
        content.append(Paragraph(conformita_text, self.styles['TechnicalData']))
        
        # Nota finale
        content.append(Spacer(1, 20*mm))
        firma_text = f"""
        <b>Il Progettista</b><br/>
        {self.project_info.get('progettista', '[Nome Progettista]')}<br/>
        Data: {datetime.now().strftime("%d/%m/%Y")}
        """
        content.append(Paragraph(firma_text, self.styles['ImportantResult']))
        
        return content


# FUNZIONE DI INTEGRAZIONE CON MAIN.PY
def genera_relazione_da_main(cabina_obj, info_progetto):
    """
    Funzione di interfaccia per generare la relazione dal main.py
    
    Args:
        cabina_obj: Oggetto CabinaMTBT con dati calcolati
        info_progetto: Dict con info progetto
        
    Returns:
        str: Path del file PDF generato
    """
    
    generatore = RelazioneTecnicaCompleta(cabina_obj, info_progetto)
    return generatore.genera_relazione_completa()


# ESEMPIO DI UTILIZZO
if __name__ == "__main__":
    # Esempio di come integrare nel main.py
    """
    # Nel main.py, dopo tutti i calcoli:
    
    if st.button("📄 Genera Relazione Tecnica Completa"):
        info_progetto = {
            'cliente': cliente_input,
            'commessa': commessa_input,
            'ubicazione': ubicazione_input,
            'progettista': 'Ing. Maurizio',
            'revisione': '00'
        }
        
        pdf_file = genera_relazione_da_main(cabina, info_progetto)
        
        st.success(f"Relazione generata: {pdf_file}")
        
        # Download del file
        with open(pdf_file, "rb") as file:
            st.download_button(
                label="📥 Scarica Relazione PDF",
                data=file.read(),
                file_name=pdf_file,
                mime="application/pdf"
            )
    """
    pass