"""
Normalizador do catalogo Base44.

Responsabilidades:

- Eliminar duplicidades
- Agrupar categorias
- Agrupar produtos
- Agrupar modelos
- Agrupar faixas
- Preparar precos para futura importacao

NAO grava no banco de dados.
NAO utiliza Repository.
NAO conhece Service.
"""

from .models import (
    ProdutoImportado,
    RecursoImportado,
    ResultadoImportacao,
)


class Base44Normalizador:

    @staticmethod
    def _slug(texto):
        return (
            str(texto)
            .strip()
            .upper()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
        )

    def normalizar(self, registros):
        resultado = ResultadoImportacao()

        categorias = {}
        produtos = {}
        modelos = {}
        faixas = {}
        recursos = {}
        precos = []

        for registro in registros:
            if registro is None:
                continue

            categoria_codigo = self._slug(registro.categoria)[:30]

            categorias[categoria_codigo] = {
                "codigo": categoria_codigo,
                "nome": registro.categoria.strip(),
                "descricao": f"Categoria importada do Base44: {registro.categoria.strip()}",
                "cor": "#0d6efd",
                "ordem": 0,
                "ativo": bool(registro.ativo),
            }

            if isinstance(registro, ProdutoImportado):
                produto_codigo = self._slug(registro.produto)[:30]
                nome_faixa = registro.nome_comercial.strip() or registro.descricao.strip()

                produtos[produto_codigo] = {
                    "categoria_codigo": categoria_codigo,
                    "codigo": produto_codigo,
                    "nome": registro.produto.strip(),
                    "descricao": registro.descricao.strip(),
                    "codigo_externo": "",
                    "unidade": "UN",
                    "tipo_recurso": "LICENCA" if registro.tipo == "LICENCA" else "SERVICO",
                    "valor_venda": 0,
                    "valor_custo": 0,
                    "origem": "MANUAL",
                    "ativo": bool(registro.ativo),
                }

                modelo_nome = registro.modelo.strip() or "STANDARD"
                modelo_codigo = self._slug(modelo_nome)[:30]
                chave_modelo = (produto_codigo, modelo_codigo)

                modelos[chave_modelo] = {
                    "produto_codigo": produto_codigo,
                    "codigo": modelo_codigo,
                    "nome": modelo_nome,
                    "descricao": f"Modelo importado do Base44: {modelo_nome}",
                    "ordem": 0,
                    "padrao": modelo_codigo == "STANDARD",
                    "versao": "",
                    "ativo": bool(registro.ativo),
                }

                if registro.faixa_inicio is not None:
                    inicio = int(registro.faixa_inicio)
                    fim = int(
                        registro.faixa_fim
                        if registro.faixa_fim is not None
                        else registro.faixa_inicio
                    )
                    faixa_codigo = f"FX_{inicio}_{fim}"[:30]
                    faixa_nome = nome_faixa or f"{inicio} a {fim} usuarios"
                    chave_faixa = (produto_codigo, modelo_codigo, inicio, fim)

                    faixas[chave_faixa] = {
                        "produto_codigo": produto_codigo,
                        "modelo_codigo": modelo_codigo,
                        "codigo": faixa_codigo,
                        "nome": faixa_nome,
                        "usuarios_inicio": inicio,
                        "usuarios_fim": fim,
                        "permite_upgrade_manual": True,
                        "descricao": registro.descricao.strip() or faixa_nome,
                        "ordem": 0,
                        "ativo": bool(registro.ativo),
                    }

                precos.append({
                    "produto_codigo": produto_codigo,
                    "modelo_codigo": modelo_codigo,
                    "usuarios_inicio": registro.faixa_inicio,
                    "usuarios_fim": registro.faixa_fim,
                    "valor_mensal": registro.valor_mensal,
                    "valor_setup": registro.valor_setup,
                    "tem_projeto": registro.tem_projeto,
                })

            elif isinstance(registro, RecursoImportado):
                recurso_nome = registro.produto.strip()
                grupo = registro.grupo.strip() or "Outro"
                recurso_codigo = self._slug(f"{grupo}_{recurso_nome}")[:30]
                chave_recurso = (
                    grupo,
                    recurso_nome,
                    registro.modelo.strip(),
                )

                recursos[chave_recurso] = {
                    "codigo": recurso_codigo,
                    "categoria": grupo,
                    "nome": recurso_nome,
                    "descricao": registro.descricao.strip(),
                    "tipo_recurso": self._tipo_recurso_recurso(grupo, recurso_nome),
                    "ativo": bool(registro.ativo),
                    "valor_mensal": registro.valor_mensal,
                    "valor_instalacao": registro.valor_setup,
                    "ordem": 0,
                }

        resultado.categorias = list(categorias.values())
        resultado.produtos = list(produtos.values())
        resultado.modelos = list(modelos.values())
        resultado.faixas = list(faixas.values())
        resultado.recursos = list(recursos.values())
        resultado.precos = precos

        resultado.resumo = {
            "categorias": len(resultado.categorias),
            "produtos": len(resultado.produtos),
            "modelos": len(resultado.modelos),
            "faixas": len(resultado.faixas),
            "recursos": len(resultado.recursos),
            "precos": len(resultado.precos),
            "erros": len(resultado.erros),
            "avisos": len(resultado.avisos),
        }

        return resultado

    @staticmethod
    def _tipo_recurso_recurso(grupo, nome):
        texto = f"{grupo} {nome}".upper()

        if "CPU" in texto or "VCPU" in texto or "PROCESSADOR" in texto:
            return "CPU"

        if "RAM" in texto or "MEMORIA" in texto:
            return "RAM"

        if "NVME" in texto or "DISCO" in texto:
            return "DISCO"

        if "NAS" in texto or "STORAGE" in texto:
            return "STORAGE"

        if "BACKUP" in texto or "SNAPSHOT" in texto:
            return "BACKUP"

        if "WINDOWS" in texto:
            return "LICENCA"

        return "SERVICO"
