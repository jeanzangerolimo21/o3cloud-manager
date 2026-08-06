import csv,io,re,unicodedata
from pathlib import Path
FIELD_LABELS={"nome":"Nome","telefone":"Telefone","email":"E-mail","empresa":"Empresa","cnpj":"CNPJ"}
ALIASES={"nome":{"nome","nomecompleto","nomeparticipante","participante","contato","nomecontato","name"},"telefone":{"telefone","telefonepessoal","telefonecomercial","celular","whatsapp","fone","phone","tel","foneempresa"},"email":{"email","emailcontato","emailaddress","mail"},"empresa":{"empresa","nomeempresa","razaosocial","razaosocialempresa","fantasia","nomefantasia","company","organizacao","organization"},"cnpj":{"cnpj","cnpjempresa","documento","taxid"}}
def normalizar_coluna(v):
 v=unicodedata.normalize("NFKD",str(v or "")).encode("ascii","ignore").decode();return re.sub(r"[^a-z0-9]","",v.lower())
def txt(v):
 if v is None:return ""
 if isinstance(v,float) and v.is_integer():return str(int(v))
 return str(v).strip()
def read_rows(fs):
 ext=Path(fs.filename or "").suffix.lower()
 if ext not in {".csv",".xls",".xlsx"}:raise ValueError("Formato inválido. Envie CSV, XLS ou XLSX.")
 b=fs.read()
 if ext==".csv":
  for enc in ("utf-8-sig","cp1252","latin-1"):
   try:t=b.decode(enc);break
   except UnicodeDecodeError:continue
  try:d=csv.Sniffer().sniff(t[:4096],delimiters=";,\t|,")
  except csv.Error:d=csv.excel;d.delimiter=";"
  rows=list(csv.reader(io.StringIO(t),d))
 else:
  try:
   if ext==".xlsx":
    import openpyxl; w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True);rows=[[txt(v) for v in r] for r in w.active.iter_rows(values_only=True)]
   else:
    import xlrd; w=xlrd.open_workbook(file_contents=b,on_demand=True);s=w.sheet_by_index(0);rows=[[txt(s.cell_value(r,c)) for c in range(s.ncols)] for r in range(s.nrows)]
  except ImportError:raise ValueError("Dependência não instalada: "+("openpyxl" if ext==".xlsx" else "xlrd"))
  except Exception as e:raise ValueError("Não foi possível ler a planilha: "+str(e))
 rows=[[txt(v) for v in r] for r in rows];rows=[r for r in rows if any(r)]
 if len(rows)<2:raise ValueError("A planilha precisa de cabeçalho e dados.")
 n=max(map(len,rows));return ext,[r+[""]*(n-len(r)) for r in rows]
def suggest_mapping(headers):
 m={}
 for f,a in ALIASES.items():
  hit=[i for i,h in enumerate(headers) if normalizar_coluna(h) in a];m[f]=hit[0] if hit else ""
 return m
def digits(v):return re.sub(r"\D","",txt(v))
def cnpj(v):
 raw=re.sub(r"[^A-Za-z0-9]","",txt(v)).upper()
 if not raw:return ""
 if len(raw)!=14 or len(set(raw))==1:return None
 if re.search(r"[A-Z]",raw):return raw
 for weights in ([5,4,3,2,9,8,7,6,5,4,3,2],[6,5,4,3,2,9,8,7,6,5,4,3,2]):
  total=sum(int(raw[i])*weights[i] for i in range(len(weights)))
  check=(total*10)%11
  if check==10:check=0
  if check!=int(raw[len(weights)]):return None
 return raw
def key(r):
 if r["email"]:return "email:"+r["email"]
 if r["telefone"]:return "telefone:"+r["telefone"]
 return "nome:"+normalizar_coluna(r["nome"])+"|empresa:"+normalizar_coluna(r["empresa"])
def validate_rows(rows,mapping,existing_keys=()):
 seen=set();out=[];existing=set(existing_keys)
 for no,raw in enumerate(rows[1:],2):
  def val(f):return txt(raw[int(mapping[f])]) if str(mapping.get(f,"")).isdigit() else ""
  r={"linha":no,"nome":val("nome")[:150],"telefone":digits(val("telefone"))[:30],"email":val("email").lower()[:150],"empresa":val("empresa")[:150],"cnpj":cnpj(val("cnpj")),"erros":[]}
  if not r["nome"]:r["erros"].append("Nome não informado")
  if not r["email"] and not r["telefone"]:r["erros"].append("Informe e-mail ou telefone")
  if r["email"] and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",r["email"]):r["erros"].append("E-mail inválido")
  if val("cnpj") and r["cnpj"] is None:r["erros"].append("CNPJ inválido");r["cnpj"]=""
  r["chave_deduplicacao"]=key(r)
  if r["chave_deduplicacao"] in seen or r["chave_deduplicacao"] in existing:r["erros"].append("Registro duplicado neste evento")
  seen.add(r["chave_deduplicacao"]);r["valido"]=not r["erros"];out.append(r)
 return out
