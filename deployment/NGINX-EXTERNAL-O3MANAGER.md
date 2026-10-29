# Nginx externo do O3Cloud Manager

Topologia validada em producao em 29/10/2026:

`Cloudflare -> Nginx externo 10.10.10.2 -> Nginx local 10.10.10.210:80 -> Gunicorn 127.0.0.1:5000`

O Nginx externo possui o IP publico `177.104.183.61`. O MariaDB esta isolado
em `10.10.10.209` e aceita a aplicacao em `10.10.10.210`.

## 1. CSP especifica

O arquivo global `/etc/nginx/custom/security.conf` contem uma CSP generica com
`unsafe-eval`. Para o virtual host do O3Manager, use uma copia sem a diretiva
`Content-Security-Policy`. A aplicacao ja entrega sua propria CSP.

Exemplo de preparacao no proxy externo:

```bash
sudo cp -a /etc/nginx/custom/security.conf /etc/nginx/custom/security-o3manager.conf
sudo sed -i '/Content-Security-Policy/d' /etc/nginx/custom/security-o3manager.conf
```

No arquivo `/etc/nginx/conf.d/o3manager.o3cloud.com.br.conf`, troque somente:

```nginx
include /etc/nginx/custom/security.conf;
```

por:

```nginx
include /etc/nginx/custom/security-o3manager.conf;
```

## 2. IP real pela Cloudflare

Configure `set_real_ip_from` para todas as redes oficiais IPv4 e IPv6 da
Cloudflare, use `real_ip_header CF-Connecting-IP` e habilite
`real_ip_recursive on`. As listas oficiais devem ser consultadas em
`https://www.cloudflare.com/ips/`; nao mantenha uma copia antiga sem revisao.

Depois que o modulo Real IP estiver configurado, use no `location /`:

```nginx
proxy_pass http://10.10.10.210;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Forwarded-Proto https;
```

O acesso direto ao origin publico deve ser limitado aos enderecos da
Cloudflare. Isso impede que um cliente externo falsifique os cabecalhos usados
para auditoria e rate limit.

No virtual host do O3Manager, o limite de upload validado em producao e:

```nginx
client_max_body_size 10M;
```

Na Cloudflare, foi criada uma Configuration Rule restrita ao hostname:

```text
Nome: SSL estrito - O3Manager
Hostname: o3manager.o3cloud.com.br
SSL/TLS encryption mode: Strict
```

## 3. Validacao

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I https://o3manager.o3cloud.com.br/login
curl https://o3manager.o3cloud.com.br/.well-known/security.txt
```

O resultado esperado e uma unica CSP, sem `unsafe-eval`, e `Canonical` com
`https://`.
