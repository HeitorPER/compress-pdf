---
name: compress-pdf
description: Compress PDF files until they fit under a target size in MB (default 2 MB), first losslessly and then by re-encoding images with progressively lower DPI/JPEG quality. Use when the user wants to shrink, reduce, or compress a PDF, make a PDF smaller for upload/email, or invokes /compress-pdf.
argument-hint: <arquivo.pdf | pasta> [-t MB] [-o saida] [-g]
---

# Compress PDF

Comprime um PDF (ou todos os PDFs de uma pasta) até ficar abaixo de um tamanho alvo.

Argumentos recebidos: `$ARGUMENTS`

## Como executar

1. Descubra o arquivo/pasta de entrada e o tamanho alvo a partir dos argumentos ou da conversa.
   - Se nenhum arquivo foi informado, procure PDFs na pasta atual e pergunte qual usar.
   - Alvo padrão: **2 MB**. Se o usuário disser "abaixo de 5 MB", use `-t 5`.
2. Rode o script que acompanha esta skill (pasta `scripts/` ao lado deste SKILL.md):

   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/compress_pdf.py" "<entrada>" -t <MB>
   ```

   Opções:
   - `-t, --target MB` — tamanho máximo em MB (padrão 2)
   - `-o, --output CAMINHO` — arquivo de saída (ou pasta, se a entrada for pasta). Padrão: `<nome>_comprimido.pdf` ao lado do original
   - `-g, --grayscale` — converte imagens para tons de cinza (reduz bem mais)

3. Se o script sair com código **3** (dependência ausente), instale com
   `python -m pip install pymupdf` e rode de novo.
4. Informe ao usuário: tamanho original → final, % de redução, nível usado e onde o arquivo foi salvo.
   - Código de saída **2** = não chegou no alvo. Sugira `--grayscale`, um alvo maior ou dividir o PDF.

## Notas

- O arquivo original nunca é sobrescrito, a menos que o usuário peça explicitamente com `-o`.
- A compressão é progressiva: limpeza sem perdas → 200 DPI/q85 … até 50 DPI/q25. Para no primeiro nível que cabe no alvo.
- PDFs só com texto/vetores reduzem pouco; a maior parte do ganho vem das imagens.
