import os, shutil, subprocess, re
from google.colab import userdata

DRIVE = '/content/drive/MyDrive/Proyecto_Mamografias'
USER, REPO = 'a23andres1223-source', 'mamografias-ac'

def verificar(nombre, ok, arreglo=""):
    print(("✅ " if ok else "❌ ") + nombre + ("" if ok else f"  →  {arreglo}"))
    return ok

def respaldar(*archivos):
    os.makedirs(f"{DRIVE}/trabajo", exist_ok=True)
    for a in archivos:
        if os.path.isdir(a):
            shutil.copytree(a, f"{DRIVE}/trabajo/{os.path.basename(a)}", dirs_exist_ok=True)
        else:
            shutil.copy(a, f"{DRIVE}/trabajo/")

def _fila(archivo, campos, clave):
    """Añade una fila a la tabla de un .md; si ya hay una con el mismo texto en la columna `clave`, la reemplaza."""
    lineas = open(archivo, encoding='utf-8').read().split('\n')
    limpio = lambda t: str(t).replace('|', '/').replace('\n', ' ').strip()
    fila = '| ' + ' | '.join(limpio(c) for c in campos) + ' |'
    vacia = re.compile(r'^\|(\s*\|)+\s*$')
    idx_tabla = [i for i, l in enumerate(lineas) if l.startswith('|')]
    # quita filas vacías y filas de ejemplo "(ej.)"
    lineas = [l for l in lineas if not vacia.match(l) and '(ej.)' not in l]
    idx_tabla = [i for i, l in enumerate(lineas) if l.startswith('|')]
    for i in idx_tabla[2:]:
        celdas = [c.strip() for c in lineas[i].strip('|').split('|')]
        if len(celdas) > clave and celdas[clave] == limpio(campos[clave]):
            lineas[i] = fila
            open(archivo, 'w', encoding='utf-8').write('\n'.join(lineas))
            return
    lineas.insert(idx_tabla[-1] + 1, fila)
    open(archivo, 'w', encoding='utf-8').write('\n'.join(lineas))

def anotar(fecha, situacion, alternativas, decision, evidencia, aporte):
    _fila('bitacora.md', [fecha, situacion, alternativas, decision, evidencia, aporte], clave=1)

def registrar_ia(fecha, pregunta, respuesta, contraste, decision):
    _fila('registro_ia.md', [fecha, pregunta, respuesta, contraste, decision], clave=1)

def sh(cmd):
    token = userdata.get('GH_TOKEN')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (r.stdout + r.stderr).replace(token, '***')
    return r.returncode, out

def commit(msg):
    token = userdata.get('GH_TOKEN')
    sh(f'git remote set-url origin https://{USER}:{token}@github.com/{USER}/{REPO}.git')
    sh('git add -A')
    c, o = sh(f'git commit -m "{msg}"')
    if c != 0 and 'nothing to commit' not in o:
        print(o); return False
    c, o = sh('git push origin main')
    if c != 0:
        print(o); print('Push rechazado.'); return False
    print('Commit y push OK:', msg)
    return True
