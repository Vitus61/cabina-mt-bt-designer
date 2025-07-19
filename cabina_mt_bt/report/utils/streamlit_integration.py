#!/usr/bin/env python3
"""
INTEGRAZIONE STREAMLIT - REPORT GENERATOR
Modulo per integrare la generazione di report nel main.py esistente

Author: Maurizio srl
Version: 1.0
Data: 19/07/2025
"""

import streamlit as st
import os
from datetime import datetime
import tempfile

# Import del generatore di report (da inserire nella cartella report/generators/)
from report.generators.relazione_tecnica_completa import RelazioneTecnicaCompleta, genera_relazione_da_main


def interfaccia_report_sidebar(cabina_obj=None):
    """
    Aggiunge l'interfaccia per i report nella sidebar di Streamlit
    
    Args:
        cabina_obj: Oggetto CabinaMTBT con dati calcolati
    """
    
    st.sidebar.markdown("---")
    st.sidebar.header("📊 GENERAZIONE REPORT")
    
    # Controllo se ci sono dati calcolati
    if cabina_obj is None:
        st.sidebar.warning("⚠️ Eseguire prima i calcoli della cabina")
        return
    
    # Controllo se ci sono dati validi
    if not hasattr(cabina_obj, 'potenza_trasformatore') or cabina_obj.potenza_trasformatore is None:
        st.sidebar.warning("⚠️ Dati di calcolo non disponibili")
        return
    
    # Sezione informazioni progetto
    with st.sidebar.expander("📋 Informazioni Progetto", expanded=False):
        info_progetto = {}
        
        info_progetto['cliente'] = st.text_input(
            "Cliente:", 
            value="", 
            key="report_cliente",
            help="Nome del cliente o azienda"
        )
        
        info_progetto['commessa'] = st.text_input(
            "Commessa:", 
            value="", 
            key="report_commessa",
            help="Numero commessa o codice progetto"
        )
        
        info_progetto['ubicazione'] = st.text_input(
            "Ubicazione:", 
            value="", 
            key="report_ubicazione",
            help="Località di installazione della cabina"
        )
        
        info_progetto['progettista'] = st.text_input(
            "Progettista:", 
            value="Ing. Maurizio", 
            key="report_progettista",
            help="Nome del progettista responsabile"
        )
        
        info_progetto['revisione'] = st.selectbox(
            "Revisione:",
            options=["00", "01", "02", "03", "04", "05"],
            index=0,
            key="report_revisione",
            help="Numero di revisione del documento"
        )
        
        info_progetto['data_progetto'] = datetime.now().strftime("%d/%m/%Y")
    
    # Pulsante di generazione
    if st.sidebar.button("📄 Genera Relazione Tecnica Completa", key="genera_report_btn"):
        genera_relazione_completa(cabina_obj, info_progetto)


def interfaccia_report_main_area(cabina_obj=None):
    """
    Interfaccia completa per i report nell'area principale
    Da usare come tab separato o sezione dedicata
    
    Args:
        cabina_obj: Oggetto CabinaMTBT con dati calcolati
    """
    
    st.header("📊 GENERAZIONE REPORT TECNICI")
    
    # Controllo prerequisiti
    if cabina_obj is None:
        st.error("⚠️ Nessun dato di calcolo disponibile. Eseguire prima i calcoli della cabina.")
        return
    
    if not hasattr(cabina_obj, 'potenza_trasformatore') or cabina_obj.potenza_trasformatore is None:
        st.error("⚠️ Dati di calcolo incompleti. Verificare i parametri di input.")
        return
    
    # Anteprima dei dati calcolati
    with st.expander("👁️ Anteprima Dati Calcolati", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Potenza Trasformatore", f"{getattr(cabina_obj, 'potenza_trasformatore', 'N/A')} kVA")
            st.metric("Tensione MT", f"{getattr(cabina_obj, 'tensione_mt', 'N/A')} kV")
            st.metric("Corrente Nominale MT", f"{getattr(cabina_obj, 'corrente_nominale_mt', 'N/A')} A")
        
        with col2:
            st.metric("Tensione BT", f"{getattr(cabina_obj, 'tensione_bt', 'N/A')} V")
            st.metric("Corrente Nominale BT", f"{getattr(cabina_obj, 'corrente_nominale_bt', 'N/A')} A")
            st.metric("Icc BT Max", f"{getattr(cabina_obj, 'icc_bt_max', 'N/A')} kA")
    
    st.markdown("---")
    
    # Sezione informazioni progetto
    st.subheader("📋 Informazioni del Progetto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cliente = st.text_input("Cliente *", help="Nome del cliente o azienda")
        commessa = st.text_input("Commessa *", help="Numero commessa o codice progetto")
        ubicazione = st.text_input("Ubicazione *", help="Località di installazione")
    
    with col2:
        progettista = st.text_input("Progettista", value="Ing. Maurizio", help="Nome del progettista responsabile")
        revisione = st.selectbox("Revisione", options=["00", "01", "02", "03", "04", "05"], help="Numero di revisione del documento")
        data_progetto = st.date_input("Data Progetto", value=datetime.now().date())
    
    # Controllo campi obbligatori
    campi_obbligatori = [cliente, commessa, ubicazione]
    campi_validi = all(campo.strip() for campo in campi_obbligatori)
    
    if not campi_validi:
        st.warning("⚠️ Compilare tutti i campi obbligatori (*)")
    
    st.markdown("---")
    
    # Sezione opzioni di generazione
    st.subheader("⚙️ Opzioni di Generazione")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_copertina = st.checkbox("Includi copertina", value=True)
        include_calcoli_dettagli = st.checkbox("Includi calcoli dettagliati", value=True)
    
    with col2:
        formato_numeri = st.selectbox("Formato numeri", ["2 decimali", "3 decimali", "Automatico"])
        lingua_report = st.selectbox("Lingua", ["Italiano", "Inglese"])
    
    st.markdown("---")
    
    # Pulsante di generazione
    if st.button("🚀 GENERA RELAZIONE TECNICA COMPLETA", disabled=not campi_validi, type="primary"):
        
        info_progetto = {
            'cliente': cliente,
            'commessa': commessa,
            'ubicazione': ubicazione,
            'progettista': progettista,
            'revisione': revisione,
            'data_progetto': data_progetto.strftime("%d/%m/%Y")
        }
        
        genera_relazione_completa(cabina_obj, info_progetto)


def genera_relazione_completa(cabina_obj, info_progetto):
    """
    Genera la relazione tecnica completa e gestisce il download
    
    Args:
        cabina_obj: Oggetto CabinaMTBT
        info_progetto: Dict con informazioni progetto
    """
    
    try:
        # Mostra progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Inizializzazione
        status_text.text("🔄 Inizializzazione generatore report...")
        progress_bar.progress(20)
        
        # Step 2: Estrazione dati
        status_text.text("📊 Estrazione dati di calcolo...")
        progress_bar.progress(40)
        
        # Step 3: Generazione PDF
        status_text.text("📄 Generazione documento PDF...")
        progress_bar.progress(60)
        
        # Genera il file usando il generatore
        pdf_file = genera_relazione_da_main(cabina_obj, info_progetto)
        
        progress_bar.progress(80)
        status_text.text("✅ Finalizzazione documento...")
        
        # Step 4: Preparazione download
        progress_bar.progress(100)
        status_text.text("🎉 Relazione generata con successo!")
        
        # Rimuovi progress bar dopo completamento
        progress_bar.empty()
        status_text.empty()
        
        # Messaggio di successo
        st.success(f"✅ Relazione tecnica generata con successo!")
        
        # Informazioni sul file generato
        file_size = os.path.getsize(pdf_file) / 1024  # KB
        st.info(f"📁 File generato: `{os.path.basename(pdf_file)}` ({file_size:.1f} KB)")
        
        # Pulsante di download
        with open(pdf_file, "rb") as file:
            pdf_data = file.read()
            
            st.download_button(
                label="📥 Scarica Relazione PDF",
                data=pdf_data,
                file_name=os.path.basename(pdf_file),
                mime="application/pdf",
                type="primary"
            )
        
        # Opzioni aggiuntive
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Genera Nuova Relazione"):
                st.rerun()
        
        with col2:
            if st.button("👁️ Anteprima Contenuto"):
                mostra_anteprima_contenuto(cabina_obj, info_progetto)
        
        # Cleanup: rimuovi file temporaneo dopo il download
        try:
            os.remove(pdf_file)
        except:
            pass  # File potrebbe essere già stato rimosso
            
    except Exception as e:
        st.error(f"❌ Errore durante la generazione del report: {str(e)}")
        st.exception(e)


def mostra_anteprima_contenuto(cabina_obj, info_progetto):
    """
    Mostra un'anteprima del contenuto che sarà incluso nel report
    
    Args:
        cabina_obj: Oggetto CabinaMTBT
        info_progetto: Dict con informazioni progetto
    """
    
    with st.expander("👁️ Anteprima Contenuto Report", expanded=True):
        
        st.markdown("### 📋 Sezioni del Report:")
        
        sezioni = [
            "1. Dati di Progetto",
            "2. Calcoli Elettrici", 
            "3. Dimensionamento Trasformatore",
            "4. Apparecchiature MT",
            "5. Apparecchiature BT",
            "6. Protezioni e Selettività",
            "7. Impianto di Terra",
            "8. Verifiche Normative"
        ]
        
        for sezione in sezioni:
            st.markdown(f"✅ {sezione}")
        
        st.markdown("### 📊 Dati Principali:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Cliente:** {info_progetto.get('cliente', 'N/A')}")
            st.markdown(f"**Commessa:** {info_progetto.get('commessa', 'N/A')}")
            st.markdown(f"**Ubicazione:** {info_progetto.get('ubicazione', 'N/A')}")
        
        with col2:
            st.markdown(f"**Potenza:** {getattr(cabina_obj, 'potenza_trasformatore', 'N/A')} kVA")
            st.markdown(f"**Tensioni:** {getattr(cabina_obj, 'tensione_mt', 'N/A')} kV / {getattr(cabina_obj, 'tensione_bt', 'N/A')} V")
            st.markdown(f"**Data:** {info_progetto.get('data_progetto', 'N/A')}")


# FUNZIONI DI UTILITÀ PER INTEGRAZIONE NEL MAIN.PY

def aggiungi_tab_report(cabina_obj):
    """
    Aggiunge un tab dedicato ai report nell'interfaccia principale
    
    Usage nel main.py:
    
    tab1, tab2, tab3, tab_report = st.tabs(["Calcoli", "Risultati", "Apparecchiature", "📊 Report"])
    
    with tab_report:
        aggiungi_tab_report(cabina)
    """
    interfaccia_report_main_area(cabina_obj)


def aggiungi_sezione_report(cabina_obj):
    """
    Aggiunge una sezione report alla fine della pagina principale
    
    Usage nel main.py:
    
    # Alla fine del main.py, dopo tutti i calcoli
    st.markdown("---")
    aggiungi_sezione_report(cabina)
    """
    st.markdown("## 📊 GENERAZIONE REPORT")
    interfaccia_report_main_area(cabina_obj)


# ESEMPIO DI INTEGRAZIONE COMPLETA NEL MAIN.PY
"""
ESEMPIO DI COME INTEGRARE NEL MAIN.PY ESISTENTE:

# All'inizio del file main.py, aggiungere:
from report.utils.streamlit_integration import interfaccia_report_sidebar, aggiungi_tab_report

# Nella funzione principale, dopo aver creato l'oggetto cabina:
def main():
    # ... codice esistente ...
    
    # Crea oggetto cabina
    cabina = CabinaMTBT(parametri...)
    
    # ... calcoli esistenti ...
    
    # OPZIONE 1: Aggiungere nella sidebar
    interfaccia_report_sidebar(cabina)
    
    # OPZIONE 2: Aggiungere come tab separato
    tab1, tab2, tab3, tab_report = st.tabs(["Calcoli", "Risultati", "Apparecchiature", "📊 Report"])
    
    with tab1:
        # ... contenuto esistente tab calcoli ...
    
    with tab2:
        # ... contenuto esistente tab risultati ...
    
    with tab3:
        # ... contenuto esistente tab apparecchiature ...
    
    with tab_report:
        aggiungi_tab_report(cabina)

if __name__ == "__main__":
    main()
"""