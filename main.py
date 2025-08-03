import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import re
import json

dados_extraidos = []

def extrair_info_pilotos(texto):
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip() != ""]

    dados = []
    lendo_tabela = False
    posicoes_opcionais = True

    for linha in linhas:
        if linha.startswith("Pos No. Name"):
            lendo_tabela = True
            continue

        if lendo_tabela:
            if "Margin of Victory" in linha:
                break

            if linha.startswith("Not classified"):
                posicoes_opcionais = False
                continue

            # Separar por partes com expressão regular
            partes = linha.split()
            if posicoes_opcionais:
                # Ex: 1 8 Miguel Facchini F4 ...
                if len(partes) >= 4:
                    pos = partes[0]
                    num = partes[1]
                    # Nome é tudo entre o número e a categoria (até encontrar algo que parece ser "F4", "FL 170" etc.)
                    for i in range(2, len(partes)):
                        if re.match(r"^(F4|FL|FT|Cadete|Mirim)", partes[i]):
                            categoria = partes[i]
                            nome = " ".join(partes[2:i])
                            break
                    else:
                        continue  # Não encontrou categoria, pula
            else:
                # Sem posição: ex: 86 Leonardo Tasca F4 ...
                if len(partes) >= 3:
                    pos = "-"
                    num = partes[0]
                    for i in range(1, len(partes)):
                        if re.match(r"^(F4|FL|FT|Cadete|Mirim)", partes[i]):
                            categoria = partes[i]
                            nome = " ".join(partes[1:i])
                            break
                    else:
                        continue

            dados.append({
                "posicao": pos,
                "numero": num,
                "nome": nome,
                "categoria": categoria
            })


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

        resultados = extrair_info_pilotos(texto)
        global dados_extraidos
        dados_extraidos = resultados

        if resultados:
            caixa_texto.delete("1.0", tk.END)
            caixa_texto.insert(tk.END, "\n".join(resultados))
        else:
            messagebox.showwarning("Aviso", "Nenhuma informação de piloto foi encontrada.")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar o PDF: {e}")

def salvar_json():
    if not dados_extraidos:
        messagebox.showwarning("Aviso", "Nenhum dado para salvar")
        return
    
    caminho = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("Arquivos JSON", "*.json")],
        title="Salvar como JSON"
    )

    if not caminho:
        return
    
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados_extraidos, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar JSON: {e}")





janela = tk.Tk()
janela.title("Extrator de Dados de Pilotos")
janela.geometry("700x500")

botao = tk.Button(janela, text="Selecionar PDF", command=selecionar_pdf)
botao.pack(pady=10)
botao_salvar = tk.Button(janela, text="Salvar", command=salvar_json)
botao_salvar.pack(pady=10)


caixa_texto = tk.Text(janela, wrap=tk.WORD)
caixa_texto.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

janela.mainloop()

