import streamlit as st
from PyPDF2 import PdfMerger
import io
import zipfile

# Configuração da página (título na aba do navegador)
st.set_page_config(page_title="Automação de PDFs - Empresa", page_icon="📄")

# Estilo para deixar o botão de download bem visível e bonito
st.markdown("""
    <style>
    .stDownloadButton button {
        width: 100%;
        background-color: #008CBA;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Capa + Formulário")
st.write("Sistema automatizado para junção de PDFs por número de ordem.")

# --- ÁREA DE UPLOAD ---
st.subheader("1. Carregue seus arquivos")
arquivos_carregados = st.file_uploader(
    "Arraste as capas e formulários aqui (pode selecionar todos de uma vez)", 
    type="pdf", 
    accept_multiple_files=True
)

if arquivos_carregados:
    # --- LOGICA DE IDENTIFICAÇÃO CORRIGIDA (SAP + PADRÃO) ---
    # Identifica como capa se tiver " - " (hífen) ou " – " (traço do SAP)
    capas = [f for f in arquivos_carregados if (" - " in f.name or " – " in f.name)]
    
    # Identifica como formulário se não tiver nenhum dos dois tipos de traço
    formularios = [f for f in arquivos_carregados if (" - " not in f.name and " – " not in f.name)]
    
    col1, col2 = st.columns(2)
    col1.metric("Capas detectadas", len(capas))
    col2.metric("Formulários detectados", len(formularios))

    # --- BOTÃO DE PROCESSAMENTO ---
    if st.button("🚀 Gerar PDFs Unidos"):
        if not capas or not formularios:
            st.warning("Certifique-se de carregar tanto as capas quanto os formulários.")
        else:
            # Criar um arquivo ZIP na memória
            buffer_zip = io.BytesIO()
            
            with zipfile.ZipFile(buffer_zip, "w") as zf:
                progresso = st.progress(0)
                status = st.empty()
                sucessos = 0

                for i, form in enumerate(formularios):
                    # Extrai o número do formulário (ex: 20402879.pdf -> 20402879)
                    num_ordem = form.name.replace(".pdf", "").strip()
                    
                    # Procura a capa que começa com esse número exato
                    capa_corresp = next((c for c in capas if c.name.startswith(num_ordem)), None)

                    if capa_corresp:
                        try:
                            merger = PdfMerger()
                            
                            # Lê os arquivos dos buffers (Streamlit)
                            merger.append(io.BytesIO(capa_corresp.getvalue()))
                            merger.append(io.BytesIO(form.getvalue()))
                            
                            # Salva o resultado em memória
                            pdf_saida = io.BytesIO()
                            merger.write(pdf_saida)
                            merger.close()
                            
                            # Adiciona ao ZIP usando apenas o número da ordem como nome
                            zf.writestr(f"{num_ordem}.pdf", pdf_saida.getvalue())
                            sucessos += 1
                        except Exception as e:
                            st.error(f"Erro no pedido {num_ordem}: {e}")
                    
                    # Atualiza barra de progresso e texto
                    progresso.progress((i + 1) / len(formularios))
                    status.text(f"Processando: {i+1} de {len(formularios)}")

            if sucessos > 0:
                st.success(f"✅ Concluído! {sucessos} arquivos processados.")
                
                # --- BOTÃO DE DOWNLOAD ---
                st.download_button(
                    label="⬇️ BAIXAR TODOS OS PDFs UNIDOS (.ZIP)",
                    data=buffer_zip.getvalue(),
                    file_name="PDFs_Finalizados.zip",
                    mime="application/zip"
                )
            else:
                st.error("Nenhum par correspondente (Capa + Formulário) foi encontrado.")