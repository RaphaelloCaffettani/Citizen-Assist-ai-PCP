"""Citizen Assist AI - assistente de orientação ao cidadão no terminal."""

from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento


def main():
    pasta = Path(__file__).resolve().parent
    base = BaseConhecimento(pasta / "data" / "base_conhecimento.json")
    base.carregar()
    assistente = Assistente("Citizen Assist AI", base)

    print("\n" + "=" * 58)
    print("      CITIZEN ASSIST AI - ORIENTAÇÃO AO CIDADÃO")
    print("=" * 58)
    print("Informações sobre Saúde, Documentos e Trabalho.")
    print("Aviso: este assistente NÃO é um canal oficial.")
    print("Não informe nome, CPF, telefone ou e-mail.")

    while True:
        print("\n========== MENU PRINCIPAL ==========")
        print("1. Fazer uma pergunta")
        print("2. Navegar por categorias")
        print("3. Ver indicadores")
        print("4. Exportar atendimentos para CSV")
        print("0. Sair")
        escolha = assistente._escolher_numero("Escolha uma opção: ", 4)
        if escolha == 1:
            assistente.perguntar()
        elif escolha == 2:
            assistente.navegar()
        elif escolha == 3:
            assistente.indicadores()
        elif escolha == 4:
            assistente.exportar_csv()
        elif escolha == 0:
            if assistente.registrar_facilidade():
                break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")
