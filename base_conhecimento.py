"""Leitura da base JSON e busca por regras com pontuação."""

import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from orientacao import Orientacao


CAMPOS = {
    "id", "categoria", "titulo", "palavras_chave", "resposta",
    "documentos", "onde", "fonte", "verificado_em"
}


def normalizar(texto):
    """Retira acentos e pontuação e padroniza espaços e letras."""
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """Carrega registros, lista categorias e encontra orientações relevantes."""

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON sem encerrar o programa caso haja problemas no arquivo."""
        self.orientacoes = []
        try:
            with self.caminho.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (FileNotFoundError, PermissionError, OSError, UnicodeError, json.JSONDecodeError) as erro:
            print(f"Aviso: não foi possível carregar a base de conhecimento: {erro}")
            return False

        if not isinstance(dados, list):
            print("Aviso: a base deve conter uma lista de orientações.")
            return False

        ids = set()
        for numero, registro in enumerate(dados, start=1):
            if not self._registro_valido(registro) or registro["id"] in ids:
                print(f"Aviso: orientação {numero} inválida ou com ID repetido; ignorada.")
                continue
            ids.add(registro["id"])
            self.orientacoes.append(Orientacao(registro))

        if not self.orientacoes:
            print("Aviso: nenhuma orientação válida foi encontrada.")
            return False
        return True

    @staticmethod
    def _registro_valido(dados):
        if not isinstance(dados, dict) or not CAMPOS.issubset(dados):
            return False
        if type(dados["id"]) is not int or dados["id"] <= 0:
            return False
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte"):
            if not isinstance(dados[campo], str) or not dados[campo].strip():
                return False
        for campo in ("palavras_chave", "documentos"):
            itens = dados[campo]
            if not isinstance(itens, list) or not itens or not all(
                isinstance(item, str) and item.strip() for item in itens
            ):
                return False
        if len(dados["palavras_chave"]) < 3:
            return False
        try:
            date.fromisoformat(dados["verificado_em"])
            endereco = urlparse(dados["fonte"])
            return endereco.scheme == "https" and bool(endereco.netloc)
        except (ValueError, TypeError):
            return False

    def categorias(self):
        return sorted({orientacao.categoria for orientacao in self.orientacoes})

    def por_categoria(self, categoria):
        return sorted(
            [item for item in self.orientacoes if item.categoria == categoria],
            key=lambda item: item.titulo
        )

    def pontuar(self, pergunta, orientacao):
        pergunta_normalizada = normalizar(pergunta)
        titulo_normalizado = normalizar(orientacao.titulo)
        pontos = 0

        # Cada expressão cadastrada encontrada na pergunta vale 3 pontos.
        # Os espaços ao redor impedem combinações parciais de palavras.
        for palavra_chave in orientacao.palavras_chave:
            chave = normalizar(palavra_chave)
            if chave.strip() and chave in pergunta_normalizada:
                pontos += 3

        # Cada palavra DIFERENTE da pergunta com >= 4 letras, se estiver
        # no título como palavra completa, acrescenta 1 ponto.
        palavras = set(pergunta_normalizada.split())
        titulo = set(titulo_normalizado.split())
        pontos += sum(1 for palavra in palavras if len(palavra) >= 4 and palavra in titulo)
        return pontos

    def buscar(self, pergunta):
        """Retorna [(pontos, orientacao), ...] em ordem decrescente."""
        resultados = [
            (self.pontuar(pergunta, item), item) for item in self.orientacoes
        ]
        # Ordenação estável em empates, pelo identificador do registro.
        return sorted(resultados, key=lambda par: (-par[0], par[1].id))
