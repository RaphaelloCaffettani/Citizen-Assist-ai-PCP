"""Representação de uma orientação de serviço público."""


class Orientacao:
    """Uma orientação cadastrada na base de conhecimento."""

    def __init__(self, dados):
        self.id = dados["id"]
        self.categoria = dados["categoria"]
        self.titulo = dados["titulo"]
        self.palavras_chave = dados["palavras_chave"]
        self.resposta = dados["resposta"]
        self.documentos = dados["documentos"]
        self.onde = dados["onde"]
        self.fonte = dados["fonte"]
        self.verificado_em = dados["verificado_em"]

    def exibir(self):
        """Apresenta a orientação, os requisitos e sua fonte oficial."""
        print("\n" + "=" * 68)
        print(f">> {self.titulo} [{self.categoria}]")
        print("=" * 68)
        print(self.resposta)
        print("\nDocumentos ou requisitos:")
        for item in self.documentos:
            print(f"  - {item}")
        print(f"\nOnde: {self.onde}")
        print(f"Fonte: {self.fonte}")
        print(f"Verificado em: {self.verificado_em}")
        print("Aviso: este assistente NÃO é um canal oficial.")
        print("Consulte a fonte antes de tomar uma decisão.")
