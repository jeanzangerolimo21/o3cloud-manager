import re

from markupsafe import escape


HTML_TAG_RE = re.compile(r"<[a-zA-Z][\s\S]*>")


def montar_email_marketing(corpo_html, logo_url=None, imagem_corpo_url=None):
    corpo = (corpo_html or "").strip()
    conteudo = corpo if HTML_TAG_RE.search(corpo) else _texto_para_html(corpo)
    if imagem_corpo_url:
        conteudo += _imagem_corpo(imagem_corpo_url)
    logo = _logo_header(logo_url)

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>O3Cloud</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;color:#1f2933;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f6f8;margin:0;padding:24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;background:#ffffff;border-collapse:collapse;border:1px solid #e5e7eb;">
          <tr>
            <td align="center" style="padding:24px 28px;border-bottom:1px solid #edf0f2;background:#ffffff;text-align:center;">
              {logo}
            </td>
          </tr>
          <tr>
            <td style="padding:28px;font-size:15px;line-height:1.6;color:#1f2933;">
              {conteudo}
            </td>
          </tr>
          <tr>
            <td style="padding:22px 28px;border-top:1px solid #edf0f2;background:#f9fafb;font-size:13px;line-height:1.5;color:#4b5563;">
              <strong style="color:#111827;">O3 CLOUD SOLUCOES EM TECNOLOGIA LTDA</strong><br>
              CNPJ: 56.777.698/0001-00<br>
              Telefone: <a href="tel:+551931420232" style="color:#0f5f8f;text-decoration:none;">19 3142-0232</a><br>
              E-mail: <a href="mailto:comercial@o3cloud.com.br" style="color:#0f5f8f;text-decoration:none;">comercial@o3cloud.com.br</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _texto_para_html(texto):
    linhas = str(escape(texto)).splitlines()
    paragrafos = []
    atual = []
    for linha in linhas:
        if linha.strip():
            atual.append(linha)
            continue
        if atual:
            paragrafos.append("<br>".join(atual))
            atual = []
    if atual:
        paragrafos.append("<br>".join(atual))
    if not paragrafos:
        return ""
    return "".join(f'<p style="margin:0 0 16px;">{paragrafo}</p>' for paragrafo in paragrafos)


def _imagem_corpo(imagem_url):
    return (
        '<div style="margin:24px 0 0;">'
        f'<img src="{escape(imagem_url)}" alt="" '
        'style="display:block;max-width:100%;height:auto;border:0;">'
        '</div>'
    )


def _logo_header(logo_url):
    if logo_url:
        return (
            f'<img src="{escape(logo_url)}" alt="O3Cloud" width="150" '
            'style="display:block;max-width:150px;height:auto;border:0;margin:0 auto;">'
        )
    return '<strong style="display:block;font-size:22px;line-height:1;color:#0f5f8f;text-align:center;">O3Cloud</strong>'
