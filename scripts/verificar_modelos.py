"""Verificação documental: fontes, interfaces, figuras e renders desta entrega."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
def main():
    erros = []
    seq = (ROOT / "docs/diagrams/sequencia.mmd").read_text(encoding="utf-8")
    classes = (ROOT / "docs/diagrams/interfaces.mmd").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    aliases = dict(re.findall(r"participant\s+(\w+)\s+as\s+(\w+)", seq))
    ops = {}
    for nome, corpo in re.findall(r"class\s+(\w+)\s*\{([^}]+)\}", classes):
        ops[nome] = set(re.findall(r"\+(\w+)\(", corpo))
    chamadas = re.findall(r"^\s*\w+(?:->>|-\))(\w+):\s*(\w+)\(", seq, re.M)
    for alias, metodo in chamadas:
        nome = aliases.get(alias, alias)
        if metodo not in ops.get(nome, set()):
            erros.append(f"Operação não declarada: {nome}.{metodo}")
    blocos = re.findall(r"\x60\x60\x60mermaid\n(.*?)\n\x60\x60\x60", readme, re.S)
    relatorio = json.loads((ROOT / "docs/rendered/render-validation.json").read_text(encoding="utf-8"))
    for item in relatorio["results"]:
        fonte = ROOT / item["file"]
        conteudo = fonte.read_text(encoding="utf-8").strip()
        if conteudo not in blocos:
            erros.append(f"Fonte não sincronizada no README: {fonte.name}")
        atual = hashlib.sha256(fonte.read_bytes()).hexdigest()
        if not item["valid"] or item.get("source_sha256") != atual:
            erros.append(f"Render ausente, inválido ou desatualizado: {fonte.name}")
        stem = fonte.stem
        if not (ROOT / f"docs/rendered/{stem}.png").exists():
            erros.append(f"PNG ausente: {stem}")
        try:
            ET.parse(ROOT / f"docs/rendered/{stem}.svg")
        except Exception as exc:
            erros.append(f"SVG inválido: {stem}: {exc}")
    adr = (ROOT / "docs/architecture/adr-0001.md").read_text(encoding="utf-8")
    for secao in ["## Status", "## Contexto", "## Decisão", "## Consequências"]:
        if secao not in adr:
            erros.append(f"Campo ADR ausente: {secao}")
    for alvo in re.findall(r"\]\(([^)]+)\)", readme):
        if not re.match(r"^(https?://|#)", alvo) and not (ROOT / alvo).exists():
            erros.append(f"Link local ausente: {alvo}")
    if len(blocos) != 5:
        erros.append(f"Esperados cinco blocos Mermaid; encontrados {len(blocos)}")
    if erros:
        print("\n".join(erros))
        raise SystemExit(1)
    print(f"OK: {len(chamadas)} chamadas correspondem a operações públicas; cinco fontes incorporadas; renders e ADR conferidos.")
if __name__ == "__main__":
    main()
