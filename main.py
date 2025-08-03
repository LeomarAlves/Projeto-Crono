import tkinter as tk
from tkinter import filedialog, messagebox
import pdfplumber
import re
import json
import os

dados_extraidos = []
tabelas_pontuacao = []

def abrir_janela_tabela():
    janela_tabela = tk.Toplevel()
    janela_tabela.title("Nova Tabela de Pontuação")
    janela_tabela.geometry("600x300")

    tk.Label(janela_tabela, text="Nome da Tabela:").pack(pady=10)
    entrada_nome = tk.Entry(janela_tabela, width=50)
    entrada_nome.pack()

    tk.Label(janela_tabela, text="Pontos:").pack(pady=10)
    entrada_pontos = tk.Entry(janela_tabela, width=60)
    entrada_pontos.pack()

    def salvar_tabela():
        nome = entrada_nome.get().strip()
        texto_pontos = entrada_pontos.get().strip()
        if not nome or not texto_pontos:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        
        try:
            pontos_lista = [int(p.strip()) for p in texto_pontos.split(",")]
            pontos_dict = {str(i+1): pontos_lista[i] for i in range(len(pontos_lista))}

            nova_tabela = {
                "nome": nome,
                "pontos": pontos_dict
            }

            caminho = "tabelas_pontuacao.json"
            if os.path.exists(caminho):
                with open(caminho, "r", encoding="utf-8") as f:
                    todas = json.load(f)
            else:
                todas = []
            
            todas.append(nova_tabela)

            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(todas, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Sucesso", "Tabela salva com sucesso.")
            janela_tabela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar tabela: {e}")
    
    tk.Button(janela_tabela, text="Salvar Tabela", command=salvar_tabela).pack(pady=10)

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

            partes = linha.split()
            if len(partes) < 4:
                continue

            if posicoes_opcionais:
                pos = partes[0]
                num = partes[1]
                nome = " ".join(partes[2:-6])
                categoria = partes[-6]
            else:
                pos = "-"
                num = partes[0]
                nome = " ".join(partes[1:-6])
                categoria = partes[-6]

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
            linhas_formatadas = [
                f"Posição: {d['posicao']} | Nº: {d['numero']} | Nome: {d['nome']} | Categoria: {d['categoria']}"
                for d in resultados
            ]
            caixa_texto.insert(tk.END, "\n".join(linhas_formatadas))

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

def carregar_tabelas():
    global tabelas_pontuacao

    caminho = "tabelas_pontuacao.json"
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            tabelas_pontuacao = json.load(f)
            nomes = [t["nome"] for t in tabelas_pontuacao]
            if nomes:
                tabela_selecionada.set(nomes[0])
                menu_tabelas["menu"].delete(0, "end")
                for nome in nomes:
                    menu_tabelas["menu"].add_command(
                        label=nome,
                        command=lambda n=nome: selecionar_tabela(n)
                        )
                    
def selecionar_tabela(nome):
    tabela_selecionada.set(nome)
    tabela = next((t for t in tabelas_pontuacao if t["nome"] == nome), None)
    if not tabela:
        messagebox.showerror("Erro", "Tabela não encontrada")
        return
    
    pontos_por_posicao = tabela["pontos"]

    for piloto in dados_extraidos:
        pos = piloto.get("posicao")
        piloto["pontos"] = pontos_por_posicao.get(pos, 0)

    linhas = [
        f"Posição: {d['posicao']} | Nº: {d['numero']} | Nome: {d['nome']} | Categoria: {d['categoria']} | Pontos: {d['pontos']}"
        for d in dados_extraidos
    ]

    caixa_texto.delete("1.0", tk.END)
    caixa_texto.insert(tk.END, "\n".join(linhas))


def carregar_json():
    caminho = filedialog.askopenfilename(
        title="Abrir arquivo de resultados (.json)",
        filetypes=[("Arquivos JSON", "*.json")]
    )
    if not caminho:
        return

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            resultados = json.load(f)

        if isinstance(resultados, list):
            global dados_extraidos
            dados_extraidos = resultados  # atualiza a variável global

            linhas = [
                f"Posição: {d['posicao']} | Nº: {d['numero']} | Nome: {d['nome']} | Categoria: {d['categoria']} | Pontos: {d.get('pontos', 0)}"
                for d in resultados
            ]
            caixa_texto.delete("1.0", tk.END)
            caixa_texto.insert(tk.END, "\n".join(linhas))
        else:
            messagebox.showerror("Erro", "Formato inválido de dados.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar JSON: {e}")


janela = tk.Tk()
janela.title("Extrator de Dados de Pilotos")
janela.geometry("700x500")

tabela_selecionada = tk.StringVar()

botao = tk.Button(janela, text="Selecionar PDF", command=selecionar_pdf)
botao.pack(pady=10)
botao_salvar = tk.Button(janela, text="Salvar", command=salvar_json)
botao_salvar.pack(pady=10)

btn_nova_tabela = tk.Button(janela, text="Criar Nova Pontuação", command=abrir_janela_tabela)
btn_nova_tabela.pack(pady=10)

btn_abrir_json = tk.Button(janela, text="Abrir Resultados JSON", command=carregar_json)
btn_abrir_json.pack(pady=5)

tk.Label(janela, text="Tabela de Pontuação:").pack()
menu_tabelas = tk.OptionMenu(janela, tabela_selecionada, "")
menu_tabelas.pack(pady=5)

caixa_texto = tk.Text(janela, wrap=tk.WORD)
caixa_texto.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

carregar_tabelas()

janela.mainloop()

