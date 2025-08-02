import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber

def extrair_info_pilotos(texto):

    print("\n=== LINHAS ENCONTRADAS ===")
    for linha in linhas:
        print(repr(linha))  
    print("===========================\n")


    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip() != ""]
    linhas_normalizadas = [linha.lower().replace(":", "").strip() for linha in linhas]

    def extrair_bloco(titulo, fim_opcoes):
        try:
            i_inicio = linhas_normalizadas.index(titulo.lower()) + 1
            for fim in fim_opcoes:
                fim = fim.lower()
                if fim in linhas_normalizadas[i_inicio:]:
                    i_fim = i_inicio + linhas_normalizadas[i_inicio:].index(fim)
                    return linhas[i_inicio:i_fim]
            return linhas[i_inicio:]  
        except ValueError:
            return []

    posicoes   = extrair_bloco("Pos", ["No.", "Name", "Class", "Laps"])
    numeros    = extrair_bloco("No.", ["Name", "Class", "Laps"])
    nomes      = extrair_bloco("Name", ["Class", "Laps"])
    categorias = extrair_bloco("Class", ["Laps", "Diff", "Total Tm", "Best Tm"])

    dados = []
    for i in range(min(len(posicoes), len(numeros), len(nomes), len(categorias))):
        dados.append(f"Posição: {posicoes[i]} | Nº: {numeros[i]} | Nome: {nomes[i]} | Categoria: {categorias[i]}")

    return dados

def selecionar_pdf():
    caminho = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if not caminho:
        return

    try:
        with pdfplumber.open(caminho) as pdf:
            texto = ""
            for pagina in pdf.pages:
                texto += pagina.extract_text() + "\n"

        
        caixa_texto.delete("1.0", tk.END)
        caixa_texto.insert(tk.END, texto)

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar o PDF: {e}")




janela = tk.Tk()
janela.title("Extrator de Dados de Pilotos")
janela.geometry("700x500")

botao = tk.Button(janela, text="Selecionar PDF", command=selecionar_pdf)
botao.pack(pady=10)

caixa_texto = tk.Text(janela, wrap=tk.WORD)
caixa_texto.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

janela.mainloop()

