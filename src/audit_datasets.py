#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria y Muestreo por Streaming de Datasets Multimodales en Hugging Face.
Tesis de Maestria en Patologia Computacional.
"""

import os
import sys
import io
import json
import base64
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
import datasets
from huggingface_hub import HfApi

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# 1. Catalogo Declarativo de Datasets y Tareas Multimodales
# ---------------------------------------------------------------------------
DATASET_REGISTRY = {
    "path-vqa": {
        "repo_id": "flaviagiammarino/path-vqa",
        "primary_task": "Visual Question Answering (VQA - Preguntas Abiertas)",
        "secondary_tasks": ["Image-to-Text Reasoning", "Medical VLP Benchmark", "Visual Feature Alignment"],
        "task_formalized": "Si (Benchmark VQA estandarizado por He et al., 2020)",
        "default_split": "train",
        "description": "32.8K preguntas abiertas sobre ~5K imagenes histopatologicas (PEIR / libros de texto)."
    },
    "quilt-instruct": {
        "repo_id": "wisdomik/QUILT-LLaVA-Instruct-107K",
        "primary_task": "Visual Instruction Tuning / Multi-turn Dialogue",
        "secondary_tasks": ["Spatial Grounding VQA", "Complex Pathological Reasoning", "LMM Fine-tuning"],
        "task_formalized": "Si (Curado para LLaVA-Med / Quilt-LLaVA por Seyfioglu et al., CVPR 2024)",
        "default_split": "train",
        "description": "107K pares de instrucciones/preguntas histopatologicas ancladas a parches con tracking narrativo."
    },
    "quilt-vqa": {
        "repo_id": "wisdomik/Quilt_VQA",
        "primary_task": "Benchmark VQA (Evaluacion de Modelos Multimodales)",
        "secondary_tasks": ["Visual Question Answering (Abierta / Cerrada)", "Zero-Shot Evaluation"],
        "task_formalized": "Si (Conjunto de evaluacion curado por expertos humanos, Seyfioglu et al., 2024)",
        "default_split": "train",
        "description": "Benchmark de evaluacion de preguntas y respuestas multimodales sobre imagenes de patologia."
    },
    "pathcap": {
        "repo_id": "jamessyx/PathCap",
        "primary_task": "Image Captioning / Vision-Language Pretraining (VLP)",
        "secondary_tasks": ["Cross-Modal Image-Text Retrieval", "Contrastive Learning (PathCLIP)"],
        "task_formalized": "Si (Dataset de preentrenamiento multimodal de PathAsst, Sun et al., AAAI 2024)",
        "default_split": "train",
        "description": "207K pares imagen-caption curados de PubMed, libros y citologia liquida (PathAsst)."
    },
    "pathinstruct": {
        "repo_id": "jamessyx/PathInstruct",
        "primary_task": "Visual Instruction Tuning / Conversational AI",
        "secondary_tasks": ["Specialized Tool-Use Prompting", "Diagnostic Decision Support"],
        "task_formalized": "Si (Instrucciones generadas por GPT-4V para PathAsst, Sun et al., 2024)",
        "default_split": "train",
        "description": "180K instrucciones y dialogos generados con GPT-4V sobre literatura medica."
    },
    "pathgen": {
        "repo_id": "jamessyx/PathGen",
        "primary_task": "Synthetic Dense Image Captioning / VLP",
        "secondary_tasks": ["WSI-Patch Feature Alignment", "Multi-Agent Vision Pretraining"],
        "task_formalized": "Si (Preentrenamiento con LMM multi-agente sobre parches TCGA, Sun et al., ICLR 2025)",
        "default_split": "train",
        "description": "1.6M pares imagen-caption generados por sistema multi-agente sobre parches de TCGA."
    },
    "pathmmu": {
        "repo_id": "jamessyx/PathMMU",
        "primary_task": "Benchmark VQA Multiple-Choice (Opcion Multiple)",
        "secondary_tasks": ["Clinical Rationale Extraction / Explanation", "Expert-Level Diagnostic Benchmark"],
        "task_formalized": "Si (Benchmark validado por 7 patologos expertos, Sun et al., ECCV 2024)",
        "default_split": "train",
        "description": "33.4K preguntas de opcion multiple con explicacion clinica experta y 24K imagenes."
    },
    "openpath": {
        "repo_id": "akshayg08/OpenPath",
        "primary_task": "Cross-Modal Retrieval (Image-to-Text & Text-to-Image)",
        "secondary_tasks": ["Zero-Shot Patch Classification", "Vision-Language Contrastive Pretraining (PLIP)"],
        "task_formalized": "Si (Curado para entrenamiento de PLIP, Huang et al., Nature Medicine 2023)",
        "default_split": "train",
        "description": "208K imagenes de patologia con descripciones clinicas curadas de Twitter medico y LAION."
    },
    "histgen": {
        "repo_id": "david4real/HistGen",
        "primary_task": "WSI-to-Diagnostic Report Generation",
        "secondary_tasks": ["Long-form Pathology Report Generation", "Multi-Cancer Report Synthesis"],
        "task_formalized": "Si (Benchmark y dataset estandar de generacion de reportes, Guo et al., MICCAI 2024)",
        "default_split": "train",
        "description": "Pares WSI/parches con reportes patologicos estructurados de TCGA."
    }
}

# ---------------------------------------------------------------------------
# 2. Carga de Variables de Entorno (.env)
# ---------------------------------------------------------------------------
def load_env_variables() -> Dict[str, str]:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    loaded = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("\"'")
                    os.environ[k] = v
                    loaded[k] = v
    return loaded

def get_hf_token() -> Optional[str]:
    load_env_variables()
    token = os.environ.get("HF_TOKEN")
    if token:
        token = token.strip().strip("\"'")
    return token

# ---------------------------------------------------------------------------
# 3. Inspeccion Factica de Metadatos y Conteo Exacto de Splits
# ---------------------------------------------------------------------------
def format_bytes(size_bytes: int) -> str:
    if size_bytes > 1024**3:
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes > 1024**2:
        return f"{size_bytes / (1024**2):.2f} MB"
    elif size_bytes > 0:
        return f"{size_bytes / 1024:.2f} KB"
    return "0 B"

def inspect_hf_metadata(repo_id: str, token: Optional[str] = None) -> Dict[str, Any]:
    api = HfApi(token=token)
    meta = {
        "repo_id": repo_id,
        "exists": False,
        "gated": False,
        "private": False,
        "license": "No especificada",
        "tags": [],
        "downloads": 0,
        "likes": 0,
        "hub_total_size_bytes": 0,
        "hub_total_size_str": "Desconocido",
        "download_size_str": "Desconocido",
        "dataset_size_str": "Desconocido",
        "files_count": 0,
        "splits_info": {},
        "total_records": 0,
        "configs": [],
        "description": ""
    }
    
    try:
        info = api.dataset_info(repo_id, token=token, files_metadata=True)
        meta["exists"] = True
        meta["gated"] = getattr(info, "gated", False)
        meta["private"] = getattr(info, "private", False)
        meta["tags"] = getattr(info, "tags", []) or []
        meta["downloads"] = getattr(info, "downloads", 0)
        meta["likes"] = getattr(info, "likes", 0)
        meta["description"] = getattr(info, "description", "") or ""
        
        for tag in meta["tags"]:
            if tag.startswith("license:"):
                meta["license"] = tag.split(":", 1)[1]
                break

        if hasattr(info, "siblings") and info.siblings:
            total_size = sum([getattr(s, "size", 0) or 0 for s in info.siblings])
            meta["files_count"] = len(info.siblings)
            meta["hub_total_size_bytes"] = total_size
            meta["hub_total_size_str"] = format_bytes(total_size)

        try:
            builder = datasets.load_dataset_builder(repo_id, token=token)
            if builder.info.splits:
                total_recs = 0
                for s_name, s_info in builder.info.splits.items():
                    num_ex = getattr(s_info, "num_examples", 0) or 0
                    num_by = getattr(s_info, "num_bytes", 0) or 0
                    total_recs += num_ex
                    meta["splits_info"][s_name] = {
                        "num_examples": num_ex,
                        "num_bytes": num_by,
                        "size_str": format_bytes(num_by)
                    }
                meta["total_records"] = total_recs

            if getattr(builder.info, "download_size", None):
                meta["download_size_str"] = format_bytes(builder.info.download_size)
            if getattr(builder.info, "dataset_size", None):
                meta["dataset_size_str"] = format_bytes(builder.info.dataset_size)
        except Exception:
            pass

        if not meta["splits_info"] and hasattr(info, "card_data") and info.card_data:
            card_dict = dict(info.card_data) if hasattr(info.card_data, "items") else {}
            if "dataset_info" in card_dict:
                ds_info = card_dict["dataset_info"]
                if isinstance(ds_info, dict) and "splits" in ds_info:
                    splits_raw = ds_info["splits"]
                    if isinstance(splits_raw, list):
                        total_recs = 0
                        for s in splits_raw:
                            s_name = s.get("name", "unknown")
                            num_ex = s.get("num_examples", 0)
                            num_by = s.get("num_bytes", 0)
                            total_recs += num_ex
                            meta["splits_info"][s_name] = {
                                "num_examples": num_ex,
                                "num_bytes": num_by,
                                "size_str": format_bytes(num_by)
                            }
                        meta["total_records"] = total_recs

    except Exception as e:
        meta["error"] = str(e)

    return meta

# ---------------------------------------------------------------------------
# 4. Procesamiento de Imagenes y Conversion a Base64
# ---------------------------------------------------------------------------
def image_to_base64(img_obj: Any, max_dim: int = 512) -> tuple[Optional[str], Dict[str, Any]]:
    meta = {"width": None, "height": None, "format": "Unknown", "mode": "Unknown"}
    try:
        pil_img = None
        if isinstance(img_obj, Image.Image):
            pil_img = img_obj
        elif isinstance(img_obj, dict):
            if "bytes" in img_obj and img_obj["bytes"]:
                pil_img = Image.open(io.BytesIO(img_obj["bytes"]))
            elif "path" in img_obj and img_obj["path"]:
                if os.path.exists(img_obj["path"]):
                    pil_img = Image.open(img_obj["path"])
        elif isinstance(img_obj, bytes):
            pil_img = Image.open(io.BytesIO(img_obj))

        if pil_img is None:
            return None, meta

        meta["width"], meta["height"] = pil_img.size
        meta["format"] = pil_img.format or "PNG"
        meta["mode"] = pil_img.mode

        w, h = pil_img.size
        if max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            new_size = (int(w * scale), int(h * scale))
            pil_img_resized = pil_img.resize(new_size, Image.Resampling.LANCZOS)
        else:
            pil_img_resized = pil_img

        buffered = io.BytesIO()
        if pil_img_resized.mode in ("RGBA", "LA") or (pil_img_resized.mode == "P" and "transparency" in pil_img_resized.info):
            pil_img_resized.save(buffered, format="PNG")
            mime_type = "image/png"
        else:
            pil_img_rgb = pil_img_resized.convert("RGB")
            pil_img_rgb.save(buffered, format="JPEG", quality=85)
            mime_type = "image/jpeg"

        b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:{mime_type};base64,{b64_str}", meta
    except Exception as e:
        meta["error"] = str(e)
        return None, meta

# ---------------------------------------------------------------------------
# 5. Extraccion de Muestras por Streaming
# ---------------------------------------------------------------------------
def sample_dataset_stream(
    repo_id: str,
    split: str = "train",
    config: Optional[str] = None,
    n_samples: int = 7,
    token: Optional[str] = None
) -> Dict[str, Any]:
    result = {
        "repo_id": repo_id,
        "split": split,
        "config": config,
        "features": {},
        "samples": [],
        "status": "pending",
        "error": None
    }
    try:
        kwargs = {"split": split, "streaming": True}
        if token:
            kwargs["token"] = token
        if config:
            kwargs["name"] = config

        ds = datasets.load_dataset(repo_id, **kwargs)

        if hasattr(ds, "features") and ds.features:
            result["features"] = {k: str(v) for k, v in ds.features.items()}

        samples_list = []
        for idx, item in enumerate(ds):
            if idx >= n_samples:
                break
            
            sample_data = {
                "sample_index": idx + 1,
                "images": [],
                "text_fields": {},
                "raw_metadata": {}
            }

            for k, v in item.items():
                if isinstance(v, (Image.Image, bytes)) or (isinstance(v, dict) and ("bytes" in v or "path" in v) and not any(isinstance(val, (dict, list)) for val in v.values())):
                    b64, img_meta = image_to_base64(v)
                    if b64:
                        sample_data["images"].append({
                            "field_name": k,
                            "data_uri": b64,
                            "metadata": img_meta
                        })
                    else:
                        sample_data["raw_metadata"][k] = str(v)[:150]
                elif isinstance(v, list):
                    if v and isinstance(v[0], dict) and ("from" in v[0] or "role" in v[0]):
                        sample_data["text_fields"][k] = {
                            "type": "dialogue",
                            "content": v
                        }
                    else:
                        sample_data["text_fields"][k] = {
                            "type": "list",
                            "content": v
                        }
                elif isinstance(v, str):
                    sample_data["text_fields"][k] = {
                        "type": "string",
                        "content": v,
                        "char_count": len(v),
                        "word_count": len(v.split())
                    }
                else:
                    sample_data["raw_metadata"][k] = v

            samples_list.append(sample_data)

        result["samples"] = samples_list
        result["status"] = "success"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    return result

# ---------------------------------------------------------------------------
# 6. Generacion del Reporte HTML Visual-Textual Detallado
# ---------------------------------------------------------------------------
def generate_html_report(
    meta_hf: Dict[str, Any],
    stream_data: Dict[str, Any],
    output_path: Path,
    registry_entry: Optional[Dict[str, Any]] = None
) -> str:
    repo_id = meta_hf["repo_id"]
    primary_task = registry_entry.get("primary_task", "Tarea Multimodal de Histopatologia") if registry_entry else "Tarea Multimodal"
    secondary_tasks = registry_entry.get("secondary_tasks", []) if registry_entry else []
    task_formalized = registry_entry.get("task_formalized", "No especificado formalmente") if registry_entry else "N/A"
    
    # Render splits table
    splits_html = ""
    if meta_hf.get("splits_info"):
        rows_html = ""
        total_rec = meta_hf.get("total_records", 0)
        for s_name, s_data in meta_hf["splits_info"].items():
            cnt = s_data.get("num_examples", 0)
            pct = f"({(cnt / total_rec * 100):.1f}%)" if total_rec > 0 else ""
            is_active = "style='color: var(--accent); font-weight: bold;'" if s_name == stream_data.get("split") else ""
            rows_html += f"""
            <tr {is_active}>
                <td style="padding: 8px 12px; border-bottom: 1px solid var(--border-color);"><code>{s_name}</code></td>
                <td style="padding: 8px 12px; border-bottom: 1px solid var(--border-color); text-align: right;">{cnt:,} {pct}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid var(--border-color); text-align: right;">{s_data.get('size_str', 'N/A')}</td>
            </tr>
            """
        splits_html = f"""
        <div class="meta-item" style="grid-column: 1 / -1; margin-top: 8px;">
            <div class="meta-label">Desglose Oficial de Particiones (Splits) - Total Registros: {total_rec:,}</div>
            <table style="width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 0.9rem;">
                <thead>
                    <tr style="background: rgba(255,255,255,0.05); text-align: left;">
                        <th style="padding: 8px 12px; border-bottom: 1px solid var(--border-color);">Split</th>
                        <th style="padding: 8px 12px; border-bottom: 1px solid var(--border-color); text-align: right;">Registros / Filas</th>
                        <th style="padding: 8px 12px; border-bottom: 1px solid var(--border-color); text-align: right;">Tamano Estimado</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """

    # Secondary tasks badges
    sec_tasks_html = ""
    for st in secondary_tasks:
        sec_tasks_html += f"<span class='badge badge-secondary'>{st}</span> "

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoria de Dataset: {repo_id}</title>
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
            padding: 12px 16px;
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
            grid-template-columns: 360px 1fr;
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
            gap: 14px;
        }}
        .sample-num {{
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: bold;
            margin-bottom: 4px;
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
            font-size: 0.95rem;
            color: var(--text-main);
            white-space: pre-wrap;
            word-break: break-word;
        }}
        .dialogue-bubble {{
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }}
        .dialogue-human {{
            background: #1e3a8a;
            color: #dbeafe;
            border-left: 4px solid var(--accent);
        }}
        .dialogue-gpt {{
            background: #14532d;
            color: #dcfce7;
            border-left: 4px solid var(--accent-green);
        }}
        .dialogue-speaker {{
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .raw-meta-box {{
            margin-top: 8px;
            font-size: 0.8rem;
            color: var(--text-muted);
        }}
        details summary {{
            cursor: pointer;
            color: var(--accent);
            outline: none;
        }}
        pre {{
            background: #020617;
            padding: 10px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 0.8rem;
        }}
        .error-banner {{
            background: #7f1d1d;
            color: #fecaca;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 24px;
            border: 1px solid #b91c1c;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Auditoria de Dataset: <code>{repo_id}</code></h1>
            
            <div class="task-banner">
                <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); font-weight: bold; margin-bottom: 4px;">
                    🎯 Tareas Multimodales Formalizadas &amp; Derivadas
                </div>
                <div style="font-size: 1.05rem; font-weight: bold; color: var(--text-main); margin-bottom: 6px;">
                    Tarea Principal: {primary_task}
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px;">
                    <strong>Formalizacion:</strong> {task_formalized}
                </div>
                <div>
                    <span style="font-size: 0.8rem; color: var(--text-muted); margin-right: 6px;">Tareas Secundarias / Posibles:</span>
                    {sec_tasks_html}
                </div>
            </div>

            <div>
                <span class="badge { 'badge-gated' if meta_hf.get('gated') else 'badge-open' }">
                    { '🔒 Gated (Requiere Aprobacion)' if meta_hf.get('gated') else '🔓 Acceso Abierto' }
                </span>
                <span class="badge badge-task">Licencia: {meta_hf.get('license', 'N/A')}</span>
                <span class="badge badge-task">Descargas: {meta_hf.get('downloads', 0):,}</span>
                <span class="badge badge-task">Likes: {meta_hf.get('likes', 0):,}</span>
            </div>

            <div class="meta-grid">
                <div class="meta-item">
                    <div class="meta-label">Tamano Total en Hub (Archivos)</div>
                    <div class="meta-value">{meta_hf.get('hub_total_size_str', 'N/A')}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">{meta_hf.get('files_count', 0)} archivos totales</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Tamano Descomprimido (Dataset)</div>
                    <div class="meta-value">{meta_hf.get('dataset_size_str', 'N/A')}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Descarga: {meta_hf.get('download_size_str', 'N/A')}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Split Muestreado</div>
                    <div class="meta-value"><code>{stream_data.get('split', 'N/A')}</code></div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">{len(stream_data.get('samples', []))} muestras extraidas</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Total Registros (Todos los Splits)</div>
                    <div class="meta-value">{meta_hf.get('total_records', 0):,}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">Sumatoria de particiones</div>
                </div>

                {splits_html}
            </div>

            {f'<div class="meta-item" style="margin-top: 16px;"><div class="meta-label">Esquema de Caracteristicas (Features)</div><pre>{json.dumps(stream_data.get("features", {}), indent=2)}</pre></div>' if stream_data.get('features') else ''}
        </div>
"""

    if stream_data.get("error"):
        html_content += f"""
        <div class="error-banner">
            <strong>⚠️ Error durante el muestreo por streaming:</strong><br>
            <code>{stream_data['error']}</code>
        </div>
        """

    html_content += f"""
        <div class="samples-header">
            <h2>🖼️ Muestras Extraidas por Streaming ({len(stream_data.get('samples', []))})</h2>
            <span style="color: var(--text-muted); font-size: 0.9rem;">Inspeccion de Alineacion Multimodal (Imagen &harr; Texto)</span>
        </div>
    """

    for sample in stream_data.get("samples", []):
        s_idx = sample["sample_index"]
        
        visual_html = ""
        if sample["images"]:
            for img in sample["images"]:
                img_meta = img["metadata"]
                dim_str = f"{img_meta.get('width', '?')} &times; {img_meta.get('height', '?')} px"
                visual_html += f"""
                <img src="{img['data_uri']}" alt="Muestra {s_idx} - {img['field_name']}">
                <div class="image-meta">
                    <strong>Campo:</strong> <code>{img['field_name']}</code><br>
                    <strong>Resolucion:</strong> {dim_str}<br>
                    <strong>Modo:</strong> {img_meta.get('mode', 'N/A')} ({img_meta.get('format', 'N/A')})
                </div>
                """
        else:
            visual_html = "<div style='color: var(--text-muted); padding: 40px;'>Sin imagen directa (o dato vectorial)</div>"

        text_html = f"<div class='sample-num'>MUESTRA #{s_idx}</div>"
        for field_name, field_val in sample.get("text_fields", {}).items():
            f_type = field_val.get("type")
            if f_type == "dialogue":
                dialogue_boxes = ""
                for turn in field_val.get("content", []):
                    speaker = turn.get("from", turn.get("role", "speaker"))
                    val = turn.get("value", turn.get("content", ""))
                    cls_name = "dialogue-gpt" if str(speaker).lower() in ("gpt", "assistant", "bot") else "dialogue-human"
                    dialogue_boxes += f"""
                    <div class="dialogue-bubble {cls_name}">
                        <div class="dialogue-speaker">{speaker}</div>
                        <div>{val}</div>
                    </div>
                    """
                text_html += f"""
                <div class="field-box">
                    <div class="field-title"><span>🗨️ Dialogo / Instruccion: <code>{field_name}</code></span></div>
                    {dialogue_boxes}
                </div>
                """
            elif f_type == "list":
                list_str = "<br>".join([f"&bull; {str(item)}" for item in field_val.get("content", [])])
                text_html += f"""
                <div class="field-box">
                    <div class="field-title"><span>📋 Lista / Opciones: <code>{field_name}</code></span></div>
                    <div class="field-content">{list_str}</div>
                </div>
                """
            else:
                content = field_val.get("content", "")
                char_c = field_val.get("char_count", 0)
                word_c = field_val.get("word_count", 0)
                text_html += f"""
                <div class="field-box">
                    <div class="field-title">
                        <span>📝 Campo: <code>{field_name}</code></span>
                        <span>{word_c} palabras | {char_c} caracteres</span>
                    </div>
                    <div class="field-content">{content}</div>
                </div>
                """

        if sample.get("raw_metadata"):
            text_html += f"""
            <div class="raw-meta-box">
                <details>
                    <summary>Ver otros metadatos / identificadores ({len(sample['raw_metadata'])})</summary>
                    <pre>{json.dumps(sample['raw_metadata'], indent=2, default=str)}</pre>
                </details>
            </div>
            """

        html_content += f"""
        <div class="sample-card">
            <div class="visual-pane">
                {visual_html}
            </div>
            <div class="text-pane">
                {text_html}
            </div>
        </div>
        """

    html_content += """
    </div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return str(output_path)

# ---------------------------------------------------------------------------
# 7. CLI / Entrada Principal
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Auditoria y Muestreo por Streaming de Datasets Multimodales en Hugging Face."
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Muestra el catalogo de datasets registrados para la tesis."
    )
    parser.add_argument(
        "--dataset", "-d",
        type=str,
        help="Alias del dataset (ej: path-vqa, quilt-instruct) o repo_id completo en HF (ej: flaviagiammarino/path-vqa)."
    )
    parser.add_argument(
        "--split", "-s",
        type=str,
        default=None,
        help="Split a auditar (train, test, validation, etc.)."
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="Configuracion especifica del dataset (si tiene multiples subconjuntos)."
    )
    parser.add_argument(
        "--samples", "-n",
        type=int,
        default=7,
        help="Numero de muestras a extraer por streaming (por defecto: 7)."
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="reports",
        help="Directorio donde se guardaran los reportes HTML (por defecto: reports/)."
    )

    args = parser.parse_args()

    if args.list:
        print("\n" + "="*80)
        print("CATALOGO DE DATASETS MULTIMODALES EN HUGGING FACE (TESIS)")
        print("="*80)
        for alias, item in DATASET_REGISTRY.items():
            print(f"[{alias}] -> {item['repo_id']}")
            print(f"   • Tarea Principal:   {item['primary_task']}")
            print(f"   • Tareas Secund.:    {', '.join(item['secondary_tasks'])}")
            print(f"   • Formalizacion:     {item['task_formalized']}")
            print(f"   • Split por defecto: {item['default_split']}")
            print("-" * 80)
        print("\nPara auditar un dataset, ejecuta:")
        print("   python src/audit_datasets.py --dataset <alias_o_repo_id> [--samples 7]\n")
        return

    if not args.dataset:
        print("Error: Debes especificar un dataset con --dataset <nombre> o usar --list para ver el catalogo.")
        parser.print_help()
        sys.exit(1)

    dataset_key = args.dataset.strip()
    registry_entry = None
    if dataset_key in DATASET_REGISTRY:
        registry_entry = DATASET_REGISTRY[dataset_key]
        repo_id = registry_entry["repo_id"]
        primary_task = registry_entry["primary_task"]
        split = args.split or registry_entry["default_split"]
    else:
        repo_id = dataset_key
        primary_task = "Dataset Externo / No catalogado"
        split = args.split or "train"

    token = get_hf_token()
    token_status = "Detectado (HF_TOKEN activo)" if token else "No detectado (solo acceso publico)"

    print("\n" + "="*80)
    print(f"🔬 AUDITANDO DATASET: {repo_id}")
    print("="*80)
    print(f"🔑 Estado de Token:    {token_status}")
    print(f"🎯 Tarea Principal:    {primary_task}")
    if registry_entry:
        print(f"📋 Tareas Posibles:    {', '.join(registry_entry['secondary_tasks'])}")
        print(f"📜 Formalizacion:      {registry_entry['task_formalized']}")
    print(f"📦 Split Objetivo:     {split}")
    print(f"🔍 Muestras a extraer: {args.samples}")
    print("-" * 80)

    print("📡 Consultando metadatos oficiales y desglose de particiones en Hub...")
    meta_hf = inspect_hf_metadata(repo_id, token=token)

    if not meta_hf["exists"]:
        print(f"❌ Error: No se pudo acceder al repositorio '{repo_id}'.")
        if "error" in meta_hf:
            print(f"   Detalle: {meta_hf['error']}")
        print("   Verifica si el nombre es correcto o si requieres aceptar terminos en Hugging Face.")
        sys.exit(1)

    print(f"   ✅ Repositorio encontrado:")
    print(f"   • Licencia:                  {meta_hf.get('license', 'N/A')}")
    print(f"   • Gated/Privado:             Gated={meta_hf.get('gated')} | Privado={meta_hf.get('private')}")
    print(f"   • Tamano Total Hub (Repo):   {meta_hf.get('hub_total_size_str', 'N/A')} ({meta_hf.get('files_count', 0)} archivos)")
    print(f"   • Tamano Dataset (Descomp.): {meta_hf.get('dataset_size_str', 'N/A')} | Descarga: {meta_hf.get('download_size_str', 'N/A')}")
    print(f"   • Total Registros en Hub:    {meta_hf.get('total_records', 0):,}")
    print(f"   • Descargas:                 {meta_hf.get('downloads', 0):,}")

    if meta_hf.get("splits_info"):
        print("\n📊 Desglose Oficial de Particiones (Splits):")
        for s_name, s_data in meta_hf["splits_info"].items():
            print(f"   • [{s_name}]: {s_data.get('num_examples', 0):,} filas ({s_data.get('size_str', 'N/A')})")

    print("\n🌊 Iniciando conexion por streaming de muestras...")
    stream_data = sample_dataset_stream(
        repo_id=repo_id,
        split=split,
        config=args.config,
        n_samples=args.samples,
        token=token
    )

    if stream_data["status"] == "error":
        print(f"⚠️ Error al hacer streaming: {stream_data['error']}")
        print("   Revisa si el split seleccionado es correcto o si el dataset tiene subconfiguraciones (--config).")
    else:
        num_samples = len(stream_data["samples"])
        print(f"   ✅ {num_samples} muestras extraidas y procesadas exitosamente.")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = repo_id.replace("/", "_").replace("-", "_").lower()
    report_filename = f"preview_{slug}.html"
    report_path = out_dir / report_filename

    print(f"\n📝 Generando reporte visual HTML en: {report_path}...")
    generate_html_report(
        meta_hf=meta_hf,
        stream_data=stream_data,
        output_path=report_path,
        registry_entry=registry_entry
    )

    print(f"   🎉 Reporte generado con exito.")
    print(f"   👉 Archivo generado: {report_path.resolve()}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
