"""Comprime PDFs até ficarem abaixo de um tamanho alvo.

Uso:
    python compress_pdf.py arquivo.pdf                 # alvo padrão: 2 MB
    python compress_pdf.py arquivo.pdf -t 2            # alvo: 2 MB
    python compress_pdf.py arquivo.pdf -o saida.pdf -t 1.5
    python compress_pdf.py pasta/ -t 10                # todos os PDFs da pasta

Estratégia: primeiro faz uma limpeza sem perdas (remove objetos órfãos,
compacta streams). Se ainda estiver acima do alvo, recomprime as imagens
em JPEG com DPI e qualidade cada vez menores até caber no limite.
"""

import argparse
import io
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import pymupdf
except ImportError:
    print("Dependência ausente. Rode: pip install pymupdf", file=sys.stderr)
    sys.exit(3)

# (dpi, qualidade JPEG) — do mais leve ao mais agressivo
LEVELS = [
    (200, 85),
    (150, 80),
    (150, 65),
    (120, 60),
    (100, 50),
    (85, 45),
    (72, 40),
    (60, 30),
    (50, 25),
]


def mb(size: int) -> str:
    return f"{size / 1024 / 1024:.2f} MB"


def save_to_bytes(doc: pymupdf.Document) -> bytes:
    buf = io.BytesIO()
    doc.save(buf, garbage=4, deflate=True, deflate_images=True,
             deflate_fonts=True, clean=True, use_objstms=True)
    return buf.getvalue()


def compress(src: Path, target_bytes: int, grayscale: bool = False) -> tuple[bytes, str]:
    """Retorna (bytes do PDF, descrição do nível usado)."""
    original = src.read_bytes()

    with pymupdf.open(stream=original, filetype="pdf") as doc:
        doc.scrub(metadata=False, thumbnails=True, xml_metadata=True,
                  reset_fields=False, reset_responses=False)
        best = save_to_bytes(doc)
    best_desc = "sem perdas"
    if len(best) <= target_bytes and not grayscale:
        return best, best_desc

    for dpi, quality in LEVELS:
        with pymupdf.open(stream=original, filetype="pdf") as doc:
            doc.rewrite_images(
                dpi_threshold=dpi + 10,
                dpi_target=dpi,
                quality=quality,
                lossy=True,
                lossless=True,
                bitonal=True,
                color=True,
                gray=True,
                set_to_gray=grayscale,
            )
            data = save_to_bytes(doc)
        desc = f"{dpi} DPI, qualidade {quality}" + (", tons de cinza" if grayscale else "")
        print(f"  tentativa {desc}: {mb(len(data))}")
        if len(data) < len(best):
            best, best_desc = data, desc
        if len(data) <= target_bytes:
            break

    return best, best_desc


def process(src: Path, dst: Path, target_mb: float, grayscale: bool) -> bool:
    target = int(target_mb * 1024 * 1024)
    size_in = src.stat().st_size
    print(f"{src.name}: {mb(size_in)} (alvo {target_mb} MB)")

    if size_in <= target and not grayscale:
        print("  já está dentro do limite — nada a fazer.\n")
        return True

    data, desc = compress(src, target, grayscale)
    if len(data) >= size_in:
        print("  não foi possível reduzir; arquivo original mantido.\n")
        return False

    dst.write_bytes(data)
    ok = len(data) <= target
    reduction = 100 * (1 - len(data) / size_in)
    status = "OK" if ok else "ACIMA DO ALVO"
    print(f"  [{status}] {mb(size_in)} -> {mb(len(data))} (-{reduction:.0f}%, {desc})")
    print(f"  salvo em: {dst}\n")
    if not ok:
        print("  dica: o PDF provavelmente tem pouco conteúdo de imagem ou fontes pesadas;"
              " tente --grayscale ou divida o arquivo.\n")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Comprime PDFs até um tamanho alvo.")
    parser.add_argument("entrada", type=Path, help="arquivo PDF ou pasta com PDFs")
    parser.add_argument("-t", "--target", type=float, default=2.0,
                        help="tamanho máximo em MB (padrão: 2)")
    parser.add_argument("-o", "--output", type=Path,
                        help="arquivo (ou pasta, se a entrada for pasta) de saída")
    parser.add_argument("-g", "--grayscale", action="store_true",
                        help="converte imagens para tons de cinza (reduz bem mais)")
    args = parser.parse_args()

    src: Path = args.entrada
    if not src.exists():
        print(f"Erro: '{src}' não encontrado.", file=sys.stderr)
        return 1

    if src.is_dir():
        files = sorted(p for p in src.glob("*.pdf") if not p.stem.endswith("_comprimido"))
        if not files:
            print("Nenhum PDF encontrado na pasta.", file=sys.stderr)
            return 1
        out_dir = args.output or src
        out_dir.mkdir(parents=True, exist_ok=True)
        results = [process(f, out_dir / f"{f.stem}_comprimido.pdf", args.target, args.grayscale)
                   for f in files]
        return 0 if all(results) else 2

    dst = args.output or src.with_name(f"{src.stem}_comprimido.pdf")
    return 0 if process(src, dst, args.target, args.grayscale) else 2


if __name__ == "__main__":
    sys.exit(main())
