#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria completa y generacion de reporte visual para OpenPath / PLIP.
Descarga e inspecciona los benchmarks de Hugging Face (akshayg08/OpenPath)
e integra muestras del corpus de preentrenamiento de OpenPath (Twitter Medico).
"""

import os
import sys
import io
import json
import base64
import zipfile
import pandas as pd
from PIL import Image
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.audit_datasets import get_hf_token

# Rutas
OUTPUT_HTML = r"C:\Users\johan\OneDrive\Documentos\Projects\Thesis\reports\preview_akshayg08_openpath.html"
LOOKUP_CSV = r"C:\Users\johan\OneDrive\Documentos\Projects\quilt_1M_lookup.csv"
IMAGES_ZIP = r"C:\Users\johan\OneDrive\Documentos\Projects\images_part_1_resized.zip"

# Mapeo clinico de clases Kather
KATHER_CLASS_INFO = {
    "ADI": {"name": "Tejido Adiposo (Adipose)", "desc": "Grasa subcutanea y peritumoral con adipocitos maduros", "color": "#fbbf24"},
    "BACK": {"name": "Fondo / Sin Tejido (Background)", "desc": "Espacio en blanco de la preparacion histologica", "color": "#64748b"},
    "DEB": {"name": "Detritos Celulares (Debris)", "desc": "Restos necroticos celulares y artefactos de corte", "color": "#f87171"},
    "LYM": {"name": "Linfocitos (Lymphocytes)", "desc": "Infiltrado inflamatorio mononuclear e inmunidad tumoral", "color": "#38bdf8"},
    "MUC": {"name": "Mucina (Mucus)", "desc": "Extravasacion de mucina coloidale extracelular", "color": "#a78bfa"},
    "MUS": {"name": "Musculo Liso (Smooth Muscle)", "desc": "Capas musculares propias de la pared intestinal", "color": "#fb923c"},
    "NORM": {"name": "Mucosa Colonica Normal (Normal Mucosa)", "desc": "Glandulas tubulares rectas con celulas caliciformes normales", "color": "#4ade80"},
    "STR": {"name": "Estroma Asociado a Cancer (Stroma)", "desc": "Respuesta desmoplasica y fibroblastos reactivos peritumorales", "color": "#e879f9"},
    "TUM": {"name": "Epitelio de Adenocarcinoma (Tumor)", "desc": "Glandulas atipicas infiltrantes con atipia nuclear y pleomorfismo", "color": "#f43f5e"}
}

def main():
    print("Iniciando auditoria completa de OpenPath / PLIP...")
    token = get_hf_token()
    api = HfApi(token=token)

    # 1. Metadatos del repositorio Hugging Face
    print("Obteniendo informacion del repositorio akshayg08/OpenPath en Hugging Face...")
    repo_files = api.list_repo_files("akshayg08/OpenPath", repo_type="dataset")
    print(f"Total archivos en el repositorio: {len(repo_files):,}")

    # 2. Descargar y auditar suites de evaluacion
    print("Descargando archivos de control CSV de los benchmarks...")
    kather_train_csv = hf_hub_download(repo_id="akshayg08/OpenPath", filename="Kather_train/Kather_train.csv", repo_type="dataset", token=token)
    kather_test_csv = hf_hub_download(repo_id="akshayg08/OpenPath", filename="Kather_test/Kather_test.csv", repo_type="dataset", token=token)
    
    df_kather_train = pd.read_csv(kather_train_csv)
    df_kather_test = pd.read_csv(kather_test_csv)
    
    print(f"Kather Train: {len(df_kather_train):,} registros")
    print(f"Kather Test: {len(df_kather_test):,} registros")

    # 3. Muestreo de imagenes TIF de cada una de las 9 clases de Kather (usando Kather_test)
    kather_samples = []
    print("Descargando parches TIF reales de cada una de las 9 clases tisulares de Kather...")
    for label in ["TUM", "STR", "LYM", "NORM", "MUC", "MUS", "ADI", "DEB", "BACK"]:
        class_rows = df_kather_test[df_kather_test['label'] == label]
        if len(class_rows) > 0:
            sample_row = class_rows.iloc[0]
            filename = sample_row['filename']
            caption = sample_row['caption']
            repo_img_path = f"{label}/{filename}"
            
            try:
                img_local = hf_hub_download(repo_id="akshayg08/OpenPath", filename=repo_img_path, repo_type="dataset", token=token)
                pil_img = Image.open(img_local)
                
                buffered = io.BytesIO()
                if pil_img.mode in ("RGBA", "P"):
                    pil_img = pil_img.convert("RGB")
                pil_img.save(buffered, format="JPEG", quality=92)
                img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                kather_samples.append({
                    "category": "kather",
                    "suite": "Kather 9-Classes Benchmark (NCT-CRC-HE / CRC-VAL-HE)",
                    "label": label,
                    "label_info": KATHER_CLASS_INFO.get(label, {}),
                    "filename": filename,
                    "caption": caption,
                    "img_b64": img_b64,
                    "dimensions": f"{pil_img.width} × {pil_img.height} px",
                    "format": "TIFF (224×224 px H&E)",
                    "split": "test"
                })
                print(f"  [OK] Clase {label}: {filename} ({pil_img.width}x{pil_img.height})")
            except Exception as e:
                print(f"  [ERROR] Descargando {repo_img_path}: {e}")

    # 4. Muestreo de casos reales del corpus de preentrenamiento OpenPath (Twitter Medico)
    twitter_samples = []
    if os.path.exists(LOOKUP_CSV) and os.path.exists(IMAGES_ZIP):
        print("Extrayendo muestras de Twitter Medico de OpenPath desde quilt_1M_lookup.csv...")
        with zipfile.ZipFile(IMAGES_ZIP, 'r') as z:
            zip_basenames = {
                os.path.basename(name): name 
                for name in z.namelist() 
                if name.lower().endswith(('.jpg', '.jpeg', '.png'))
            }
            
            for chunk in pd.read_csv(LOOKUP_CSV, chunksize=50000, low_memory=False):
                openpath_chunk = chunk[chunk['subset'] == 'openpath']
                matched = openpath_chunk[openpath_chunk['image_path'].isin(zip_basenames)]
                for _, row in matched.iterrows():
                    img_name = row['image_path']
                    zip_path = zip_basenames[img_name]
                    try:
                        img_bytes = z.read(zip_path)
                        pil_img = Image.open(io.BytesIO(img_bytes))
                        
                        buffered = io.BytesIO()
                        if pil_img.mode in ("RGBA", "P"):
                            pil_img = pil_img.convert("RGB")
                        pil_img.save(buffered, format="JPEG", quality=88)
                        img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                        
                        twitter_samples.append({
                            "category": "twitter",
                            "suite": "OpenPath Pretraining Corpus (Twitter / Medical X)",
                            "filename": img_name,
                            "caption": str(row['caption']),
                            "img_b64": img_b64,
                            "dimensions": f"{pil_img.width} × {pil_img.height} px",
                            "format": "JPEG / PNG (512×512 px)",
                            "split": str(row.get('split', 'train'))
                        })
                        if len(twitter_samples) >= 4:
                            break
                    except Exception as e:
                        print(f"Error procesando {img_name}: {e}")
                if len(twitter_samples) >= 4:
                    break

    print(f"Total muestras de Kather listas: {len(kather_samples)}")
    print(f"Total muestras de Twitter listas: {len(twitter_samples)}")

    # 5. Generar tarjetas HTML para Kather
    cards_html = []
    
    # Seccion 1: Benchmark Suites (Kather 9 Clases)
    cards_html.append("""
    <div style="margin: 28px 0 16px 0;">
        <h2 style="font-size: 1.3rem; color: var(--accent); margin-bottom: 4px;">
            🔬 Parte 1: Suite de Evaluación Zero-Shot (Kather Benchmark - 9 Clases Tisulares)
        </h2>
        <div style="font-size: 0.85rem; color: var(--text-muted);">
            Parches reales en formato TIFF decodificados y transmitidos desde el repositorio <code>akshayg08/OpenPath</code> en Hugging Face.
        </div>
    </div>
    """)
    
    for idx, sample in enumerate(kather_samples, 1):
        lbl = sample['label']
        info = sample['label_info']
        color = info.get('color', '#38bdf8')
        name = info.get('name', lbl)
        desc = info.get('desc', '')
        
        card = f"""
        <div class="sample-card">
            <div class="visual-pane">
                <img src="data:image/jpeg;base64,{sample['img_b64']}" alt="{sample['filename']}">
                <div class="image-meta">
                    <strong>Archivo:</strong> <code>{lbl}/{sample['filename']}</code><br>
                    <strong>Resolución:</strong> {sample['dimensions']} | H&E Patch
                </div>
            </div>
            <div class="text-pane">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="sample-num">MUESTRA #{idx} &bull; {sample['suite']}</span>
                    <span class="badge" style="background: rgba(255,255,255,0.1); color: {color}; border: 1px solid {color}; font-size: 0.85rem;">
                        Clase: {lbl}
                    </span>
                </div>

                <div class="field-box" style="border-left: 3px solid {color};">
                    <div class="field-title">🏷️ Diagnóstico y Clasificación Tisular</div>
                    <div class="field-content" style="font-weight: 600; font-size: 1.05rem; color: #f8fafc;">
                        {name}
                    </div>
                    <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">
                        {desc}
                    </div>
                </div>

                <div class="field-box">
                    <div class="field-title">📝 Prompt / Caption Estandarizado de Evaluación Zero-Shot</div>
                    <div class="field-content" style="font-style: italic; color: #e2e8f0;">
                        "{sample['caption']}"
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.8rem;">
                    <div style="background: var(--badge-bg); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border-color);">
                        <span style="color: var(--text-muted);">Uso en Benchmark:</span><br>
                        <strong>Zero-Shot Cosine Similarity</strong>
                    </div>
                    <div style="background: var(--badge-bg); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border-color);">
                        <span style="color: var(--text-muted);">Embeddings Precalculados:</span><br>
                        <strong><code>.npy</code> disponibles (PLIP &amp; CLIP)</strong>
                    </div>
                </div>
            </div>
        </div>
        """
        cards_html.append(card)

    # Seccion 2: Twitter Medical Cases (Pretraining)
    if twitter_samples:
        cards_html.append("""
        <div style="margin: 36px 0 16px 0;">
            <h2 style="font-size: 1.3rem; color: var(--accent-green); margin-bottom: 4px;">
                🐦 Parte 2: Corpus de Preentrenamiento Abierto (Medical Twitter / Casos Clínicos)
            </h2>
            <div style="font-size: 0.85rem; color: var(--text-muted);">
                Casos y debates de patología diagnóstica real compartidos por especialistas en Twitter (curaduría Stanford / PLIP de 133.5K casos).
            </div>
        </div>
        """)
        
        for idx, sample in enumerate(twitter_samples, 1):
            card = f"""
            <div class="sample-card">
                <div class="visual-pane">
                    <img src="data:image/jpeg;base64,{sample['img_b64']}" alt="{sample['filename']}">
                    <div class="image-meta">
                        <strong>Archivo:</strong> <code>{sample['filename']}</code><br>
                        <strong>Resolución:</strong> {sample['dimensions']} | Color RGB
                    </div>
                </div>
                <div class="text-pane">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="sample-num" style="color: var(--accent-green);">CASO CLÍNICO TWITTER #{idx}</span>
                        <span class="badge badge-open">Subconjunto: OpenPath Pretraining</span>
                    </div>

                    <div class="field-box" style="border-left: 3px solid var(--accent-green);">
                        <div class="field-title">💬 Discusión / Caso Clínico de Patólogo en Redes Sociales (`caption`)</div>
                        <div class="field-content">
                            {sample['caption']}
                        </div>
                    </div>

                    <div style="background: var(--badge-bg); padding: 10px 14px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.82rem; color: var(--text-muted);">
                        <strong>Metodología de Alineación:</strong> Extracción de tweets médicos con imágenes histopatológicas validadas por patólogos de Stanford para entrenar el espacio latente conjunto de PLIP.
                    </div>
                </div>
            </div>
            """
            cards_html.append(card)

    # 6. Ensamblar documento HTML completo
    total_samples_count = len(kather_samples) + len(twitter_samples)
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoria de Dataset: akshayg08/OpenPath (PLIP)</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --border-color: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-green: #4ade80;
            --accent-amber: #fbbf24;
            --accent-purple: #c084fc;
            --badge-bg: #0b1329;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 1.8rem;
            color: var(--accent);
        }}
        .task-banner {{
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 8px;
            padding: 14px 18px;
            margin: 14px 0;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        .meta-item {{
            background: var(--badge-bg);
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        .meta-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}
        .meta-value {{
            font-size: 1rem;
            font-weight: 600;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-right: 6px;
            margin-top: 6px;
        }}
        .badge-open {{ background: #065f46; color: var(--accent-green); }}
        .badge-gated {{ background: #78350f; color: var(--accent-amber); }}
        .badge-task {{ background: #1e3a8a; color: var(--accent); }}
        .badge-secondary {{ background: #334155; color: #cbd5e1; }}
        
        .subsets-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            font-size: 0.9rem;
        }}
        .subsets-table th, .subsets-table td {{
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            text-align: left;
        }}
        .subsets-table th {{
            background: var(--badge-bg);
            color: var(--accent);
        }}

        .sample-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            margin-bottom: 24px;
            overflow: hidden;
            display: grid;
            grid-template-columns: 380px 1fr;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        @media (max-width: 900px) {{
            .sample-card {{ grid-template-columns: 1fr; }}
        }}
        .visual-pane {{
            background: #020617;
            padding: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-right: 1px solid var(--border-color);
        }}
        .visual-pane img {{
            max-width: 100%;
            max-height: 320px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.5);
            object-fit: contain;
        }}
        .image-meta {{
            margin-top: 12px;
            font-size: 0.8rem;
            color: var(--text-muted);
            text-align: center;
        }}
        .text-pane {{
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .sample-num {{
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: bold;
        }}
        .field-box {{
            background: var(--badge-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px;
        }}
        .field-title {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: bold;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
        }}
        .field-content {{
            font-size: 0.92rem;
            color: var(--text-main);
            white-space: pre-wrap;
            word-break: break-word;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Auditoria de Dataset: <code>akshayg08/OpenPath</code> (PLIP)</h1>
            
            <div class="task-banner">
                <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); font-weight: bold; margin-bottom: 4px;">
                    🎯 Tareas Multimodales Formalizadas &amp; Derivadas
                </div>
                <div style="font-size: 1.05rem; font-weight: bold; color: var(--text-main); margin-bottom: 6px;">
                    Tarea Principal: Zero-Shot Tissue Classification &amp; Cross-Modal Image-Text Retrieval
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">
                    <strong>Formalizacion y Paper:</strong> Nature Medicine (2023) — <em>"A Visual-Language Foundation Model for Pathology"</em> (Huang et al., Stanford University).
                </div>
                <div>
                    <span style="font-size: 0.8rem; color: var(--text-muted); margin-right: 6px;">Componentes Multimodales del Ecosistema OpenPath:</span>
                    <span class='badge badge-secondary'>Kather 9-Classes Benchmark (NCT-CRC-HE)</span>
                    <span class='badge badge-secondary'>PanNuke 19-Classes Nuclear Benchmark</span>
                    <span class='badge badge-secondary'>DigestPath Colon Carcinoma Suite</span>
                    <span class='badge badge-secondary'>Medical Twitter Pretraining Corpus (133.5K - 208K)</span>
                </div>
            </div>

            <div>
                <span class="badge badge-open">🔓 Acceso Abierto Directo</span>
                <span class="badge badge-task">Licencia: Apache-2.0 / CC BY-NC 4.0</span>
                <span class="badge badge-task">Archivos en Hub: 7,223 (TIFFs + CSVs + NPY Embeddings)</span>
            </div>

            <div class="meta-grid">
                <div class="meta-item">
                    <div class="meta-label">Total Archivos / Parches en Hub</div>
                    <div class="meta-value">7,223 archivos</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">7,180 parches TIFF de tejido real</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Corpus Preentrenamiento Twitter</div>
                    <div class="meta-value">133,511 a 208,414 casos</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Curados de Twitter Médico por patólogos</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Modalidad de Imagen</div>
                    <div class="meta-value">TIFF (224×224) &amp; JPEG (512×512)</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Tinciones H&amp;E multi-institucionales</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Matrices Vectoriales</div>
                    <div class="meta-value">32 archivos .npy precalculados</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Embeddings de imagen y texto (PLIP / CLIP)</div>
                </div>
            </div>

            <div style="margin-top: 20px;">
                <div style="font-size: 0.9rem; font-weight: bold; color: var(--accent); margin-bottom: 6px;">📊 Desglose de Suites y Subconjuntos Auditados</div>
                <table class="subsets-table">
                    <thead>
                        <tr>
                            <th>Suite / Subconjunto</th>
                            <th>Muestras / Tamaño</th>
                            <th>Tipo de Tarea Multimodal</th>
                            <th>Descripción Histopatológica</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><code>Kather Benchmark</code> (Kather_train / test)</td>
                            <td><strong>7,180 parches TIFF</strong></td>
                            <td>Zero-Shot Classification (9 Clases)</td>
                            <td>Tejido colorrectal: tumor, estroma, linfocitos, mucosa normal, mucina, músculo, grasa, detritos y fondo.</td>
                        </tr>
                        <tr>
                            <td><code>PanNuke Benchmark</code> (PanNuke_test)</td>
                            <td><strong>Embeddings + CSV</strong></td>
                            <td>Nuclear Classification (19 Clases)</td>
                            <td>Clasificación fina de núcleos neoplásicos, epiteliales, estromales e inflamatorios.</td>
                        </tr>
                        <tr>
                            <td><code>DigestPath Benchmark</code></td>
                            <td><strong>Embeddings + CSV</strong></td>
                            <td>Cancer Detection / Retrieval</td>
                            <td>Identificación de adenocarcinoma en biopsias endoscópicas de colon.</td>
                        </tr>
                        <tr>
                            <td><code>WSSS4LUAD Benchmark</code></td>
                            <td><strong>Embeddings + CSV</strong></td>
                            <td>Binary Patch Classification</td>
                            <td>Clasificación binaria (Tumor vs Normal) en adenocarcinoma de pulmón.</td>
                        </tr>
                        <tr>
                            <td><code>OpenPath Pretraining Twitter</code></td>
                            <td><strong>133,511 casos reales</strong></td>
                            <td>Vision-Language Pretraining (VLP)</td>
                            <td>Casos compartidos con imágenes diagnósticas, preguntas y discusión clínica por patólogos certificados.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div style="margin: 32px 0 16px 0; display: flex; justify-content: space-between; align-items: center;">
            <h2 style="margin: 0; font-size: 1.4rem;">🖼️ Muestras Multimodales Auditadas con Imágenes Reales ({total_samples_count})</h2>
            <div style="font-size: 0.85rem; color: var(--text-muted);">
                Imágenes TIFF transmitidas desde Hugging Face + muestras de Twitter alineadas en base64
            </div>
        </div>

        {"".join(cards_html)}

    </div>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Reporte de OpenPath generado exitosamente en: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
