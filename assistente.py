"""Atendimento no terminal, histórico, métricas e exportação em CSV."""

import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path


CAMPOS_CSV = [
    "data", "origem", "pergunta", "id_orientacao", "encontrou",
    "ajudou", "tentativas", "tempo_segundos", "facilidade"
]


class Assistente:
    """Conduz os atendimentos usando uma BaseConhecimento."""

    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.historico = []
        self.caminho_historico = base.caminho.parent / "historico.json"
        self.indice_ultimo_atendimento_sessao = None
        self._carregar_historico()

    def _carregar_historico(self):
        try:
            with self.caminho_historico.open("r", encoding="utf-8") as arquivo:
                registros = json.load(arquivo)
            if not isinstance(registros, list):
                raise ValueError("o histórico deve ser uma lista")
            self.historico = [r for r in registros if isinstance(r, dict)]
        except FileNotFoundError:
            self.historico = []
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as erro:
            print(f"Aviso: histórico não pôde ser lido: {erro}")
            self.historico = []

    @staticmethod
    def contem_dados_pessoais(texto):
        """Não aceita perguntas com @ ou com 8 ou mais algarismos."""
        return "@" in texto or len(re.findall(r"\d", texto)) >= 8

    @staticmethod
    def _escolher_numero(mensagem, maximo):
        """Repete a pergunta até receber uma opção válida, incluindo 0."""
        while True:
            valor = input(mensagem).strip()
            if valor.isdigit() and 0 <= int(valor) <= maximo:
                return int(valor)
            print(f"Opção inválida. Digite um número entre 0 e {maximo}.")

    @staticmethod
    def _ler_sim_nao(mensagem):
        """0 significa não avaliar; não encerra o programa."""
        while True:
            resposta = input(mensagem).strip().lower()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "nao", "não"):
                return False
            if resposta == "0":
                return None
            print("Resposta inválida. Digite s, n ou 0 para voltar.")

    def registrar(self, origem, pergunta, orientacao_id, encontrou, ajudou,
                  tentativas, inicio):
        registro = {
            "data": datetime.now().astimezone().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": orientacao_id,
            "encontrou": bool(encontrou),
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": round(time.time() - inicio, 1),
            "facilidade": None
        }
        if self.contem_dados_pessoais(pergunta):
            print("Consulta recusada por proteção de dados. Nada foi registrado.")
            return False
        self.historico.append(registro)
        self.indice_ultimo_atendimento_sessao = len(self.historico) - 1
        self._salvar_historico()
        return True

    def _salvar_historico(self):
        try:
            self.caminho_historico.parent.mkdir(parents=True, exist_ok=True)
            with self.caminho_historico.open("w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError as erro:
            print(f"Aviso: não foi possível salvar o histórico: {erro}")

    def _apresentar_resultado(self, pontos, orientacao, alternativas):
        confianca = "ALTA" if pontos >= 6 else "MÉDIA"
        print(f"\nConfiança da resposta: {confianca} ({pontos} pontos)")
        orientacao.exibir()
        if alternativas:
            print("\nOutras orientações relacionadas:")
            for pontos_alt, alternativa in alternativas[:2]:
                print(f"  - {alternativa.titulo} ({pontos_alt} pontos)")

    def perguntar(self):
        """Busca por pontuação, permite reformulação e registra o atendimento."""
        if not self.base.orientacoes:
            print("Base de conhecimento indisponível. Não é possível consultar.")
            return

        inicio = time.time()
        tentativas = 0
        primeira_pergunta = None
        while True:
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                if tentativas:
                    self.registrar("pergunta", primeira_pergunta, None,
                                   False, False, tentativas, inicio)
                return
            if not pergunta:
                print("Digite uma dúvida ou 0 para voltar.")
                continue
            if self.contem_dados_pessoais(pergunta):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva a pergunta.")
                continue

            tentativas += 1
            if primeira_pergunta is None:
                primeira_pergunta = pergunta

            encontrados = self.base.buscar(pergunta)
            melhores = [(pontos, item) for pontos, item in encontrados if pontos >= 3]
            if melhores:
                pontos, orientacao = melhores[0]
                self._apresentar_resultado(pontos, orientacao, melhores[1:3])
                ajudou = self._ler_sim_nao(
                    "Essa orientação respondeu sua dúvida? (s/n, 0 para voltar): "
                )
                self.registrar("pergunta", primeira_pergunta, orientacao.id,
                               True, ajudou, tentativas, inicio)
                return

            print("\nNão encontrei uma orientação com confiança suficiente.")
            print("Tente outras palavras ou consulte a lista de categorias.")
            refazer = self._ler_sim_nao(
                "Quer reformular a dúvida? (s/n, 0 para voltar): "
            )
            if refazer is True:
                continue
            self.registrar("pergunta", primeira_pergunta, None,
                           False, False, tentativas, inicio)
            return

    def navegar(self):
        """Navegação completa por categorias e orientações numeradas."""
        if not self.base.orientacoes:
            print("Base de conhecimento indisponível. Não há categorias.")
            return

        while True:
            categorias = self.base.categorias()
            print("\n--- CATEGORIAS ---")
            for indice, categoria in enumerate(categorias, start=1):
                print(f"{indice}. {categoria}")
            print("0. Voltar")
            numero = self._escolher_numero("Categoria: ", len(categorias))
            if numero == 0:
                return
            categoria = categorias[numero - 1]

            while True:
                itens = self.base.por_categoria(categoria)
                print(f"\n--- {categoria.upper()} ---")
                for indice, orientacao in enumerate(itens, start=1):
                    print(f"{indice}. {orientacao.titulo}")
                print("0. Voltar")
                numero_item = self._escolher_numero("Orientação: ", len(itens))
                if numero_item == 0:
                    break
                inicio = time.time()
                orientacao = itens[numero_item - 1]
                print("\nConfiança da resposta: SELEÇÃO DIRETA POR CATEGORIA")
                orientacao.exibir()
                ajudou = self._ler_sim_nao(
                    "Essa orientação respondeu sua dúvida? (s/n, 0 para voltar): "
                )
                self.registrar("categoria", orientacao.titulo, orientacao.id,
                               True, ajudou, 1, inicio)

    def registrar_facilidade(self):
        """Solicita nota 1 a 5 ao encerrar e a associa à sessão atual."""
        print("\nAvaliação da facilidade de uso (1 = difícil; 5 = fácil).")
        print("0. Voltar ao menu")
        nota = self._escolher_numero("Nota (1 a 5, ou 0): ", 5)
        if nota == 0:
            return False
        if self.indice_ultimo_atendimento_sessao is not None:
            self.historico[self.indice_ultimo_atendimento_sessao]["facilidade"] = nota
            self._salvar_historico()
        else:
            print("Nota recebida. Não houve atendimento nesta sessão para vinculá-la.")
        print("Obrigado por utilizar o Citizen Assist AI!")
        return True

    def indicadores(self):
        """Calcula e mostra índices a partir de dados realmente registrados."""
        registros = self.historico
        total = len(registros)
        encontrados = sum(1 for r in registros if r.get("encontrou") is True)
        avaliados = [r for r in registros if r.get("ajudou") in (True, False)
                     and r.get("encontrou") is True]
        ajudaram = sum(1 for r in avaliados if r["ajudou"] is True)
        tempos = [float(r["tempo_segundos"]) for r in registros
                  if r.get("encontrou") is True
                  and isinstance(r.get("tempo_segundos"), (int, float))]
        tentativas = [int(r["tentativas"]) for r in registros
                      if isinstance(r.get("tentativas"), int)]
        notas = [r["facilidade"] for r in registros if isinstance(r.get("facilidade"), int)
                 and 1 <= r["facilidade"] <= 5]
        pendentes = sorted({r.get("pergunta", "") for r in registros
                           if r.get("encontrou") is False and r.get("pergunta")})

        percentual_encontradas = 100 * encontrados / total if total else 0.0
        percentual_ajudou = 100 * ajudaram / len(avaliados) if avaliados else 0.0
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0.0
        media_tentativas = sum(tentativas) / len(tentativas) if tentativas else 0.0
        facilidade = sum(notas) / len(notas) if notas else None
        dados = {
            "atendimentos": total,
            "encontradas_percentual": percentual_encontradas,
            "ajudou_percentual": percentual_ajudou,
            "avaliacoes_resposta": len(avaliados),
            "tempo_medio": tempo_medio,
            "tentativas_medias": media_tentativas,
            "facilidade_media": facilidade,
            "notas_recebidas": len(notas),
            "duvidas_sem_solucao": pendentes
        }

        print("\n--- INDICADORES DOS ATENDIMENTOS REGISTRADOS ---")
        print(f"Total de atendimentos: {total}")
        print(f"Respostas encontradas: {percentual_encontradas:.1f}%")
        print(f"Taxa de acerto (ajudou): {percentual_ajudou:.1f}% "
              f"({len(avaliados)} respostas avaliadas)")
        print(f"Tempo médio para encontrar: {tempo_medio:.1f} segundo(s)")
        print(f"Tentativas por atendimento: {media_tentativas:.2f}")
        if facilidade is None:
            print("Facilidade de uso (1 a 5): sem avaliações")
        else:
            print(f"Facilidade de uso (1 a 5): {facilidade:.2f} "
                  f"({len(notas)} avaliação/avaliações)")
        print("Dúvidas sem solução:")
        if pendentes:
            for pergunta in pendentes:
                print(f"  - {pergunta}")
        else:
            print("  Nenhuma registrada.")
        return dados

    def exportar_csv(self):
        """Exporta registros em CSV UTF-8 com delimitador ponto e vírgula."""
        caminho = self.base.caminho.parent / "atendimentos.csv"
        try:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                           delimiter=";", extrasaction="ignore")
                escritor.writeheader()
                escritor.writerows(self.historico)
            print(f"\nCSV exportado: {caminho}")
            print(f"Registros exportados: {len(self.historico)}")
            return True
        except OSError as erro:
            print(f"Não foi possível exportar o CSV: {erro}")
            return False
