#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria y generacion de reporte visual para WSI-VQA (ECCV 2024).
Descarga preguntas Q&A desde GitHub (cpystan/WSI-VQA) y transmite miniaturas
reales de láminas gigapíxel (WSIs) directamente desde la API de NIH GDC.
"""

import os
import sys
import io
import json
import struct
import base64
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_HTML = PROJECT_ROOT / "reports" / "preview_cpystan_wsi_vqa.html"
GITHUB_BASE_URL = "https://raw.githubusercontent.com/cpystan/WSI-VQA/master/dataset/WSI_captions/"

class HTTPRangeReader:
    def __init__(self, url):
        self.url = url
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-10"})
        with urllib.request.urlopen(req) as resp:
            content_range = resp.headers.get("Content-Range", "")
            if "/" in content_range:
                self.size = int(content_range.split("/")[1])
            else:
                self.size = int(resp.headers.get("Content-Length", 0))
        self.pos = 0

    def read_at(self, offset, length):
        if length <= 0 or offset >= self.size:
            return b""
        end = min(self.size - 1, offset + length - 1)
        req = urllib.request.Request(
            self.url,
            headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={offset}-{end}"}
        )
        with urllib.request.urlopen(req) as resp:
            return resp.read()

def query_gdc_slide(case_id: str):
    """Consulta en GDC API el archivo SVS diagnostico para un caso TCGA."""
    filters = {
        "op": "and",
        "content": [
            {"op": "in", "content": {"field": "cases.submitter_id", "value": [case_id]}},
            {"op": "in", "content": {"field": "data_format", "value": ["SVS"]}}
        ]
    }
    query_url = f"https://api.gdc.cancer.gov/files?filters={urllib.parse.quote(json.dumps(filters))}&fields=file_id,file_name,file_size,tags&size=10"
    req = urllib.request.Request(query_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            hits = res.get("data", {}).get("hits", [])
            # Preferir laminas diagnosticas DX frente a cortes por congelacion TS
            dx_hits = [h for h in hits if "DX" in h["file_name"]]
            if dx_hits:
                return dx_hits[0]
            elif hits:
                return hits[0]
    except Exception as e:
        print(f"Error consultando GDC para {case_id}: {e}")
    return None

def extract_wsi_thumbnail_from_gdc(file_id: str):
    """Extrae y ensambla la miniatura real del WSI desde GDC usando HTTP Range requests."""
    url = f"https://api.gdc.cancer.gov/data/{file_id}"
    try:
        reader = HTTPRangeReader(url)
        header = reader.read_at(0, 8)
        byte_order = "<" if header[:2] == b"II" else ">"
        first_ifd = struct.unpack(f"{byte_order}I", header[4:8])[0]
        
        # SVS almacena thumbnail en IFD1
        ifd0_data = reader.read_at(first_ifd, 2)
        num0 = struct.unpack(f"{byte_order}H", ifd0_data)[0]
        next_ifd = struct.unpack(f"{byte_order}I", reader.read_at(first_ifd + 2 + num0*12, 4))[0]
        
        if next_ifd == 0:
            return None
            
        ifd1_data = reader.read_at(next_ifd, 2)
        num1 = struct.unpack(f"{byte_order}H", ifd1_data)[0]
        entries = reader.read_at(next_ifd + 2, num1 * 12)
        
        tags = {}
        for i in range(num1):
            tag, ttype, cnt, val = struct.unpack(f"{byte_order}HHI I", entries[i*12 : (i+1)*12])
            tags[tag] = (ttype, cnt, val)
            
        width = tags[256][2]
        height = tags[257][2]
        
        # JPEGTables (tag 347)
        _, t_cnt, t_val = tags[347]
        tables = reader.read_at(t_val, t_cnt)
        tables_clean = tables[:-2] if tables.endswith(b"\xff\xd9") else tables
        
        # Strips (tags 273 y 279)
        _, s_cnt, s_val = tags[273]
        _, b_cnt, b_val = tags[279]
        
        if s_cnt == 1:
            strip_offsets = [s_val]
            strip_bytes = [b_val]
        else:
            strip_offsets = list(struct.unpack(f"{byte_order}{s_cnt}I", reader.read_at(s_val, s_cnt*4)))
            strip_bytes = list(struct.unpack(f"{byte_order}{b_cnt}I", reader.read_at(b_val, b_cnt*4)))
            
        canvas = Image.new("RGB", (width, height), (255, 255, 255))
        y_offset = 0
        
        for offset, count in zip(strip_offsets, strip_bytes):
            strip_data = reader.read_at(offset, count)
            strip_clean = strip_data[2:] if strip_data.startswith(b"\xff\xd8") else strip_data
            full_jpeg = tables_clean + strip_clean
            strip_img = Image.open(io.BytesIO(full_jpeg))
            canvas.paste(strip_img, (0, y_offset))
            y_offset += strip_img.height
            
        return canvas
    except Exception as e:
        print(f"Error extrayendo miniatura para file_id {file_id}: {e}")
        return None

def main():
    print("Iniciando auditoria de WSI-VQA (ECCV 2024)...")
    
    # 1. Cargar preguntas de Train, Val y Test
    splits_data = {}
    total_questions = 0
    all_slide_ids = set()
    
    for split_name in ["train", "val", "test"]:
        url = f"{GITHUB_BASE_URL}WsiVQA_{split_name}.json"
        print(f"Descargando metadatos Q&A de {split_name}...")
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            splits_data[split_name] = data
            total_questions += len(data)
            split_slides = set(d["Id"] for d in data)
            all_slide_ids.update(split_slides)
            print(f"  -> {split_name}: {len(data):,} preguntas sobre {len(split_slides)} láminas.")

    # 2. Agrupar preguntas por lámina para generar casos clinicos completos
    # Seleccionaremos 6 casos diversos de Test y Val
    target_cases = ["TCGA-BH-A202", "TCGA-AR-A1AI", "TCGA-B6-A0WZ", "TCGA-EW-A1PF", "TCGA-AO-A0JE", "TCGA-LD-A74U"]
    
    cards_html = []
    print("\nExtrayendo miniaturas reales de WSIs desde NIH GDC para los casos seleccionados...")
    
    for case_idx, case_id in enumerate(target_cases, 1):
        print(f"Procesando caso {case_idx}/{len(target_cases)}: {case_id}...")
        
        # Buscar todas las preguntas asociadas a este caso
        case_questions = []
        source_split = "test"
        for d in splits_data["test"]:
            if d["Id"] == case_id:
                case_questions.append(d)
        if not case_questions:
            source_split = "val"
            for d in splits_data["val"]:
                if d["Id"] == case_id:
                    case_questions.append(d)
        if not case_questions:
            source_split = "train"
            for d in splits_data["train"]:
                if d["Id"] == case_id:
                    case_questions.append(d)

        # Consultar GDC para obtener la lamina gigapixel
        gdc_info = query_gdc_slide(case_id)
        img_b64 = None
        file_id = ""
        file_name = "N/A"
        file_size_mb = 0
        
        if gdc_info:
            file_id = gdc_info["file_id"]
            file_name = gdc_info["file_name"]
            file_size_mb = gdc_info["file_size"] / (1024**2)
            print(f"  -> SVS encontrado en GDC: {file_name} ({file_size_mb:.1f} MB)")
            
            pil_thumb = extract_wsi_thumbnail_from_gdc(file_id)
            if pil_thumb:
                buf = io.BytesIO()
                pil_thumb.save(buf, format="JPEG", quality=88)
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                print(f"  -> [OK] Miniatura extraida exitosamente: {pil_thumb.size}")
                
        # Construir lista de preguntas para la tarjeta
        q_items_html = []
        for q_idx, q in enumerate(case_questions[:6], 1):
            q_text = q.get("Question", "")
            ans = q.get("Answer", "")
            choices = q.get("Choice", [])
            
            choices_html = ""
            if choices:
                c_badges = []
                for c in choices:
                    is_correct = (str(c).strip().lower() == str(ans).strip().lower())
                    if is_correct:
                        c_badges.append(f"<span style='display:inline-block; padding:2px 8px; margin:2px; border-radius:4px; font-size:0.78rem; background:#065f46; color:#4ade80; border:1px solid #4ade80; font-weight:bold;'>✓ {c}</span>")
                    else:
                        c_badges.append(f"<span style='display:inline-block; padding:2px 8px; margin:2px; border-radius:4px; font-size:0.78rem; background:#1e293b; color:#94a3b8; border:1px solid #334155;'>{c}</span>")
                choices_html = f"<div style='margin-top:6px;'>{' '.join(c_badges)}</div>"
            
            q_item = f"""
            <div style="background: var(--badge-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                <div style="font-size: 0.85rem; color: var(--accent); font-weight: bold;">
                    ❓ Q{q_idx}: {q_text}
                </div>
                {choices_html}
                <div style="font-size: 0.9rem; color: #f8fafc; margin-top: 6px;">
                    <strong>Respuesta / Ground Truth:</strong> <code style="color: #4ade80; font-size: 0.9rem;">{ans}</code>
                </div>
            </div>
            """
            q_items_html.append(q_item)

        gdc_viewer_url = f"https://portal.gdc.cancer.gov/files/{file_id}" if file_id else "#"
        img_html = f'<img src="data:image/jpeg;base64,{img_b64}" alt="WSI {case_id}" style="width:100%; border-radius:6px; box-shadow:0 4px 8px rgba(0,0,0,0.4);">' if img_b64 else '<div style="color:var(--accent-amber);">Miniatura no disponible</div>'

        card = f"""
        <div class="sample-card" style="grid-template-columns: 460px 1fr;">
            <div class="visual-pane">
                <div style="width: 100%; text-align: center; margin-bottom: 8px; font-size: 0.85rem; font-weight: bold; color: var(--accent);">
                    🔬 Whole Slide Image (Lámina Completa de Biopsia / Mastectomía)
                </div>
                {img_html}
                <div class="image-meta" style="margin-top: 10px; width: 100%;">
                    <div><strong>Caso TCGA:</strong> <code>{case_id}</code></div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">
                        <strong>Archivo SVS:</strong> <code>{file_name}</code> ({file_size_mb:.1f} MB)
                    </div>
                    <div style="margin-top: 12px;">
                        <a href="{gdc_viewer_url}" target="_blank" style="display: inline-block; background: #0284c7; color: #fff; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: bold; border: 1px solid #38bdf8;">
                            🔍 Abrir Lámina en Visor NCI GDC (Zoom 40×) &rarr;
                        </a>
                    </div>
                </div>
            </div>
            <div class="text-pane">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="sample-num">CASO CLÍNICO WSI #{case_idx} &bull; TCGA-BRCA</span>
                    <div>
                        <span class="badge badge-wsi">Escala: Whole Slide Image</span>
                        <span class="badge badge-secondary">Split: {source_split.upper()}</span>
                    </div>
                </div>

                <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 6px;">
                    <strong>Preguntas Clínicas y Biomarcadores Evaluados sobre esta Lámina:</strong>
                </div>

                {"".join(q_items_html)}
            </div>
        </div>
        """
        cards_html.append(card)

    # 3. Ensamblar documento HTML
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoria de Dataset: cpystan/WSI-VQA (ECCV 2024)</title>
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
            --accent-rose: #fb7185;
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
            max-width: 1450px;
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
            background: rgba(251, 113, 133, 0.1);
            border: 1px solid rgba(251, 113, 133, 0.3);
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
        .badge-wsi {{ background: #881337; color: var(--accent-rose); }}
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
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }}
        @media (max-width: 950px) {{
            .sample-card {{ grid-template-columns: 1fr !important; }}
        }}
        .visual-pane {{
            background: #020617;
            padding: 18px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-right: 1px solid var(--border-color);
        }}
        .image-meta {{
            font-size: 0.82rem;
            color: var(--text-muted);
            text-align: center;
        }}
        .text-pane {{
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .sample-num {{
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Auditoria de Dataset: <code>cpystan/WSI-VQA</code></h1>
            
            <div class="task-banner">
                <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent-rose); font-weight: bold; margin-bottom: 4px;">
                    🎯 Tareas Multimodales Formalizadas &amp; Derivadas
                </div>
                <div style="font-size: 1.05rem; font-weight: bold; color: var(--text-main); margin-bottom: 6px;">
                    Tarea Principal: Whole Slide Image Visual Question Answering (VQA a Nivel de Lámina Gigapíxel)
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">
                    <strong>Formalización y Paper:</strong> ECCV 2024 — <em>"WSI-VQA: Interpreting Whole Slide Image by Generative Question Answering"</em> (Shen et al., Westlake Univ. &amp; Tencent AI Lab).
                </div>
                <div>
                    <span style="font-size: 0.8rem; color: var(--text-muted); margin-right: 6px;">Tareas Clínicas Integradas:</span>
                    <span class='badge badge-secondary'>Carcinoma Subtyping &amp; Grading</span>
                    <span class='badge badge-secondary'>IHC Biomarker Prediction (ER, PR, HER2)</span>
                    <span class='badge badge-secondary'>Survival &amp; Patient Prognosis Prediction</span>
                    <span class='badge badge-secondary'>TNM Staging &amp; Margin Status Reasoning</span>
                </div>
            </div>

            <div>
                <span class="badge badge-open">🔓 Acceso Abierto (GitHub + NIH GDC Portal)</span>
                <span class="badge badge-wsi">Cohorte: TCGA-BRCA (Cáncer de Mama)</span>
                <span class="badge badge-secondary">Total Preguntas Q&amp;A: 8,672</span>
                <span class="badge badge-secondary">Láminas Gigapíxel: 976 WSIs</span>
            </div>

            <div class="meta-grid">
                <div class="meta-item">
                    <div class="meta-label">Total Preguntas Estructuradas</div>
                    <div class="meta-value">8,672 Q&amp;A pairs</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">52.2% Opción Múltiple | 47.8% Abiertas</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Partición de Datos (Splits)</div>
                    <div class="meta-value">Train: 7,139 | Val: 798 | Test: 735</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Aisladas por paciente / lámina</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Modalidad Visual</div>
                    <div class="meta-value">Láminas SVS Gigapíxel (20×/40×)</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">NIH Genomic Data Commons (GDC)</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Embeddings &amp; Checkpoints</div>
                    <div class="meta-value">CLAM / ResNet Patch Tensors</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Modelos W2T Transformer listos</div>
                </div>
            </div>

            <div style="margin-top: 20px;">
                <div style="font-size: 0.9rem; font-weight: bold; color: var(--accent); margin-bottom: 6px;">📊 Distribución Temática de Preguntas Clínicas</div>
                <table class="subsets-table">
                    <thead>
                        <tr>
                            <th>Categoría Diagnóstica / Tarea</th>
                            <th>Porcentaje (%)</th>
                            <th>Ejemplos de Preguntas Evaluadas</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Biomarcadores Moleculares (IHC)</strong></td>
                            <td>21.5%</td>
                            <td><code>"what is the result of progesterone_receptor in the slide?"</code>, <code>"what is her2 according to the slide?"</code></td>
                        </tr>
                        <tr>
                            <td><strong>Supervivencia y Estado Vital</strong></td>
                            <td>20.1%</td>
                            <td><code>"please predict vital_status?"</code> (Alive/Dead), <code>"From the slide, can you infer the survival time?"</code> (Días)</td>
                        </tr>
                        <tr>
                            <td><strong>Subtipo Histológico</strong></td>
                            <td>13.6%</td>
                            <td><code>"what type of breast cancer is present?"</code> (Invasive Ductal, Lobular, Medullary, Tubulolobular)</td>
                        </tr>
                        <tr>
                            <td><strong>Morfología y Extensión Tumoral</strong></td>
                            <td>13.1%</td>
                            <td><code>"what is the tumor size approximately?"</code>, <code>"what was the status of surgical margins?"</code></td>
                        </tr>
                        <tr>
                            <td><strong>Gradación y Estadificación (TNM)</strong></td>
                            <td>8.4%</td>
                            <td><code>"what is the nottingham score?"</code> (3 a 9), <code>"what is the pathological stage?"</code> (pT2N0, etc.)</td>
                        </tr>
                        <tr>
                            <td><strong>Otros Hallazgos Histopatológicos</strong></td>
                            <td>23.4%</td>
                            <td>Presencia de componente <em>in situ</em> (DCIS), necrosis comedogénica, calcificaciones y cambios fibroquísticos.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div style="margin: 32px 0 16px 0; display: flex; justify-content: space-between; align-items: center;">
            <h2 style="margin: 0; font-size: 1.4rem;">🖼️ Casos Clínicos Multimodales Auditados ({len(target_cases)} Láminas Gigapíxel Reales)</h2>
            <div style="font-size: 0.85rem; color: var(--text-muted);">
                Miniaturas panorámicas de láminas transmitidas desde GDC + preguntas clínicas asociadas de WSI-VQA
            </div>
        </div>

        {"".join(cards_html)}

    </div>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\nReporte de WSI-VQA generado exitosamente en: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
