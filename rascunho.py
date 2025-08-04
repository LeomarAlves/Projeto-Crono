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

