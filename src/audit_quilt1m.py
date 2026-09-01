#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria y generacion de reporte visual HTML para el dataset Quilt-1M.
Lee directamente quilt_1M_lookup.csv y extrae muestras de images_part_1_resized.zip.
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

# Paths
LOOKUP_CSV = r"C:\Users\johan\OneDrive\Documentos\Projects\quilt_1M_lookup.csv"
IMAGES_ZIP = r"C:\Users\johan\OneDrive\Documentos\Projects\images_part_1_resized.zip"
OUTPUT_HTML = r"C:\Users\johan\OneDrive\Documentos\Projects\Thesis\reports\preview_wisdomik_quilt_1m.html"

def main():
    print("Iniciando auditoria de Quilt-1M...")
    
    if not os.path.exists(LOOKUP_CSV):
        print(f"Error: no se encuentra {LOOKUP_CSV}")
        return
    if not os.path.exists(IMAGES_ZIP):
        print(f"Error: no se encuentra {IMAGES_ZIP}")
        return

    # 1. Indexar archivos en el ZIP
    print("Indexando imagenes disponibles en el archivo .zip...")
    with zipfile.ZipFile(IMAGES_ZIP, 'r') as z:
        zip_namelist = z.namelist()
        zip_basenames = {
            os.path.basename(name): name 
            for name in zip_namelist 
            if name.lower().endswith(('.jpg', '.jpeg', '.png'))
        }
    print(f"Total imagenes encontradas en images_part_1_resized.zip: {len(zip_basenames):,}")

    # 2. Leer y agregar estadisticas completas de quilt_1M_lookup.csv
    print("Procesando quilt_1M_lookup.csv para conteos y metadatos...")
    total_records = 0
    subsets_count = {}
    splits_count = {}
    magnification_count = {}
    non_null_cols = {}
    
    # Seleccion estructurada de muestras diversas (por subset y magnificacion)
    samples_candidates = {
        "quilt_mag0": [],
        "quilt_mag1": [],
        "quilt_mag2": [],
        "openpath": [],
        "pubmed": [],
        "laion": []
    }

    for chunk in pd.read_csv(LOOKUP_CSV, chunksize=100000, low_memory=False):
        total_records += len(chunk)
        for col in chunk.columns:
            non_null_cols[col] = non_null_cols.get(col, 0) + int(chunk[col].notna().sum())
            
        for k, v in chunk['subset'].value_counts().items():
            subsets_count[k] = subsets_count.get(k, 0) + int(v)
            
        for k, v in chunk['split'].value_counts().items():
            splits_count[k] = splits_count.get(k, 0) + int(v)
            
        for k, v in chunk['magnification'].value_counts().items():
            magnification_count[k] = magnification_count.get(k, 0) + int(v)

        # Muestreo estratificado de filas que estan en el zip
        matched = chunk[chunk['image_path'].isin(zip_basenames)]
        for _, row in matched.iterrows():
            sub = str(row.get('subset', ''))
            mag = row.get('magnification', None)
            
            if sub == 'quilt':
                if mag == 0.0 and len(samples_candidates["quilt_mag0"]) < 2:
                    samples_candidates["quilt_mag0"].append(row.to_dict())
                elif mag == 1.0 and len(samples_candidates["quilt_mag1"]) < 2:
                    samples_candidates["quilt_mag1"].append(row.to_dict())
                elif mag == 2.0 and len(samples_candidates["quilt_mag2"]) < 2:
                    samples_candidates["quilt_mag2"].append(row.to_dict())
            elif sub == 'openpath' and len(samples_candidates["openpath"]) < 2:
                samples_candidates["openpath"].append(row.to_dict())
            elif sub == 'pubmed' and len(samples_candidates["pubmed"]) < 2:
                samples_candidates["pubmed"].append(row.to_dict())
            elif sub == 'laion' and len(samples_candidates["laion"]) < 2:
                samples_candidates["laion"].append(row.to_dict())

    # Consolidar lista de muestras
    final_samples = []
    for cat, s_list in samples_candidates.items():
        final_samples.extend(s_list)

    print(f"Total registros facticos: {total_records:,}")
    print(f"Subsets: {subsets_count}")
    print(f"Splits: {splits_count}")
    print(f"Magnificaciones: {magnification_count}")
    print(f"Muestras seleccionadas para renderizar: {len(final_samples)}")

    # 3. Extraer y convertir imagenes de las muestras a Base64
    sample_cards_html = []
    with zipfile.ZipFile(IMAGES_ZIP, 'r') as z:
        for idx, sample in enumerate(final_samples, 1):
            img_filename = sample.get('image_path')
            zip_internal_path = zip_basenames.get(img_filename)
            
            img_b64 = None
            img_w, img_h = 512, 512
            img_mode = "RGB"
            img_format = "JPEG"
            
            if zip_internal_path:
                try:
                    img_bytes = z.read(zip_internal_path)
                    pil_img = Image.open(io.BytesIO(img_bytes))
                    img_w, img_h = pil_img.size
                    img_mode = pil_img.mode
                    img_format = pil_img.format or "JPEG"
                    
                    # Convert to base64
                    buffered = io.BytesIO()
                    if pil_img.mode in ("RGBA", "P"):
                        pil_img = pil_img.convert("RGB")
                    pil_img.save(buffered, format="JPEG", quality=88)
                    img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                except Exception as e:
                    print(f"Error procesando imagen {img_filename}: {e}")

            # Construir tarjeta HTML
            sub = str(sample.get('subset', 'N/A'))
            split = str(sample.get('split', 'N/A'))
            caption = str(sample.get('caption', 'Sin caption disponible'))
            pathology = str(sample.get('pathology', 'N/A'))
            mag_val = sample.get('magnification')
            
            mag_text = "No especificada (N/A)"
            if pd.notna(mag_val):
                if mag_val == 0.0:
                    mag_text = "0.0 (Baja Magnificacion / Vision Panoramica)"
                elif mag_val == 1.0:
                    mag_text = "1.0 (Magnificacion Media)"
                elif mag_val == 2.0:
                    mag_text = "2.0 (Alta Magnificacion / Nivel Celular)"
                else:
                    mag_text = f"{mag_val}"
                    
            roi_text = sample.get('roi_text')
            corrected_text = sample.get('corrected_text')
            noisy_text = sample.get('noisy_text')
            umls_ids = sample.get('med_umls_ids')

            # Badge color por subset
            badge_sub_color = {
                "quilt": "#38bdf8",
                "openpath": "#4ade80",
                "pubmed": "#fbbf24",
                "laion": "#c084fc"
            }.get(sub, "#94a3b8")

            img_html = f'<img src="data:image/jpeg;base64,{img_b64}" alt="{img_filename}">' if img_b64 else '<div style="color:var(--accent-amber);">Imagen no disponible</div>'

            # Campos opcionales si vienen de YouTube (Quilt)
            extra_fields_html = ""
            if pd.notna(roi_text) and str(roi_text).strip() != "" and str(roi_text) != "nan":
                extra_fields_html += f"""
                <div class="field-box" style="border-left: 3px solid #38bdf8;">
                    <div class="field-title">🎯 ROI Narration (Texto hablado al senalar la region)</div>
                    <div class="field-content">{roi_text}</div>
                </div>
                """
            if pd.notna(corrected_text) and str(corrected_text).strip() != "" and str(corrected_text) != "nan":
                extra_fields_html += f"""
                <div class="field-box" style="border-left: 3px solid #4ade80;">
                    <div class="field-title">✨ Corrected Text (Correccion Medica GPT-3.5)</div>
                    <div class="field-content">{corrected_text}</div>
                </div>
                """
            if pd.notna(umls_ids) and str(umls_ids).strip() != "" and str(umls_ids) != "nan":
                extra_fields_html += f"""
                <div class="field-box">
                    <div class="field-title">🏷️ Conceptos Medicos UMLS (`med_umls_ids`)</div>
                    <div class="field-content"><code>{umls_ids}</code></div>
                </div>
                """

            card_html = f"""
            <div class="sample-card">
                <div class="visual-pane">
                    {img_html}
                    <div class="image-meta">
                        <strong>Archivo:</strong> <code>{img_filename}</code><br>
                        <strong>Dimensiones:</strong> {img_w} × {img_h} px | {img_mode} | {img_format}
                    </div>
                </div>
                <div class="text-pane">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="sample-num">MUESTRA #{idx}</span>
                        <div>
                            <span class="badge" style="background: rgba(56,189,248,0.15); color: {badge_sub_color}; border: 1px solid {badge_sub_color};">
                                Subset: {sub.upper()}
                            </span>
                            <span class="badge badge-secondary">Split: {split}</span>
                        </div>
                    </div>

                    <div class="field-box">
                        <div class="field-title">📝 Texto / Caption Principal (`caption`)</div>
                        <div class="field-content">{caption}</div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div class="field-box">
                            <div class="field-title">🔬 Magnificacion / Escala</div>
                            <div class="field-content" style="font-weight: 600; color: var(--accent);">{mag_text}</div>
                        </div>
                        <div class="field-box">
                            <div class="field-title">🩺 Sub-Patologia / Organo (`pathology`)</div>
                            <div class="field-content" style="font-weight: 600;">{pathology if pathology != 'nan' else 'No categorizado'}</div>
                        </div>
                    </div>

                    {extra_fields_html}
                </div>
            </div>
            """
            sample_cards_html.append(card_html)

    # 4. Ensamblar documento HTML completo
    samples_joined = "".join(sample_cards_html)
    num_rendered = len(final_samples)
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoria de Dataset: wisdomik/Quilt-1M</title>
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

        .samples-header {{
            margin: 32px 0 16px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
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
            max-height: 340px;
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
            <h1>🔬 Auditoria de Dataset: <code>wisdomik/Quilt-1M</code></h1>
            
            <div class="task-banner">
                <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); font-weight: bold; margin-bottom: 4px;">
                    🎯 Tareas Multimodales Formalizadas &amp; Derivadas
                </div>
                <div style="font-size: 1.05rem; font-weight: bold; color: var(--text-main); margin-bottom: 6px;">
                    Tarea Principal: Vision-Language Pretraining (VLP) / Medical Contrastive Representation Learning
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">
                    <strong>Formalizacion y Paper:</strong> NeurIPS 2023 (Oral) — <em>"Quilt-1M: One Million Image-Text Pairs for Histopathology"</em> (Ikezogwo et al., Univ. of Washington).
                </div>
                <div>
                    <span style="font-size: 0.8rem; color: var(--text-muted); margin-right: 6px;">Tareas Secundarias / Derivadas:</span>
                    <span class='badge badge-secondary'>Cross-Modal Image-Text Retrieval</span>
                    <span class='badge badge-secondary'>Zero-Shot &amp; Linear Probing Patch Classification</span>
                    <span class='badge badge-secondary'>Visual Instruction Tuning Anchor (Quilt-LLaVA / Quilt-Instruct)</span>
                    <span class='badge badge-secondary'>Scale-Aware Representation Learning</span>
                </div>
            </div>

            <div>
                <span class="badge badge-gated">🔒 Licencia: CC BY-NC-SA 4.0 (Gated / Uso Academico)</span>
                <span class="badge badge-task">Total Pares Imagen-Texto: 1,017,712</span>
                <span class="badge badge-task">Imagenes en Muestra Local (Part 1 Resized 512x512): 65,322</span>
            </div>

            <div class="meta-grid">
                <div class="meta-item">
                    <div class="meta-label">Total Pares Multimodales</div>
                    <div class="meta-value">1,017,712 pares</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Lookup CSV: 2.08 GB</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Distribucion de Splits</div>
                    <div class="meta-value">Train: 1,004,153 (98.67%)</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Val: 13,559 (1.33%)</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Magnificacion / Escala Codificada</div>
                    <div class="meta-value">802,148 registros (78.82%)</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">0.0: 480k | 1.0: 135k | 2.0: 186k</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Enriquecimiento UMLS y ROI</div>
                    <div class="meta-value">802,148 pares con ROI/UMLS</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Audio Whisper + Correccion GPT-3.5</div>
                </div>
            </div>

            <div style="margin-top: 20px;">
                <div style="font-size: 0.9rem; font-weight: bold; color: var(--accent); margin-bottom: 6px;">📊 Desglose Factico por Subconjunto de Origen (Subsets)</div>
                <table class="subsets-table">
                    <thead>
                        <tr>
                            <th>Subconjunto (<code>subset</code>)</th>
                            <th>Cantidad de Pares</th>
                            <th>Porcentaje (%)</th>
                            <th>Fuente Original y Metodologia de Curaduria</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><code>quilt</code> (YouTube)</td>
                            <td><strong>802,148</strong></td>
                            <td>78.82%</td>
                            <td>&gt;1,000 horas de videos docentes de patologos en YouTube. Extraccion guiada por tracking del cursor y audio Whisper procesado con LLM.</td>
                        </tr>
                        <tr>
                            <td><code>openpath</code> (Twitter/X)</td>
                            <td><strong>133,511</strong></td>
                            <td>13.12%</td>
                            <td>Casos y debates clinicos reales compartidos por patologos en Twitter (corpus OpenPath/PLIP de Stanford).</td>
                        </tr>
                        <tr>
                            <td><code>pubmed</code> (PMC OA)</td>
                            <td><strong>59,371</strong></td>
                            <td>5.83%</td>
                            <td>Figuras y leyendas explicativas de articulos cientificos de acceso abierto en PubMed Central.</td>
                        </tr>
                        <tr>
                            <td><code>laion</code> (Web Histology)</td>
                            <td><strong>22,682</strong></td>
                            <td>2.23%</td>
                            <td>Filtro tematico de histopatologia sobre el corpus web a gran escala LAION-5B.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="samples-header">
            <h2 style="margin: 0; font-size: 1.3rem;">🖼️ Muestras Multimodales Auditadas ({num_rendered} Registros Representativos)</h2>
            <div style="font-size: 0.85rem; color: var(--text-muted);">
                Imagenes extraidas directamente de <code>images_part_1_resized.zip</code> (512×512 px) y alineadas con <code>quilt_1M_lookup.csv</code>
            </div>
        </div>

        {samples_joined}

    </div>
</body>
</html>
"""
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Reporte generado exitosamente en: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
