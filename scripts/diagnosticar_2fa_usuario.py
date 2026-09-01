#!/usr/bin/env python3
"""Diagnostico read-only de 2FA/dispositivo confiavel para um usuario."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.configuracoes.auth_service import AuthConfigService  # noqa: E402
from app.core.database import get_connection  # noqa: E402


def fetch_all(cursor, sql, params=()):
    cursor.execute(sql, params)
    return cursor.fetchall()


def fetch_one(cursor, sql, params=()):
    cursor.execute(sql, params)
    return cursor.fetchone()


def fmt(valor):
    if valor is None:
        return "-"
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M:%S")
    return str(valor)


def linha(titulo):
    print("\n" + titulo)
    print("-" * len(titulo))


def imprimir_chave_valor(dados, chaves):
    for chave, label in chaves:
        print(f"{label}: {fmt(dados.get(chave))}")


def abreviar(texto, limite=140):
    texto = (texto or "").replace("\n", " ").strip()
    if len(texto) <= limite:
        return texto or "-"
    return texto[: limite - 3] + "..."


def main():
    parser = argparse.ArgumentParser(description="Diagnostica 2FA e dispositivo confiavel de um usuario.")
    parser.add_argument("--email", default="wilgner.correa@o3cloud.com.br", help="E-mail/login do usuario")
    parser.add_argument("--limite", type=int, default=20, help="Quantidade de registros recentes por bloco")
    args = parser.parse_args()

    email = (args.email or "").strip().lower()
    if not email:
        raise SystemExit("Informe --email.")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        agora = fetch_one(cursor, "SELECT NOW() AS agora") or {}
        print("Diagnostico 2FA / dispositivo confiavel")
        print(f"Usuario pesquisado: {email}")
        print(f"Data/hora banco: {fmt(agora.get('agora'))}")
        print(f"Cookie esperado no navegador: {AuthConfigService.MFA_COOKIE_NAME}")
        print(f"Validade esperada do dispositivo confiavel: {AuthConfigService.MFA_TRUSTED_DEVICE_DAYS} dias")

        usuarios = fetch_all(
            cursor,
            """
            SELECT id, nome, email, login, origem, status, exigir_2fa, two_factor_metodo,
                   two_factor_configurado_em, ultimo_login_em, updated_at
            FROM auth_usuarios
            WHERE LOWER(COALESCE(email, ''))=%s OR LOWER(COALESCE(login, ''))=%s
            ORDER BY id
            """,
            (email, email),
        )
        if not usuarios:
            linha("Usuario")
            print("Nenhum usuario encontrado com esse email/login nesta base.")
            return 1

        for usuario in usuarios:
            usuario_id = usuario.get("id")
            linha(f"Usuario #{usuario_id}")
            imprimir_chave_valor(
                usuario,
                [
                    ("nome", "Nome"),
                    ("email", "Email"),
                    ("login", "Login"),
                    ("origem", "Origem"),
                    ("status", "Status"),
                    ("exigir_2fa", "Exige 2FA"),
                    ("two_factor_metodo", "Metodo 2FA"),
                    ("two_factor_configurado_em", "TOTP configurado em"),
                    ("ultimo_login_em", "Ultimo login"),
                    ("updated_at", "Atualizado em"),
                ],
            )

            dispositivos = fetch_all(
                cursor,
                """
                SELECT id, descricao, ip_origem, user_agent, created_at, ultimo_uso_em, expira_em, revogado_em,
                       CASE
                         WHEN revogado_em IS NOT NULL THEN 'REVOGADO'
                         WHEN expira_em < NOW() THEN 'EXPIRADO'
                         ELSE 'VALIDO'
                       END AS status_dispositivo
                FROM auth_dispositivos_confiaveis
                WHERE usuario_id=%s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (usuario_id, args.limite),
            )
            linha("Dispositivos confiaveis")
            if not dispositivos:
                print("Nenhum dispositivo confiavel gravado para este usuario.")
            for item in dispositivos:
                print(
                    "#{id} {status} | criado {created} | ultimo uso {uso} | expira {expira} | IP {ip} | {ua}".format(
                        id=item.get("id"),
                        status=item.get("status_dispositivo"),
                        created=fmt(item.get("created_at")),
                        uso=fmt(item.get("ultimo_uso_em")),
                        expira=fmt(item.get("expira_em")),
                        ip=fmt(item.get("ip_origem")),
                        ua=abreviar(item.get("user_agent")),
                    )
                )

            codigos = fetch_all(
                cursor,
                """
                SELECT id, status, tentativas, ip_origem, user_agent, created_at, expira_em, usado_em
                FROM auth_2fa_codigos
                WHERE usuario_id=%s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (usuario_id, args.limite),
            )
            linha("Codigos 2FA recentes")
            if not codigos:
                print("Nenhum codigo 2FA recente encontrado para este usuario.")
            for item in codigos:
                print(
                    "#{id} {status} | tentativas {tentativas} | criado {created} | expira {expira} | usado {usado} | IP {ip} | {ua}".format(
                        id=item.get("id"),
                        status=item.get("status"),
                        tentativas=item.get("tentativas"),
                        created=fmt(item.get("created_at")),
                        expira=fmt(item.get("expira_em")),
                        usado=fmt(item.get("usado_em")),
                        ip=fmt(item.get("ip_origem")),
                        ua=abreviar(item.get("user_agent")),
                    )
                )

            auditoria = fetch_all(
                cursor,
                """
                SELECT acao, detalhes, ip_origem, user_agent, created_at
                FROM auth_auditoria
                WHERE LOWER(usuario_email)=%s
                  AND acao IN (
                    'LOGIN_SENHA_VALIDADA', 'LOGIN_2FA_CODIGO_ENVIADO', 'LOGIN_2FA_SUCESSO',
                    'LOGIN_2FA_FALHA', 'LOGIN_2FA_BLOQUEADO', 'LOGIN_SUCESSO', 'LOGOUT'
                  )
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (email, args.limite),
            )
            linha("Auditoria recente")
            if not auditoria:
                print("Nenhuma auditoria recente encontrada para este email nos ultimos registros retidos.")
            for item in auditoria:
                print(
                    "{data} | {acao} | {detalhes} | IP {ip} | {ua}".format(
                        data=fmt(item.get("created_at")),
                        acao=item.get("acao"),
                        detalhes=abreviar(item.get("detalhes"), 80),
                        ip=fmt(item.get("ip_origem")),
                        ua=abreviar(item.get("user_agent")),
                    )
                )

            linha("Leitura rapida")
            validos = [d for d in dispositivos if d.get("status_dispositivo") == "VALIDO"]
            if not bool(usuario.get("exigir_2fa")):
                print("Este usuario nao esta marcado para exigir 2FA. Se esta pedindo 2FA, confira perfil/login usado.")
            elif not validos:
                print("Nao ha dispositivo confiavel valido. Se ele marcou confiar por 30 dias, o cookie pode nao estar sendo salvo ou o registro foi expirado/revogado.")
            elif all(not d.get("ultimo_uso_em") or d.get("ultimo_uso_em") == d.get("created_at") for d in validos):
                print("Existe dispositivo valido, mas sem reutilizacao clara. Forte indicio de navegador nao devolvendo o cookie.")
            else:
                print("Existe dispositivo valido com uso recente. Se ainda pede 2FA, verifique se ele acessa por outro navegador, perfil, modo anonimo ou outra URL/dominio.")
            print("Conferir no PC: cookies permitidos, limpeza automatica ao fechar, extensoes de privacidade, modo anonimo e mesma URL do Beta.")
    finally:
        cursor.close()
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
