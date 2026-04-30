import os
from PyPDF2 import PdfMerger

# --- CONFIGURAÇÃO AUTOMÁTICA ---
# O comando abaixo faz o script olhar para a pasta onde ele está salvo
diretorio = os.path.dirname(os.path.abspath(__file__))
pasta_destino = os.path.join(diretorio, 'Finalizados')

# Cria a pasta de destino se não existir
if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

def processar_pdfs():
    # Lista arquivos .pdf na pasta
    arquivos = [f for f in os.listdir(diretorio) if f.lower().endswith('.pdf')]
    
    # Lógica: Capas têm o traço " - ". Formulários são apenas o número.
    capas = [f for f in arquivos if " - " in f]
    formularios = [f for f in arquivos if " - " not in f]

    print(f"--- Iniciando Processamento ---")
    print(f"Arquivos na pasta: {len(arquivos)}")
    print(f"Capas identificadas: {len(capas)}")
    print(f"Formulários identificados: {len(formularios)}\n")

    if not formularios:
        print("❌ Nenhum formulário (ex: 20402879.pdf) encontrado na pasta!")
        return

    for formulario in formularios:
        # Extrai o número da ordem (remove o .pdf)
        num_ordem = formulario.replace('.pdf', '').strip()
        
        # Procura a capa que começa com esse número
        capa_correspondente = next((c for c in capas if c.startswith(num_ordem)), None)

        if capa_correspondente:
            try:
                merger = PdfMerger()
                
                caminho_capa = os.path.join(diretorio, capa_correspondente)
                caminho_form = os.path.join(diretorio, formulario)
                
                # Juntar: Capa primeiro, depois Formulário
                merger.append(caminho_capa)
                merger.append(caminho_form)
                
                # Salva na pasta Finalizados
                nome_saida = f"{num_ordem}.pdf"
                merger.write(os.path.join(pasta_destino, nome_saida))
                merger.close()
                
                print(f"✅ Gerado com sucesso: {nome_saida}")
            except Exception as e:
                print(f"❌ Erro no número {num_ordem}: {e}")
        else:
            print(f"⚠️ Capa não encontrada para: {formulario}")

if __name__ == "__main__":
    processar_pdfs()
    print(f"\n--- Finalizado! Os arquivos estão em: {pasta_destino} ---")