from html import escape

from flask import current_app, has_app_context


class ProxmoxAgendamentoEmailBuilder:
    @classmethod
    def cadastro(cls, agendamento):
        assunto = f"[O3Cloud Manager] Agendamento Proxmox #{agendamento.get('id')} criado"
        resumo = "Seu agendamento foi registrado e será executado automaticamente no horário programado."
        return assunto, cls._texto(agendamento, "Agendamento criado", resumo), cls._html(agendamento, "Agendamento criado", resumo, "Agendado")

    @classmethod
    def inicio(cls, agendamento):
        assunto = f"[O3Cloud Manager] Agendamento Proxmox #{agendamento.get('id')} em execução"
        resumo = "O worker iniciou a execução e está validando o estado atual da VM no Proxmox."
        return assunto, cls._texto(agendamento, "Execução iniciada", resumo), cls._html(agendamento, "Execução iniciada", resumo, "Em execução")

    @classmethod
    def final(cls, agendamento, sucesso=True, mensagem_erro=None):
        status = "concluído com sucesso" if sucesso else "falhou"
        assunto = f"[O3Cloud Manager] Agendamento Proxmox #{agendamento.get('id')} {status}"
        if sucesso:
            titulo = "Agendamento concluído"
            resumo = "O upgrade foi aplicado e validado no Proxmox."
            selo = "Concluído"
        else:
            titulo = "Agendamento com falha"
            resumo = "A execução foi interrompida e o detalhe do erro está registrado no histórico do agendamento."
            selo = "Falha"
        return (
            assunto,
            cls._texto(agendamento, titulo, resumo, mensagem_erro=mensagem_erro),
            cls._html(agendamento, titulo, resumo, selo, mensagem_erro=mensagem_erro, sucesso=sucesso),
        )

    @classmethod
    def _texto(cls, agendamento, titulo, resumo, mensagem_erro=None):
        linhas = [
            titulo,
            "",
            resumo,
            "",
            "Resumo do agendamento",
            f"Agendamento: #{agendamento.get('id')}",
            f"Execução programada: {cls._data(agendamento.get('executar_em'))}",
            f"Criado por: {agendamento.get('created_by') or '-'}",
            "",
            "Ambiente",
            f"Cluster: {agendamento.get('integracao_nome') or agendamento.get('cluster_nome') or '-'}",
            f"Node: {agendamento.get('node_nome') or '-'}",
            f"VMID: {agendamento.get('vmid') or '-'}",
            f"VM: {agendamento.get('vm_nome') or '-'}",
            f"Status da VM: {cls._status_vm(agendamento)}",
            "",
            "Alterações",
            f"CPU atual: {cls._cpu_topologia(agendamento.get('cpu_original'), agendamento.get('cpu_sockets_original'), agendamento.get('cpu_cores_por_socket_original'))}",
            f"CPU desejada: {cls._cpu_desejada(agendamento)}",
            f"CPU final: {cls._cpu_topologia(agendamento.get('cpu_final'), agendamento.get('cpu_sockets_final'), agendamento.get('cpu_cores_por_socket_final'))}",
            f"Memória atual: {cls._memoria_gb(agendamento.get('memoria_original_mb'))}",
            f"Memória desejada: {cls._memoria_gb(agendamento.get('memoria_nova_mb'), vazio='sem alteração')}",
            f"Memória final: {cls._memoria_gb(agendamento.get('memoria_final_mb'))}",
            "",
            f"Desligar se necessário: {cls._sim_nao(agendamento.get('desligar_se_necessario'))}",
            f"Religar automaticamente: {cls._sim_nao(agendamento.get('religar_automaticamente'))}",
            f"Motivo: {agendamento.get('motivo') or '-'}",
        ]
        erro = mensagem_erro or agendamento.get('mensagem_erro')
        if erro:
            linhas.extend(["", f"Erro: {erro}"])
        link = cls._link(agendamento)
        if link:
            linhas.extend(["", f"Acompanhar no O3Cloud Manager: {link}"])
        return "\n".join(linhas)

    @classmethod
    def _html(cls, agendamento, titulo, resumo, selo, mensagem_erro=None, sucesso=None):
        erro = mensagem_erro or agendamento.get('mensagem_erro')
        link = cls._link(agendamento)
        cor_selo = "#198754" if sucesso is True else "#dc3545" if sucesso is False else "#0d6efd"
        erro_html = ""
        if erro:
            erro_html = f'''
                <div style="background:#fff5f5;border:1px solid #f5c2c7;border-radius:8px;padding:14px 16px;margin:18px 0;color:#842029;">
                  <div style="font-size:12px;text-transform:uppercase;font-weight:700;margin-bottom:6px;">Erro registrado</div>
                  <div style="font-size:14px;line-height:1.5;">{escape(str(erro))}</div>
                </div>
            '''
        botao_html = ""
        rodape_link = ""
        if link:
            link_html = escape(link)
            botao_html = f'''<p style="margin:24px 0 0;"><a href="{link_html}" style="display:inline-block;background:#0d6efd;color:#ffffff;text-decoration:none;font-weight:700;border-radius:6px;padding:12px 18px;font-size:14px;">Abrir agendamento</a></p>'''
            rodape_link = f'''<p style="margin:14px 4px 0;font-size:12px;line-height:1.5;color:#667085;">Se o botão não abrir, copie e cole este link no navegador:<br><a href="{link_html}" style="color:#0d6efd;">{link_html}</a></p>'''
        return f'''
        <div style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;color:#17202a;">
          <div style="max-width:720px;margin:0 auto;padding:28px 16px;">
            <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
              <div style="padding:22px 26px;border-bottom:1px solid #eef0f2;">
                <div style="font-size:13px;color:#667085;text-transform:uppercase;letter-spacing:.04em;">O3Cloud Manager - Proxmox</div>
                <h2 style="margin:8px 0 0;font-size:22px;line-height:1.3;color:#101828;">{escape(titulo)}</h2>
                <span style="display:inline-block;margin-top:12px;background:{cor_selo};color:#ffffff;border-radius:999px;padding:5px 10px;font-size:12px;font-weight:700;">{escape(selo)}</span>
              </div>
              <div style="padding:26px;">
                <p style="margin:0 0 18px;font-size:15px;line-height:1.6;">{escape(resumo)}</p>
                {cls._bloco_html('Resumo do agendamento', [
                    ('Agendamento', '#' + str(agendamento.get('id') or '-')),
                    ('Execução programada', cls._data(agendamento.get('executar_em'))),
                    ('Criado por', agendamento.get('created_by') or '-'),
                ])}
                {cls._bloco_html('Ambiente', [
                    ('Cluster', agendamento.get('integracao_nome') or agendamento.get('cluster_nome') or '-'),
                    ('Node', agendamento.get('node_nome') or '-'),
                    ('VMID', agendamento.get('vmid') or '-'),
                    ('VM', agendamento.get('vm_nome') or '-'),
                    ('Status da VM', cls._status_vm(agendamento)),
                ])}
                {cls._bloco_html('Alterações solicitadas', [
                    ('CPU atual', cls._cpu_topologia(agendamento.get('cpu_original'), agendamento.get('cpu_sockets_original'), agendamento.get('cpu_cores_por_socket_original'))),
                    ('CPU desejada', cls._cpu_desejada(agendamento)),
                    ('CPU final', cls._cpu_topologia(agendamento.get('cpu_final'), agendamento.get('cpu_sockets_final'), agendamento.get('cpu_cores_por_socket_final'))),
                    ('Memória atual', cls._memoria_gb(agendamento.get('memoria_original_mb'))),
                    ('Memória desejada', cls._memoria_gb(agendamento.get('memoria_nova_mb'), vazio='sem alteração')),
                    ('Memória final', cls._memoria_gb(agendamento.get('memoria_final_mb'))),
                ])}
                {cls._bloco_html('Política de execução', [
                    ('Desligar se necessário', cls._sim_nao(agendamento.get('desligar_se_necessario'))),
                    ('Religar automaticamente', cls._sim_nao(agendamento.get('religar_automaticamente'))),
                    ('Motivo', agendamento.get('motivo') or '-'),
                ])}
                {erro_html}
                {botao_html}
              </div>
            </div>
            {rodape_link}
          </div>
        </div>
        '''

    @staticmethod
    def _bloco_html(titulo, linhas):
        rows = []
        for chave, valor in linhas:
            rows.append(f'''
              <tr>
                <td style="padding:8px 12px;border-bottom:1px solid #eef0f2;color:#667085;font-size:13px;width:36%;">{escape(str(chave))}</td>
                <td style="padding:8px 12px;border-bottom:1px solid #eef0f2;color:#101828;font-size:14px;font-weight:600;">{escape(str(valor or '-'))}</td>
              </tr>
            ''')
        return f'''
          <div style="border:1px solid #e5e7eb;border-radius:8px;margin:18px 0;overflow:hidden;">
            <div style="background:#f8fafc;padding:10px 12px;font-size:13px;font-weight:700;color:#344054;">{escape(titulo)}</div>
            <table role="presentation" cellspacing="0" cellpadding="0" style="width:100%;border-collapse:collapse;">{''.join(rows)}</table>
          </div>
        '''

    @classmethod
    def _cpu_desejada(cls, agendamento):
        cpu = agendamento.get('cpu_nova')
        if not cpu:
            return 'sem alteração'
        sockets = int(agendamento.get('cpu_sockets_original') or 1)
        cpu = int(cpu)
        if sockets > 1 and cpu % sockets != 0:
            return f"{cpu} vCPU (será aplicado como 1 socket x {cpu} core(s))"
        cores = int(cpu / sockets) if sockets else cpu
        return f"{cpu} vCPU ({sockets} socket(s) x {cores} core(s))"

    @staticmethod
    def _cpu_topologia(cpu_total, sockets=None, cores_por_socket=None):
        if not cpu_total:
            return '-'
        if sockets and cores_por_socket:
            return f"{cpu_total} vCPU ({sockets} socket(s) x {cores_por_socket} core(s))"
        return f"{cpu_total} vCPU"

    @staticmethod
    def _memoria_gb(memoria_mb, vazio='-'):
        if not memoria_mb:
            return vazio
        return f"{round(float(memoria_mb) / 1024, 2)} GB"

    @staticmethod
    def _status_vm(agendamento):
        original = agendamento.get('status_original') or '-'
        final = agendamento.get('status_final')
        return f"{original} -> {final}" if final else original

    @staticmethod
    def _sim_nao(valor):
        return 'Sim' if bool(valor) else 'Não'

    @staticmethod
    def _data(valor):
        if not valor:
            return '-'
        if hasattr(valor, 'strftime'):
            return valor.strftime('%d/%m/%Y %H:%M')
        return str(valor)

    @staticmethod
    def _link(agendamento):
        if not has_app_context():
            return None
        base = (current_app.config.get('PUBLIC_BASE_URL') or '').rstrip('/')
        if not base or not agendamento.get('id'):
            return None
        return f"{base}/infraestrutura/agendamentos/{agendamento.get('id')}"
