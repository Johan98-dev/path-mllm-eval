# Evaluation of Multimodal Large Language Models in Computational Pathology (`path-mllm-eval`)

> **Tesis de Maestría en Patología Computacional**  
> *Evaluación comparativa de modelos de lenguaje multimodal en tareas de análisis de contenido visual y textual de histopatología.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![HuggingFace Datasets](https://img.shields.io/badge/🤗%20Hugging%20Face-Datasets-orange.svg)](https://huggingface.co/)

---

## 📌 Descripción del Proyecto

Este repositorio contiene el marco metodológico, herramientas de auditoría de datos, scripts de evaluación y diseño experimental para comparar el desempeño de **Modelos de Lenguaje Multimodal (MLLMs / Vision-Language Models)** aplicados al análisis de imágenes y texto en patología digital e histopatología.

### Objetivos Principales
1. **Consolidar y auditar** conjuntos de datos públicos en tareas estandarizadas de análisis visual y textual (VQA, Image-Captioning, WSI-Report Generation, Cross-Modal Retrieval, Zero-Shot Classification).
2. **Seleccionar y adaptar** modelos fundacionales multimodales preentrenados en dominio general y patología computacional (e.g., Quilt-LLaVA, PathAsst, LLaVA-Med, BiomedCLIP, etc.).
3. **Establecer un benchmark unificado** con métricas formales cuantitativas para evaluar razonamiento visual, alineación texto-imagen y precisión diagnóstica.

---

## 🗂️ Estructura del Repositorio

```text
path-mllm-eval/
├── .env.example                        # Plantilla de variables de entorno
├── .gitignore                          # Exclusión de binarios (.svs, .png, .h5, .pt) y secretos
├── README.md                           # Documentación principal del repositorio
├── requirements.txt                    # Dependencias de Python
│
├── docs/                               # Control metodológico e informes
│   ├── multimodal_datasets_matrix.xlsx # Matriz de control (splits, tamaños, tareas)
│   └── datasets_histopatologia_multimodal.md # Catálogo detallado de datasets
│
├── src/                                # Código fuente modular
│   ├── __init__.py
│   └── audit_datasets.py               # Streaming, muestreo y auditoría de datasets
│
└── reports/                            # Reportes y previsualizaciones HTML generadas
```

---

## 🚀 Inicio Rápido

### 1. Clonar el repositorio
```bash
git clone https://github.com/Johan98-dev/path-mllm-eval.git
cd path-mllm-eval
```

### 2. Configurar el entorno virtual
```bash
# En Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# En Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Variables de entorno
Copia la plantilla y configura tu token de Hugging Face:
```bash
cp .env.example .env
```
Edita `.env` e ingresa tu `HF_TOKEN` (necesario para acceder a datasets con acceso restringido/gated como Quilt-1M o Quilt-Instruct).

---

## 🔍 Auditoría y Muestreo de Datasets

El módulo `src/audit_datasets.py` permite auditar y previsualizar datasets mediante **streaming** sin necesidad de descargar gigabytes a disco local:

```bash
# Listar datasets registrados
python src/audit_datasets.py --list

# Auditar un dataset en streaming (e.g., Path-VQA)
python src/audit_datasets.py --dataset path-vqa --num-samples 5

# Auditar y generar reporte HTML visual
python src/audit_datasets.py --dataset quilt-instruct --num-samples 5 --html
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
