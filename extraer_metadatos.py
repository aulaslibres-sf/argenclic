import os
import json
from pathlib import Path
from bs4 import BeautifulSoup

def determinar_ciclo(url_relativa):
    """
    Determina el ciclo educativo basándose en la ruta del proyecto
    
    Args:
        url_relativa: Ruta relativa del proyecto (ej: "SEGUNDOCICLO/LENGUA/determin/index.html")
    
    Returns:
        Nombre del ciclo educativo
    """
    if url_relativa == 'index.html':
        return 'Principal'
    
    # Obtener la primera carpeta de la ruta
    carpeta_raiz = url_relativa.split('/')[0]
    
    # Mapeo de carpetas a nombres de ciclos
    ciclos = {
        'INICIAL': 'Nivel Inicial',
        'PRIMERCICLO': 'Primer Ciclo Primaria',
        'SEGUNDOCICLO': 'Segundo Ciclo Primaria',
        'SECUNDARIO': 'Secundaria'
    }
    
    return ciclos.get(carpeta_raiz, 'Sin clasificar')

def extraer_metadatos_jclic(ruta_projects):
    """
    Escanea carpetas de proyectos JClic y extrae metadatos (busca recursivamente)
    Incluye automáticamente el campo 'ciclo' basado en la estructura de carpetas
    
    Args:
        ruta_projects: Ruta a la carpeta /projects/ de tu sitio local
    
    Returns:
        Lista de diccionarios con metadatos de cada proyecto
    """
    proyectos = []
    
    # Convertir a Path para mejor manejo de rutas
    ruta_base = Path(ruta_projects)
    
    # Buscar todos los archivos index.html recursivamente
    archivos_index = list(ruta_base.rglob("index.html"))
    
    print(f"Archivos index.html encontrados: {len(archivos_index)}\n")
    
    for index_html in archivos_index:
        try:
            # Leer el contenido del HTML
            with open(index_html, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Parsear con BeautifulSoup
            soup = BeautifulSoup(contenido, 'html.parser')
            
            # Extraer el título
            titulo_tag = soup.find('title')
            titulo = titulo_tag.text.strip() if titulo_tag else index_html.parent.name
            
            # Intentar extraer descripción (si existe meta description)
            descripcion = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                descripcion = meta_desc['content'].strip()
            
            # Extraer keywords si existen
            keywords = []
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                keywords = [k.strip() for k in meta_keywords['content'].split(',')]
            
            # Construir ruta relativa desde /projects/
            ruta_relativa = index_html.relative_to(ruta_base)
            # Ruta relativa sin prefijo projects/
            url_relativa = ruta_relativa.as_posix()
            
            # Obtener categoría (carpeta padre del proyecto)
            carpeta_padre = index_html.parent.parent.name
            carpeta_proyecto = index_html.parent.name
            
            # Determinar el ciclo educativo
            ciclo = determinar_ciclo(url_relativa)
            
            # Agregar al array
            proyectos.append({
                'titulo': titulo,
                'descripcion': descripcion,
                'url': url_relativa,
                'categoria': carpeta_padre,
                'carpeta': carpeta_proyecto,
                'ciclo': ciclo,
                'keywords': keywords
            })
            
            print(f"✓ [{ciclo}] [{carpeta_padre}] {titulo}")
            
        except Exception as e:
            print(f"✗ Error procesando {index_html}: {e}")
    
    return proyectos

def generar_archivo_js(proyectos, archivo_salida="proyectos-data.js"):
    """
    Genera un archivo JavaScript con los metadatos para el buscador
    """
    # Convertir a formato JavaScript
    js_content = "// Metadatos de proyectos JClic - Generado automáticamente\n"
    js_content += "const proyectosData = " + json.dumps(proyectos, indent=2, ensure_ascii=False) + ";\n\n"
    js_content += "// Para usar en módulos ES6\n"
    js_content += "export default proyectosData;\n"
    
    # Guardar archivo
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\n✓ Archivo generado: {archivo_salida}")

def generar_archivo_json(proyectos, archivo_salida="proyectos-data.json"):
    """
    Genera un archivo JSON con los metadatos
    """
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(proyectos, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Archivo generado: {archivo_salida}")

def mostrar_estadisticas_ciclos(proyectos):
    """
    Muestra estadísticas de distribución por ciclo educativo
    """
    if not proyectos:
        return
    
    # Contar proyectos por ciclo
    ciclos = {}
    for p in proyectos:
        ciclo = p.get('ciclo', 'Sin clasificar')
        ciclos[ciclo] = ciclos.get(ciclo, 0) + 1
    
    print("\n=== Distribución por Ciclo Educativo ===")
    for ciclo in sorted(ciclos.keys()):
        count = ciclos[ciclo]
        porcentaje = (count / len(proyectos)) * 100
        print(f"  • {ciclo}: {count} proyectos ({porcentaje:.1f}%)")

# === USO DEL SCRIPT ===
if __name__ == "__main__":
    # CONFIGURACIÓN: El script se ejecuta desde DENTRO de /projects
    RUTA_PROJECTS = "."
    
    print("=== Extractor de Metadatos JClic (con Ciclos) ===\n")
    
    # Verificar que la carpeta existe
    ruta_absoluta = os.path.abspath(RUTA_PROJECTS)
    print(f"Ruta absoluta: {ruta_absoluta}")
    
    if not os.path.exists(RUTA_PROJECTS):
        print(f"❌ ERROR: La carpeta '{RUTA_PROJECTS}' no existe")
        print(f"\nEstás en: {os.getcwd()}")
        print("\nCarpetas disponibles en el directorio actual:")
        for item in os.listdir('.'):
            if os.path.isdir(item):
                print(f"  📁 {item}")
        print("\n💡 Ajusta la variable RUTA_PROJECTS en el script")
        exit(1)
    
    print(f"Escaneando carpeta: {RUTA_PROJECTS}")
    
    # Listar subcarpetas encontradas
    subcarpetas = [f for f in os.listdir(RUTA_PROJECTS) if os.path.isdir(os.path.join(RUTA_PROJECTS, f))]
    print(f"Subcarpetas encontradas: {len(subcarpetas)}\n")
    
    # Extraer metadatos
    proyectos = extraer_metadatos_jclic(RUTA_PROJECTS)
    
    print(f"\n=== Resumen ===")
    print(f"Total de proyectos encontrados: {len(proyectos)}")
    
    # Mostrar resumen por categoría
    if proyectos:
        categorias = {}
        for p in proyectos:
            cat = p.get('categoria', 'Sin categoría')
            categorias[cat] = categorias.get(cat, 0) + 1
        
        print("\nProyectos por categoría:")
        for cat, count in sorted(categorias.items()):
            print(f"  • {cat}: {count} proyectos")
        
        # Mostrar estadísticas de ciclos
        mostrar_estadisticas_ciclos(proyectos)
    
    # Generar archivos de salida
    if proyectos:
        generar_archivo_js(proyectos, "proyectos-data.js")
        generar_archivo_json(proyectos, "proyectos-data.json")
        
        print("\n✓ Proceso completado exitosamente")
        print(f"\nArchivos generados en: {os.getcwd()}")
        print("\n📋 Campos incluidos en cada proyecto:")
        print("  • titulo")
        print("  • descripcion")
        print("  • url")
        print("  • categoria")
        print("  • carpeta")
        print("  • ciclo (NUEVO)")
        print("  • keywords")
        print("\nPróximos pasos:")
        print("1. Sube los archivos proyectos-data.json y proyectos-data.js")
        print("2. El buscador funcionará con filtros por ciclo educativo")
    else:
        print("\n⚠ No se encontraron proyectos para procesar")
        print("Verifica que las carpetas contengan archivos index.html")
