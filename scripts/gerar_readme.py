"""Incorpora as fontes Mermaid e a ADR no README sem divergência de conteúdo."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMAS = [
    ("Diagrama de sequência", "docs/diagrams/sequencia.mmd", "sequencia"),
    ("Diagrama de atividades com raias", "docs/diagrams/atividades.mmd", "atividades"),
    ("Diagrama de transição de estados", "docs/diagrams/estados.mmd", "estados"),
    ("C4 nível 3 de componentes", "docs/architecture/componentes.mmd", "componentes"),
    ("Interfaces públicas de apoio", "docs/diagrams/interfaces.mmd", "interfaces"),
]
def main():
    partes = [(ROOT / "docs/descricao.md").read_text(encoding="utf-8").strip()]
    for titulo, fonte, imagem in DIAGRAMAS:
        codigo = (ROOT / fonte).read_text(encoding="utf-8").strip()
        partes.append(
            f"## {titulo}\n\n"
            f"![{titulo}](docs/rendered/{imagem}.png)\n\n"
            f"[Ampliar SVG](docs/rendered/{imagem}.svg) | [Fonte Mermaid]({fonte})\n\n"
            f"<details>\n<summary>Código Mermaid incorporado</summary>\n\n"
            f"\x60\x60\x60mermaid\n{codigo}\n\x60\x60\x60\n\n</details>"
        )
    adr = (ROOT / "docs/architecture/adr-0001.md").read_text(encoding="utf-8").strip()
    adr = "\n".join("#" + linha if linha.startswith("#") else linha for linha in adr.splitlines())
    partes.append(adr)
    (ROOT / "README.md").write_text("\n\n".join(partes) + "\n", encoding="utf-8", newline="\n")
    print("README atualizado com cinco diagramas e ADR.")
if __name__ == "__main__":
    main()
