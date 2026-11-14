# compress-pdf

Skill do Claude Code que comprime PDFs até ficarem abaixo de um tamanho alvo (padrão: 2 MB).

Depois de instalada, é só digitar **`/compress-pdf`** no chat do Claude Code (ou pedir em linguagem natural, ex.: "comprime esse PDF pra menos de 3 MB").

## Como funciona

Primeiro faz uma limpeza sem perdas (remove objetos órfãos, compacta streams). Se ainda estiver acima do alvo, recomprime as imagens em JPEG com DPI e qualidade cada vez menores (200 DPI/q85 → 50 DPI/q25) até caber no limite. O original nunca é sobrescrito: a saída vai para `<nome>_comprimido.pdf`.

## Instalação

1. Clone este repositório dentro da pasta de skills do Claude Code:

   ```bash
   # Linux / macOS / Git Bash
   git clone https://github.com/HeitorPER/compress-pdf.git ~/.claude/skills/compress-pdf
   ```

   ```powershell
   # Windows (PowerShell)
   git clone https://github.com/HeitorPER/compress-pdf.git "$env:USERPROFILE\.claude\skills\compress-pdf"
   ```

   Para usar só em um projeto, clone em `.claude/skills/compress-pdf` dentro do projeto.

2. Instale as dependências Python:

   ```bash
   pip install pymupdf
   ```

   (ou `pip install -r requirements.txt`)

3. Reinicie o Claude Code. A skill aparece como `/compress-pdf`.

## Uso no Claude Code

```text
/compress-pdf passaporte.pdf
/compress-pdf contrato.pdf -t 1
/compress-pdf documentos/ -t 5
/compress-pdf escaneado.pdf -t 0.5 --grayscale
```

## Uso direto pela linha de comando

O script funciona sozinho, sem o Claude:

```bash
python scripts/compress_pdf.py arquivo.pdf -t 2
python scripts/compress_pdf.py pasta/ -t 5 -o saida/
python scripts/compress_pdf.py arquivo.pdf -t 1 -g
```

| Opção | Descrição |
|---|---|
| `-t, --target MB` | tamanho máximo em MB (padrão 2) |
| `-o, --output` | arquivo ou pasta de saída |
| `-g, --grayscale` | imagens em tons de cinza (reduz bem mais) |

## Estrutura

```text
compress-pdf/
├── SKILL.md            # instruções da skill (lidas pelo Claude)
├── scripts/
│   └── compress_pdf.py
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.10+
- [Claude Code](https://claude.com/claude-code)
