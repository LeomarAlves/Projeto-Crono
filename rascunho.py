from collections import defaultdict

def gerar_ranking():
    arquivos = filedialog.askopenfilenames(
        title="Selecionar arquivos de baterias (.json)",
        filetypes=[("Arquivos JSON", "*.json")]
    )
    if not arquivos:
        return

    pontuacao_total = defaultdict(int)

    try:
        for caminho in arquivos:
            with open(caminho, "r", encoding="utf-8") as f:
                bateria = json.load(f)

            for piloto in bateria:
                nome = piloto.get("nome")
                pontos = int(piloto.get("pontos", 0))
                pontuacao_total[nome] += pontos

        # Gerar lista ordenada por pontuação
        ranking = sorted(pontuacao_total.items(), key=lambda x: x[1], reverse=True)

        linhas = [f"{i+1}º - {nome}: {pontos} pontos" for i, (nome, pontos) in enumerate(ranking)]
        caixa_texto.delete("1.0", tk.END)
        caixa_texto.insert(tk.END, "\n".join(linhas))

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar ranking: {e}")
