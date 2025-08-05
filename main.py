import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
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
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    dados = []
    lendo_dados = False
    posicoes_opcionais = True

    for linha in linhas:
        if "Pos No." in linha and "Name" in linha and "Class" in linha:
            lendo_dados = True
            continue

        if lendo_dados:
            if "Margin of Victory" in linha:
                break

            if linha.startswith("Not classified"):
                posicoes_opcionais = False
                continue

            partes = linha.split()
            if len(partes) < 4:
                continue

            match = re.search(r"\b([A-Z]{2,3})\b", linha)
            categoria = match.group(1) if match else "?"

            if posicoes_opcionais:
                pos = partes[0]
                num = partes[1]
                resto = linha.split(num, 1)[1].strip()
            else:
                pos = "-"
                num = partes[0]
                resto = linha.split(num, 1)[1].strip()

            nome_ate_categoria = resto.split(categoria)[0].strip()
            nome = nome_ate_categoria

            dados.append({
                "posicao": pos,
                "numero": num,
                "nome": nome,
                "categoria": categoria
            })

    return dados

def selecionar_pdf():
    caminho = filedialog.askopenfilename(title="Selecione um arquivo PDF", filetypes=[("Arquivos PDF", "*.pdf")])
    if not caminho:
        return

    try:
        with pdfplumber.open(caminho) as pdf:
            texto = "\n".join(pagina.extract_text() for pagina in pdf.pages if pagina.extract_text())

        resultados = extrair_info_pilotos(texto)
        global dados_extraidos
        dados_extraidos = resultados

        if resultados:
            atualizar_interface()
        else:
            messagebox.showwarning("Aviso", "Nenhuma informação de piloto foi encontrada.")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar o PDF: {e}")

def salvar_json():
    if not dados_extraidos:
        messagebox.showwarning("Aviso", "Nenhum dado para salvar")
        return

    caminho = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Arquivos JSON", "*.json")], title="Salvar como JSON")
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
                    menu_tabelas["menu"].add_command(label=nome, command=lambda n=nome: selecionar_tabela(n))

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

    atualizar_interface()

def atualizar_interface():
    linhas = []
    for d in dados_extraidos:
        pontos_base = d.get("pontos", 0)
        extras = d.get("pontos_extras", 0)
        total = pontos_base + extras
        linha = f"Posição: {d['posicao']} | Nº: {d['numero']} | Nome: {d['nome']} | Categoria: {d['categoria']} | Pontos: {total}"
        if extras:
            linha += f" (inclui {extras} extras)"
        linhas.append(linha)

    caixa_texto.delete("1.0", tk.END)
    caixa_texto.insert(tk.END, "\n".join(linhas))

def abrir_janela_pontos_extras():
    if not dados_extraidos:
        messagebox.showwarning("Aviso", "Nenhum dado carregado.")
        return

    janela_extra = tk.Toplevel()
    janela_extra.title("Adicionar Pontos Extras")
    janela_extra.geometry("400x200")

    tk.Label(janela_extra, text="Selecione o piloto:").pack(pady=5)
    nomes = [piloto["nome"] for piloto in dados_extraidos]
    nome_var = tk.StringVar(janela_extra)
    nome_var.set(nomes[0])
    tk.OptionMenu(janela_extra, nome_var, *nomes).pack(pady=5)

    tk.Label(janela_extra, text="Pontos extras:").pack(pady=5)
    entrada_pontos = tk.Entry(janela_extra)
    entrada_pontos.pack(pady=5)

    def aplicar_pontos():
        try:
            pontos_extras = int(entrada_pontos.get())
            for piloto in dados_extraidos:
                if piloto["nome"] == nome_var.get():
                    piloto["pontos_extras"] = pontos_extras
                    break
            atualizar_interface()
            janela_extra.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico válido.")

    tk.Button(janela_extra, text="Aplicar", command=aplicar_pontos).pack(pady=10)

def carregar_json():
    caminho = filedialog.askopenfilename(title="Abrir arquivo de resultados (.json)", filetypes=[("Arquivos JSON", "*.json")])
    if not caminho:
        return

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            resultados = json.load(f)

        if isinstance(resultados, list):
            global dados_extraidos
            dados_extraidos = resultados
            atualizar_interface()
        else:
            messagebox.showerror("Erro", "Formato inválido de dados.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar JSON: {e}")

def gerar_ranking():
    arquivos = filedialog.askopenfilenames(title="Selecionar Baterias", filetypes=[("Arquivos JSON", "*.json")])
    if not arquivos:
        return

    pontuacao_total = defaultdict(int)

    try:
        for caminho in arquivos:
            with open(caminho, "r", encoding="utf-8") as f:
                bateria = json.load(f)

            for piloto in bateria:
                nome = piloto.get("nome")
                pontos = int(piloto.get("pontos", 0)) + int(piloto.get("pontos_extras", 0))
                pontuacao_total[nome] += pontos

        ranking = sorted(pontuacao_total.items(), key=lambda x: x[1], reverse=True)
        linhas = [f"{i+1}º - {nome}: {pontos}" for i, (nome, pontos) in enumerate(ranking)]

        caixa_texto.delete("1.0", tk.END)
        caixa_texto.insert(tk.END, "\n".join(linhas))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar ranking: {e}")

janela = tk.Tk()
janela.title("Extrator de Dados de Pilotos")
janela.geometry("700x500")

tabela_selecionada = tk.StringVar()

tk.Button(janela, text="Selecionar PDF", command=selecionar_pdf).pack(pady=10)
tk.Button(janela, text="Salvar", command=salvar_json).pack(pady=10)
tk.Button(janela, text="Gerar Ranking Geral", command=gerar_ranking).pack(pady=5)
tk.Button(janela, text="Criar Nova Pontuação", command=abrir_janela_tabela).pack(pady=10)
tk.Button(janela, text="Abrir Resultados JSON", command=carregar_json).pack(pady=5)
tk.Button(janela, text="Adicionar Pontos Extras", command=abrir_janela_pontos_extras).pack(pady=5)

tk.Label(janela, text="Tabela de Pontuação:").pack()
menu_tabelas = tk.OptionMenu(janela, tabela_selecionada, "")
menu_tabelas.pack(pady=5)

caixa_texto = tk.Text(janela, wrap=tk.WORD)
caixa_texto.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

carregar_tabelas()
janela.mainloop()
