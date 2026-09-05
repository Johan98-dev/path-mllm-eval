# Consolidado de Datasets Histopatológicos para Modelos Multimodales

Este documento sirve como catálogo, matriz metodológica y base de conocimientos consolidada para el registro, auditoría factual y seguimiento experimental de datasets histopatológicos multimodales en el proyecto de tesis de maestría:
**"Evaluación comparativa de modelos de lenguaje multimodal en tareas de análisis de contenido visual y textual de histopatología"**.

---

## 1. Tabla Comparativa General de Datasets Auditados y del Proyecto

| # | Dataset | Modalidad / Tipo de Dato | Tarea Multimodal Principal | Escala Fáctica en Repositorio (Hub) | Licencia / Acceso | Estado de Auditoría | Reporte HTML |
| :-: | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | **PathVQA** | Parche + Pregunta / Respuesta | Visual Question Answering (VQA Abierta) | **32,632 registros** (train: 19,654 \| test: 6,719 \| val: 6,259) | MIT / Abierto | ✅ Auditado (Parquet) | [`preview_flaviagiammarino_path_vqa.html`](../reports/preview_flaviagiammarino_path_vqa.html) |
| 2 | **Quilt-VQA** | Parche + VQA Curado Humano | Benchmark VQA de Evaluación Ciega | **985 preguntas** (curadas por patólogos) | CC BY-NC-ND 3.0 / Gated | ✅ Auditado (Parquet) | [`preview_wisdomik_quilt_vqa.html`](../reports/preview_wisdomik_quilt_vqa.html) |
| 3 | **Quilt-Instruct** | Diálogo Multi-turno + Referencia | Visual Instruction Tuning (SFT) | **107,000 diálogos** (anclados a Quilt-1M) | CC BY-NC-ND 3.0 / Gated | ✅ Auditado (Parquet/JSON) | [`preview_wisdomik_quilt_llava_instruct_107k.html`](../reports/preview_wisdomik_quilt_llava_instruct_107k.html) |
| 4 | **HistGen** | WSI (DINOv2) + Reporte Quirúrgico | WSI-to-Diagnostic Report Generation | **7,690 reportes** (train: 6,152 \| test: 769 \| val: 769) | Apache-2.0 / Abierto | ✅ Auditado (Embeddings) | [`preview_david4real_histgen.html`](../reports/preview_david4real_histgen.html) |
| 5 | **PathMMU** | Imagen + Opciones + Justificación | Benchmark VQA Multiple-Choice | **10,387 preguntas** (test: 8,521 \| test_tiny: 1,156 \| val: 710) | CC BY-ND 4.0 / Gated | ✅ Auditado (Range Stream) | [`preview_jamessyx_pathmmu.html`](../reports/preview_jamessyx_pathmmu.html) |
| 6 | **PathCap** | Parche + Caption Clínico | Image Captioning / VLP Pretraining | **223,169 pares** imagen-caption de PMC | CC BY-NC 2.0 / Gated | ✅ Auditado (Range Stream) | [`preview_jamessyx_pathcap.html`](../reports/preview_jamessyx_pathcap.html) |
| 7 | **PathInstruct** | Parche + Diálogo Multi-turno | Visual Instruction Tuning (SFT en 2 Fases) | **186,194 instrucciones** (con imágenes propias) | CC BY-NC 2.0 / Gated | ✅ Auditado (Range Stream) | [`preview_jamessyx_pathinstruct.html`](../reports/preview_jamessyx_pathinstruct.html) |
| 8 | **PathGen-1.6M** | Coordenadas TCGA + Dense Caption | Dense Captioning & Synthetic Pretraining | **1,620,876 parches** sobre WSIs de TCGA | CC BY-NC 2.0 / Gated | ✅ Auditado (JSON/Coords) | [`preview_jamessyx_pathgen.html`](../reports/preview_jamessyx_pathgen.html) |
| 9 | **OpenPath** | Parches TIF + CSV + Embeddings NPY | Zero-Shot Classification & Retrieval | **7,180 parches** en 4 suites (Kather, PanNuke, etc.) | Apache-2.0 / Abierto | ✅ Auditado (Parquet/CSV) | [`preview_akshayg08_openpath.html`](../reports/preview_akshayg08_openpath.html) |
| 10 | **Quilt-1M** | Imagen (parche/ROI) + texto | Vision-Language Pretraining (VLP) / Retrieval | **1,017,712 pares** (train: 1,004,153 | val: 13,559) | CC BY-NC-SA 4.0 / Gated | ✅ Auditado (Local CSV + Zip) | [`preview_wisdomik_quilt_1m.html`](../reports/preview_wisdomik_quilt_1m.html) |
| 11 | **ARCH** | Subfigura / Bolsa MIL + Caption Compuesto | Multiple-Instance Captioning & Retrieval | **7,579 imágenes / 7,614 captions** (4,270 libros + 3,309 PubMed) | CC BY-NC-SA 4.0 / Abierto | ✅ Auditado (Local ZIPs) | [`preview_arch.html`](../reports/preview_arch.html) |
| 12 | **WSI-VQA** | WSI + Q/A diagnóstico | VQA a nivel de lámina completa | **8,672 preguntas** (train: 7,139 | val: 798 | test: 735) / 976 WSIs | Abierto / GDC Portal | ✅ Auditado (GitHub + GDC Stream) | [`preview_cpystan_wsi_vqa.html`](../reports/preview_cpystan_wsi_vqa.html) |
| 13 | **PathText (WsiCaption)** | WSI (SVS) + Reporte Quirúrgico Estructurado | WSI-Level Captioning & Report Generation | **9,009 pares WSI-reporte** (30 proyectos TCGA, 55 sitios) | MIT / Abierto (GDC) | ✅ Auditado (JSON + GDC Stream) | [`preview_cpystan_wsi_caption.html`](../reports/preview_cpystan_wsi_caption.html) |
| 14 | **SlideInstruction / SlideBench** | WSI + instrucciones / VQA | WSI Visual Instruction Tuning & Benchmarking | 4.9K WSI-reportes → 4.2K captions + 176K VQA | Abierto / GDC | ⏳ Pendiente Auditoría | - |
| 15 | **PatchGastricADC22** | Parches + caption de reporte clínico | Patch-Level Diagnostic Captioning | **262,777 parches** / 1,305 reportes de 991 WSIs | Acceso Abierto / Zenodo (6021442) | ✅ Auditado (Local Zip/CSV) | [`preview_patch_gastric_adc22.html`](../reports/preview_patch_gastric_adc22.html) |
| 16 | **CAMELYON16 / 17** | WSI + anotación a nivel de píxel/slide | Metástasis en Ganglio Centinela | 400 WSIs (CAMELYON16) / 1,000 WSIs (CAMELYON17) | CC0 (Dominio Público) | ⏳ Pendiente Auditoría | - |
| 17 | **TCGA (familia)** | WSI SVS + reporte PDF + clínica | Corpus Clínico y Genómico Multimodal | >30K láminas gigapíxel SVS con reportes clínicos | Open-Access (GDC) | ⏳ Base Multicéntrica | - |
| 18 | **HEST-1k** | WSI H&E + transcriptómica espacial | Histology-to-Spatial-Transcriptomics | 1.2K perfiles de transcriptómica ligados a WSI | CC BY-NC-SA 4.0 | ⏳ Pendiente Auditoría | - |

---

## 2. Fichas Técnicas Detalladas y Registro de Auditoría Factual

---

### 1. PathVQA (`flaviagiammarino/path-vqa`)

- **Tipo de Dato / Modalidad Principal:** Parche histopatológico + Pregunta abierta / Respuesta (*Visual Question Answering*).
- **Descripción General:** Benchmark clásico de VQA abierto construido a partir de libros de texto médicos (Pathology Education Instructional Resource - PEIR, libros de texto de patología abierta).
- **Acceso / Licencia:** Repositorio público en Hugging Face (`flaviagiammarino/path-vqa`), Licencia **MIT**. Acceso abierto directo.
- **Referencia Bibliográfica:** He et al., *"PathVQA: 30,000+ Questions for Medical Visual Question Answering in Pathology"*, 2020 / arXiv:2003.10286.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Parches histopatológicos individuales en formato binario decodificable (`image`), dimensiones variables (~$300 \times 300$ a $600 \times 600$ px), predominantemente tinciones H&E e inmunohistoquímica.
  - **Textual:** Preguntas abiertas directas (`question`) formuladas en lenguaje natural y respuestas clínicas concisas (`answer`) generadas mediante extracción semi-estructurada.
- **Número de Ejemplos / Parches / WSIs (Cifras Fácticas en Hub):**
  - **Total Registros:** **`32,632 preguntas VQA`** sobre 4,998 imágenes únicas.
  - **Tamaño Total en Hub:** `749.04 MB` (16 archivos parquet).
  - **Tamaño Descomprimido:** `5.10 GB` (en memoria/disco).
- **Splits Disponibles (Train / Val / Test):**
  - `train`: **19,654 preguntas** (60.2% \| 2.95 GB).
  - `test`: **6,719 preguntas** (20.6% \| 1.04 GB) — Split ciego estándar de evaluación.
  - `validation`: **6,259 preguntas** (19.2% \| 1.11 GB).
- **Riesgo de Data Leakage (Aislamiento por Patient ID):**
  - **Riesgo Moderado a Alto:** Al provenir de PEIR y atlas médicos, múltiples preguntas corresponden a la misma imagen de origen. La partición oficial de He et al. aisló las imágenes para que una misma imagen no aparezca simultáneamente en `train` y `test`. Sin embargo, existe riesgo de solapamiento con datasets que usen la misma fuente base (ej. subconjuntos de Quilt-1M o PathCap).
- **Notas y Hallazgos del Proyecto:**
  - Es el *benchmark* de VQA abierta más citado y utilizado en la literatura para evaluar modelos como LLaVA-Med, PathAsst y BiomedCLIP.
  - **Reporte Visual HTML:** [`reports/preview_flaviagiammarino_path_vqa.html`](../reports/preview_flaviagiammarino_path_vqa.html).

---

### 2. Quilt-VQA (`wisdomik/Quilt_VQA`)

- **Tipo de Dato / Modalidad Principal:** Parche histopatológico + Pregunta VQA Curada por Expertos (*Human-in-the-loop VQA Evaluation*).
- **Descripción General:** Conjunto de evaluación y benchmark ciego de alta fidelidad curado y validado directamente por patólogos humanos para evaluar modelos de lenguaje multimodal en histopatología.
- **Acceso / Licencia:** Repositorio en Hugging Face (`wisdomik/Quilt_VQA`), Licencia **CC BY-NC-ND 3.0** (Gated / Requiere autenticación vía `HF_TOKEN`).
- **Referencia Bibliográfica:** Seyfioglu et al., *"Quilt-LLaVA: Visual Instruction Tuning by Extracting Visual Knowledge from Complex Educational Videos"*, CVPR 2024 / arXiv:2312.04746.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Parches histopatológicos extraídos de videos educativos de patología en YouTube mediante tracking del cursor del narrador. Formato Parquet nativo (`image`).
  - **Textual:** Preguntas abiertas y cerradas formuladas por patólogos certificados con respuestas de referencia verificadas.
- **Número de Ejemplos / Parches / WSIs (Cifras Fácticas en Hub):**
  - **Total Registros:** **`985 preguntas VQA curadas`**.
  - **Tamaño Total en Hub:** `505.50 MB` (6 archivos parquet).
  - **Tamaño Descomprimido:** `215.13 MB`.
- **Splits Disponibles (Train / Val / Test):**
  - `train`: **985 preguntas** (100% — diseñado metodológicamente como split de evaluación ciego / zero-shot).
- **Riesgo de Data Leakage:**
  - **Bajo:** Curaduría manual con preguntas diseñadas específicamente para no estar presentes textualmente en el corpus de preentrenamiento.
- **Notas y Hallazgos del Proyecto:**
  - Benchmark de referencia para evaluar capacidades de razonamiento patológico fino y reducción de alucinaciones en modelos LMM.
  - **Reporte Visual HTML:** [`reports/preview_wisdomik_quilt_vqa.html`](../reports/preview_wisdomik_quilt_vqa.html).

---

### 3. Quilt-Instruct (`wisdomik/QUILT-LLaVA-Instruct-107K`)

- **Tipo de Dato / Modalidad Principal:** Diálogo multi-turno de instrucción visual (*Visual Instruction Tuning / SFT*).
- **Descripción General:** Dataset masivo de ajuste fino supervisado para modelos multimodales (LLaVA-Med, Quilt-LLaVA) generado a partir del análisis multimodal de videos educativos de patología y tracking de cursor.
- **Acceso / Licencia:** Repositorio en Hugging Face (`wisdomik/QUILT-LLaVA-Instruct-107K`), Licencia **CC BY-NC-ND 3.0** (Gated / Requiere autenticación).
- **Referencia Bibliográfica:** Seyfioglu et al., CVPR 2024 / arXiv:2312.04746.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Referencias a parches `.jpg` anclados espacialmente mediante las coordenadas del cursor del patólogo en el video.
  - **Textual:** Conversaciones estructuradas en formato LLaVA (`conversations: [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]`).
- **Número de Ejemplos (Cifras Fácticas en Hub):**
  - **Total de Diálogos:** **`107,000 secuencias multi-turno`**.
  - **Tamaño Total en Hub:** `855.79 MB` (9 archivos JSON/Parquet).
  - **Subconjuntos Clave en Repo:** `quilt_instruct_107k.json`, `quilt_instruct_ablation_40k.json`, `quilt_instruct_complex_abductive.json`, `quilt_instruct_conv_desc.json`, `quilt_pretrain.json`, `cursor.parquet`, `diagnosis_and_clues.parquet`.
- **Splits Disponibles:**
  - `train`: 107K instrucciones destinadas a *Supervised Fine-Tuning* (SFT).
- **Hallazgo Metodológico de Alineación:**
  - **Estructura Desacoplada:** El repositorio almacena los diálogos y los nombres de archivo (`image: "_KJZm1orOvU_roi_...jpg"`). Los píxeles binarios pertenecen al repositorio madre `wisdomik/Quilt-1M`. Para evaluación o entrenamiento local, se asocian mediante dicha clave.
- **Notas y Hallazgos del Proyecto:**
  - **Reporte Visual HTML:** [`reports/preview_wisdomik_quilt_llava_instruct_107k.html`](../reports/preview_wisdomik_quilt_llava_instruct_107k.html).

---

### 4. HistGen (`david4real/HistGen`)

- **Tipo de Dato / Modalidad Principal:** Whole Slide Image (WSI) + Reporte Patológico Quirúrgico Diagnóstico Estructurado (*WSI-to-Report Generation*).
- **Descripción General:** Benchmark y dataset formal para la generación automatizada de reportes diagnósticos patológicos extensos a partir de láminas histopatológicas completas de múltiples tipos de cáncer en TCGA.
- **Acceso / Licencia:** Repositorio en Hugging Face (`david4real/HistGen`), Licencia **Apache-2.0**. Acceso abierto directo.
- **Referencia Bibliográfica:** Guo et al., *"HistGen: Histopathology Report Generation via Local-Global Feature Interaction"*, MICCAI 2024 / arXiv:2403.05396.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Vectores de características densos pre-extraídos con **DINOv2** (`dinov2_cpath_v1.pth`) junto con coordenadas espaciales en formato H5 (`h5_files.zip`), representando la totalidad de cada lámina gigapíxel de TCGA sin requerir transferencias masivas de archivos `.svs`.
  - **Textual:** Reportes quirúrgicos patológicos completos (*Surgical Pathology Reports* de TCGA), que incluyen diagnóstico principal, descripción microscópica, grado histológico, score mitótico y estado de márgenes.
- **Número de Ejemplos y Desglose de Particiones (Cifras Fácticas en `annotation.json`):**
  - **Total de Registros WSI &harr; Reporte:** **`7,690 casos clínicos`** de múltiples cohortes de TCGA (mama, próstata, pulmón, colon, etc.).
  - `train`: **6,152 reportes** (80.0%) — Entrenamiento multimodal.
  - `val`: **769 reportes** (10.0%) — Validación y ajuste de hiperparámetros.
  - `test`: **769 reportes** (10.0%) — Evaluación cuantitativa ciega (BLEU-1/4, ROUGE-L, METEOR, F1-RadGraph).
- **Tamaño Total en Hub:** **`303.24 GB`** (23 archivos, incluyendo 15 volúmenes ZIP de features DINOv2 de 299.3 GB, `annotation.json` de 26.91 MB y checkpoints del modelo).
- **Hallazgo Metodológico Clave:**
  - **Eficiencia WSI:** Resuelve el cuello de botella computacional de procesar gigapíxeles crudos permitiendo evaluar directamente la capacidad de generación de texto extenso (*Long-form Generation*) a partir de tensores de lámina completa.
- **Notas y Hallazgos del Proyecto:**
  - **Reporte Visual HTML:** [`reports/preview_david4real_histgen.html`](../reports/preview_david4real_histgen.html).

---

### 5. PathMMU (`jamessyx/PathMMU`)

- **Tipo de Dato / Modalidad Principal:** Imagen histopatológica + Pregunta clínica de opción múltiple + Justificación/Explicación experta (*Benchmark VQA Multiple-Choice*).
- **Descripción General:** El benchmark de razonamiento multimodal más extenso y riguroso de la literatura, validado por 7 patólogos certificados sobre casos de medicina académica, atlas y literatura científica.
- **Acceso / Licencia:** Repositorio en Hugging Face (`jamessyx/PathMMU`), Licencia **CC BY-ND 4.0** (Gated / Requiere autenticación).
- **Referencia Bibliográfica:** Sun et al., *"PathMMU: A Massive Multimodal Expert-Level Benchmark for Pathology"*, ECCV 2024 / arXiv:2401.16355.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Imágenes histopatológicas contenidas en `images.zip` (1.80 GB), extraídas mediante *streaming* selectivo por HTTP Range Requests.
  - **Textual:** Pregunta de razonamiento clínico (`question`), 4 opciones estructuradas (`options: ["A) ...", "B) ...", "C) ...", "D) ..."]`), respuesta correcta (`answer`) y justificación citoarquitectónica detallada (`explanation`).
- **Número de Ejemplos y Desglose por Partición (Cifras Fácticas en `data.json`):**
  - **Total Preguntas Validadas:** **`10,387 preguntas VQA`**.
  - `test`: **8,521 preguntas** (82.0% — Split principal de evaluación ciega).
  - `test_tiny`: **1,156 preguntas** (11.1% — Subconjunto ligero para evaluación rápida *zero-shot*).
  - `val`: **710 preguntas** (6.8% — Validación).
- **Desglose por Fuentes Clínicas del Benchmark:**
  - **PubMed:** 3,301 preguntas (Casos clínicos de literatura médica indexada).
  - **EduContent:** 2,084 preguntas (Material educativo y docente de patología).
  - **SocialPath:** 2,010 preguntas (Casos clínicos compartidos en redes académicas).
  - **PathCLS:** 1,905 preguntas (Subclasificación y diagnóstico diferencial).
  - **Atlas:** 1,087 preguntas (Atlas histopatológicos de referencia).
- **Tamaño Total en Hub:** `1.81 GB` (`data.json`: 8.88 MB \| `images.zip`: 1.80 GB).
- **Notas y Hallazgos del Proyecto:**
  - Permite evaluar tanto la precisión (*accuracy*) en opción múltiple como la coherencia diagnóstica de la justificación generada por el modelo (*rationale evaluation*).
  - **Reporte Visual HTML:** [`reports/preview_jamessyx_pathmmu.html`](../reports/preview_jamessyx_pathmmu.html).

---

### 6. PathCap (`jamessyx/PathCap`)

- **Tipo de Dato / Modalidad Principal:** Parche histopatológico + Caption descriptivo clínico (*Vision-Language Pretraining - VLP*).
- **Descripción General:** Corpus a gran escala de preentrenamiento multimodal para alinear representaciones de visión y lenguaje en patología, curado a partir de artículos abiertos de PubMed Central.
- **Acceso / Licencia:** Repositorio en Hugging Face (`jamessyx/PathCap`), Licencia **CC BY-NC 2.0** (Gated / Requiere autenticación).
- **Referencia Bibliográfica:** Sun et al., *"PathAsst: A Generative Foundation AI Assistant Towards Artificial General Intelligence of Pathology"*, AAAI 2024 / arXiv:2305.15072.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Subfiguras y paneles histopatológicos (H&E, IHC, tinciones especiales) contenidos en `images.zip` (12.68 GB), con resoluciones heterogéneas.
  - **Textual:** Captions originales de las figuras en PubMed Central, filtrados para eliminar marcas de agua y texto no patológico (`caption`). Metadatos trazables mediante `pmc_id` y `figure_fn`.
- **Número de Ejemplos (Cifras Fácticas en `data.json`):**
  - **Total de Pares Imagen-Caption:** **`223,169 registros`** *(auditados y verificados frente a la estimación teórica de 207K)*.
  - **Tamaño Total en Hub:** `12.75 GB` (`data.json`: 66.96 MB \| `images.zip`: 12.68 GB).
- **Riesgo de Data Leakage:**
  - **Alto riesgo de solapamiento inter-dataset:** Al provenir de PMC, comparte artículos con PathVQA, ARCH y Quilt-1M. La unidad de aislamiento requerida es el **PMID / PMC ID**.
- **Notas y Hallazgos del Proyecto:**
  - Conjunto base para entrenar encoders visuales tipo PathCLIP o evaluar tareas de *Image-Text Retrieval*.
  - **Reporte Visual HTML:** [`reports/preview_jamessyx_pathcap.html`](../reports/preview_jamessyx_pathcap.html).

---

### 7. PathInstruct (`jamessyx/PathInstruct`)

- **Tipo de Dato / Modalidad Principal:** Parche histopatológico + Diálogo conversacional multi-turno (*Visual Instruction Tuning / SFT*).
- **Descripción General:** Dataset de ajuste fino supervisado instruccional desarrollado para entrenar el asistente patológico PathAsst, generado mediante prompting estructurado de GPT-4 sobre figuras y leyendas de PMC.
- **Acceso / Licencia:** Repositorio en Hugging Face (`jamessyx/PathInstruct`), Licencia **CC BY-NC 2.0** (Gated / Requiere autenticación).
- **Referencia Bibliográfica:** Sun et al., AAAI 2024 / arXiv:2305.15072.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Parches histopatológicos empaquetados en su propio archivo `images.zip` (10.74 GB).
  - **Textual:** Diálogos multi-turno divididos en dos fases pedagógicas:
    - **Fase 1 (`instruction_tuning_phase1.json`):** **`186,194 secuencias de diálogo`** orientadas a la descripción morfológica meticulosa de estructuras y tinciones.
    - **Fase 2 (`instruction_tuning_phase2.json`):** Diálogos clínicos de razonamiento patológico, hipótesis diferenciales y pruebas moleculares.
- **Tamaño Total en Hub:** **`10.92 GB`** (5 archivos).
- **Hallazgo Metodológico Clave:**
  - **Autonomía:** A diferencia de Quilt-Instruct, PathInstruct es autocontenido y almacena sus propias imágenes dentro del repositorio.
- **Notas y Hallazgos del Proyecto:**
  - **Reporte Visual HTML:** [`reports/preview_jamessyx_pathinstruct.html`](../reports/preview_jamessyx_pathinstruct.html).

---

### 8. PathGen-1.6M (`jamessyx/PathGen`)

- **Tipo de Dato / Modalidad Principal:** Coordenadas espaciales sobre WSI de TCGA + Caption denso sintético generado por LMM (*Dense Captioning & Synthetic Pretraining*).
- **Descripción General:** Dataset masivo de 1.62 millones de descripciones densas sintéticas generadas por GPT-4 sobre parches extraídos de láminas histopatológicas de The Cancer Genome Atlas (TCGA).
- **Acceso / Licencia:** Repositorio en Hugging Face (`jamessyx/PathGen`), Licencia **CC BY-NC 2.0** (Gated / Requiere autenticación).
- **Referencia Bibliográfica:** Sun, Zhang et al., *"PathGen-1.6M: 1.6 Million Synthetic Pathology Image-Caption Pairs for Vision-Language Pretraining"*, ICLR 2025 / arXiv:2407.00203.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Coordenadas espaciales `position: [X, Y]` y UUIDs de parches (`file_id`) indexados sobre láminas WSI completas de TCGA (`wsi_id`).
  - **Textual:** Captions sintéticos densos de alta complejidad morfológica (`caption`), describiendo arquitectura glandular, atipia nuclear, infiltración estromal e hipótesis tumorales.
- **Número de Ejemplos (Cifras Fácticas en `PathGen-1.6M.json`):**
  - **Total de Pares Coordenada-Caption:** **`1,620,876 registros` (1.62 Millones)**.
  - **Tamaño Total en Hub:** `933.28 MB` (archivo JSON estructurado).
- **Hallazgo Metodológico Clave:**
  - **Datos Sintéticos vs. Datos Reales:** Permite evaluar experimentalmente en la tesis si los modelos multimodales adquieren mejores representaciones entrenando con descripciones sintéticas densas (PathGen) frente a captions humanos escuetos (PathCap / Quilt-1M).
- **Notas y Hallazgos del Proyecto:**
  - **Reporte Visual HTML:** [`reports/preview_jamessyx_pathgen.html`](../reports/preview_jamessyx_pathgen.html).

---

### 9. OpenPath (`akshayg08/OpenPath`)

- **Tipo de Dato / Modalidad Principal:** Parches histopatológicos `.tif` + Archivos CSV + Matrices de Embeddings `.npy` (*Multimodal Zero-Shot Classification & Retrieval Benchmark*).
- **Descripción General:** Repositorio oficial con las suites de evaluación estandarizadas del modelo fundacional **PLIP** (*Pathology Language-Image Pretraining*), que incluye múltiples tareas de clasificación de subtipos y tejidos.
- **Acceso / Licencia:** Repositorio público en Hugging Face (`akshayg08/OpenPath`), Licencia **Apache-2.0**. Acceso abierto directo.
- **Referencia Bibliográfica:** Huang et al., *"A Visual-Language Foundation Model for Pathology"*, **Nature Medicine (2023)** / doi:10.1038/s41591-023-02504-3.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** 7,180 parches de tejido en formato `.tif` clasificados por subtipos histológicos (tumor, estroma, adiposo, linfocitos, etc.).
  - **Textual:** Etiquetas clínicas (`label_text`) y prompts estandarizados para evaluación *Zero-Shot* (`caption: "An H&E image patch of benign tissue."`).
  - **Representaciones Vectoriales:** 32 matrices `.npy` con los embeddings normalizados de imagen y texto extraídos con PLIP y CLIP para reproducibilidad inmediata.
- **Subconjuntos y Benchmarks Incluidos:**
  1. **Kather Benchmark (NCT-CRC-HE / CRC-VAL-HE):** 7,180 parches en 9 clases tisulares (`Kather_train.csv`, `Kather_test.csv`).
  2. **DigestPath Benchmark:** Detección de adenocarcinoma colorrectal (`DigestPath_train.csv`, `DigestPath_test.csv`).
  3. **PanNuke Benchmark:** Clasificación de 19 tipos de núcleos neoplásicos/inmunes (`PanNuke_train.csv`, `PanNuke_test.csv`).
  4. **WSSS4LUAD Benchmark:** Detección binaria de adenocarcinoma pulmonar (`WSSS4LUAD_binary_train.csv`, `WSSS4LUAD_binary_test.csv`).
- **Tamaño Total en Hub:** `2.15 GB` (7,222 archivos).
- **Hallazgo Metodológico Clave:**
  - **Baseline Universal:** Proporciona los benchmarks y matrices canónicas para comparar cuantitativamente las capacidades *Zero-Shot* de cualquier modelo multimodal evaluado en la tesis frente a PLIP.
- **Notas y Hallazgos del Proyecto:**
  - **Reporte Visual HTML:** [`reports/preview_akshayg08_openpath.html`](../reports/preview_akshayg08_openpath.html).

---

### 10. Quilt-1M (`wisdomik/quilt1m`)

- **Tipo de Dato / Modalidad Principal:** Parche / ROI Histopatológico + Caption Descriptivo / Narración Clínica (*Vision-Language Pretraining & Multi-Modal Alignment*).
- **Descripción General:** El dataset multimodal abierto más grande y diverso en patología computacional, compuesto por más de un millón de pares imagen-texto obtenidos mediante procesamiento automatizado de videos educativos de YouTube (con tracking del cursor del patólogo y transcripción de voz con corrección LLM), combinado con PubMed Central, Twitter/OpenPath y LAION-5B.
- **Acceso / Licencia:** Repositorio en Hugging Face (`wisdomik/Quilt-1M`), Licencia **CC BY-NC-SA 4.0** (Uso para investigación / académico).
- **Referencia Bibliográfica:** Ikezogwo et al., *"Quilt-1M: One Million Image-Text Pairs for Histopathology"*, **NeurIPS 2023 (Oral)** / arXiv:2306.11207.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Parches y ROIs histopatológicos en formato `.jpg` / `.png` (redimensionados estándar a $512\times 512$ px), cubriendo múltiples órganos, subtipos tumorales y tinciones histológicas.
  - **Textual:** Captions descriptivos (`caption`), transcripciones automáticas de voz (`noisy_text`), descripciones refinadas mediante GPT-3.5 (`corrected_text`), narraciones específicas del área señalada (`roi_text`) e identificadores de conceptos médicos de la ontología UMLS (`med_umls_ids`).
- **Número de Ejemplos / Parches / Subconjuntos (Cifras Fácticas del Dataset):**
  - **Total Registros:** **`1,017,712 pares imagen-texto`** (1,017,708 con caption válido).
  - **Desglose Fáctico por Subconjunto (`subset`):**
    - `quilt` (Videos de YouTube): **802,148 pares** (78.82%) con tracking espacial de cursor y corrección GPT.
    - `openpath` (Twitter / Casos de Patólogos): **133,511 pares** (13.12%).
    - `pubmed` (PubMed Central Open Access): **59,371 pares** (5.83%).
    - `laion` (Subconjunto filtrado de LAION-5B): **22,682 pares** (2.23%).
- **Splits Disponibles:**
  - `train`: **1,004,153 pares** (98.67%).
  - `val`: **13,559 pares** (1.33%).
- **Magnificación y Escala Microquímica:**
  - **802,148 registros (78.82%)** del subconjunto YouTube cuentan con magnificación discreta clasificada:
    - Nivel `0.0` (Baja magnificación / Arquitectura panorámica): **480,726 pares** (59.9%).
    - Nivel `1.0` (Magnificación media): **135,048 pares** (16.8%).
    - Nivel `2.0` (Alta magnificación / Detalle celular y nuclear): **186,374 pares** (23.2%).
- **Riesgo de Data Leakage (Aislamiento y Filtrado):**
  - **Riesgo Alto:** Al ser el corpus de preentrenamiento base más grande, presenta solapamiento de artículos y casos con datasets como PathCap, OpenPath y subconjuntos de PubMed. Para evaluar en benchmarks como Quilt-VQA o PathVQA se deben excluir rigurosamente los canales de YouTube y PMIDs correspondientes.
- **Notas y Hallazgos del Proyecto:**
  - Base sobre la cual se entrenaron modelos fundamentales de visión-lenguaje como **QuiltNet** (CLIP adaptado a patología) y el dataset de instrucciones **Quilt-LLaVA / Quilt-Instruct-107K**.
  - **Reporte Visual HTML:** [`reports/preview_wisdomik_quilt_1m.html`](../reports/preview_wisdomik_quilt_1m.html).

---

### 11. ARCH (Multiple Instance Captioning)

- **Tipo de Dato / Modalidad Principal:** Subfigura Histopatológica Individual / Bolsas de Instancias Múltiples (MIL) + Caption Diagnóstico Morfológico Compuesto (*Multiple Instance Histopathology Captioning & Dense Retrieval*).
- **Descripción General:** Conjunto pionero diseñado para el preentrenamiento por supervisión visual densa (*dense supervision*) y aprendizaje de representaciones transferibles en patología computacional. Introduce la tarea de captioning de instancia múltiple sobre figuras compuestas (con múltiples paneles o subfiguras A, B, C...) extraídas de atlas/libros de texto y artículos científicos de libre acceso en PubMed Central.
- **Acceso / Licencia:** Repositorio oficial en el Tissue Image Analytics (TIA) Centre de la University of Warwick ([TIA Warwick ARCH](https://warwick.ac.uk/fac/cross_fac/tia/data/arch)); Licencia **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.
- **Referencia Bibliográfica:** Jevgenij Gamper & Nasir Rajpoot, *"Multiple Instance Captioning: Learning Representations from Histopathology Textbooks and Articles"*, **CVPR 2021 (Oral)**, pp. 16549–16559 / [arXiv:2103.05121](https://arxiv.org/abs/2103.05121).

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Imágenes en alta resolución (formato PNG en libros, JPG/PNG en PubMed; dimensiones promedio ~819 × 656 px en libros y ~613 × 473 px en PubMed; resolución máxima >1,540 px). Cubren tinciones diagnósticas estándar (H&E) e inmunohistoquímica (IHC).
  - **Textual:** Captions densos con descripciones citoarquitectónicas detalladas en lenguaje natural. En libros de texto, los captions describen conjuntos de subfiguras con referencias a letras (ej. *"A, Spindle cell variant of embryonal rhabdomyosarcoma... (B), some of which can show prominent..."*).
- **Estructura Fáctica y Desglose por Subconjuntos (Archivos ZIP Auditados en Disco):**
  - **Total Consolidado:** **`7,579 imágenes binarias`** y **`7,614 registros textuales`** en dos archivos ZIP en `Data/raw/arch/` (**5.75 GB** totales en disco):
    1. `books_set.zip` (4.91 GB / 5,275,751,113 bytes):
       - **4,270 imágenes PNG** de atlas médicos y libros de histopatología.
       - **4,305 descripciones en `captions.json`** (4,270 pares válidos con imagen, 35 captions sin imagen binaria física, 0 imágenes huérfanas).
       - **3,321 bolsas (*figures*) únicas:**
         - 2,720 bolsas de instancia única (81.9%) con letra `Single`.
         - 601 bolsas de instancias múltiples (18.1%) compuestas por entre 2 y 9 subfiguras asociadas a letras (A: 568, B: 586, C: 235, D: 106, E: 42, F: 26, G: 9, H: 5, I: 4, J: 2, K: 1).
    2. `pubmed_set.zip` (456.6 MB / 478,791,695 bytes):
       - **3,309 imágenes** (3,272 JPG + 37 PNG) de artículos de libre acceso en PubMed Central.
       - **3,309 descripciones en `captions.json`** (100.0% de alineación determinista 1 a 1).
- **Métricas Cuantitativas de Texto:**
  - **Volumen Total:** 214,326 palabras en el corpus.
  - **Vocabulario Médico Único:** 9,564 tokens léxicos consolidados.
  - **Longitud Textual por Fuente:**
    - *books_set:* Media de **36.0 palabras/caption** (mediana: 27 palabras; rango: 0 a 331 palabras; promedio 3.1 oraciones por caption).
    - *pubmed_set:* Media de **17.9 palabras/caption** (mediana: 15 palabras; rango: 1 a 167 palabras; promedio 1.6 oraciones por caption).
  - **Prevalencia de Descriptores Patológicos Clave:**
    - *cells / cell:* 5,926 menciones
    - *stain / staining:* 2,057 menciones
    - *tumor / tumour:* 2,013 menciones
    - *carcinoma / adenocarcinoma:* 1,627 menciones
    - *nuclei / nuclear:* 1,569 menciones
    - *glands / gland:* 1,241 menciones
    - *stroma / stromal:* 890 menciones
    - *biopsy:* 570 menciones
    - *malignant / benign:* 722 menciones
    - *necrosis:* 280 menciones
    - *IHC:* 263 menciones
- **Nota Metodológica sobre la Discrepancia de Muestras (Oficial de Warwick TIA):**
  - En el artículo original de CVPR 2021 se citaron preliminarmente 11,833 bolsas y ~15,200 imágenes en su rastreo inicial. No obstante, el portal oficial del Warwick TIA Centre consigna formalmente: *"There is a disparity between the number of samples within the paper and the dataset available for download due to an error."* Nuestra auditoría certifica la cantidad fáctica disponible en la distribución oficial descargada: **7,579 imágenes y 7,614 captions**.
- **Riesgo de Data Leakage (Aislamiento con Benchmarks de la Tesis):**
  - **Riesgo Alto:** Al provenir de atlas médicos clásicos y artículos de PubMed, comparte fuentes y figuras con `PathVQA` (libros de PEIR) y `PathCap` (PMC Open Access). Para evaluaciones en la Fase 3, se debe verificar el aislamiento de identificadores de imagen/texto si ARCH se utiliza en etapas de entrenamiento o fine-tuning.
- **Relevancia Estratégica para la Tesis de Maestría:**
  - Constituye el conjunto de datos de referencia para evaluar la capacidad de los modelos de lenguaje multimodal en desambiguar paneles múltiples dentro de una misma figura diagnóstica (*multi-panel figure reasoning*), modelando la formulación de aprendizaje por instancia múltiple (MIL) en la interacción visión-lenguaje.
- **Reporte Visual HTML:** [`reports/preview_arch.html`](../reports/preview_arch.html) (con 13 casos interactivos de bolsas multi-instancia A/B/C, figuras de atlas y marcaciones IHC de PubMed).

---

### 12. WSI-VQA (`cpystan/WSI-VQA`)

- **Tipo de Dato / Modalidad Principal:** Whole Slide Image (SVS Gigapíxel / Tensores de Parches) + Preguntas Diagnósticas Clínicas (*Whole Slide Image Visual Question Answering*).
- **Descripción General:** Framework y dataset pionero de VQA generativo sobre láminas histopatológicas completas de cáncer de mama (cohorte TCGA-BRCA). Permite evaluar el razonamiento clínico multimodal sobre la totalidad de la lámina en tareas de subtipificación de carcinomas, gradación de Nottingham, predicción de biomarcadores moleculares (ER, PR, HER2) y estimación de supervivencia global.
- **Acceso / Licencia:** Código y anotaciones Q&A abiertas en GitHub (`cpystan/WSI-VQA`); láminas SVS gigapíxel de libre acceso a través del portal de NIH Genomic Data Commons (GDC).
- **Referencia Bibliográfica:** Shen et al., *"WSI-VQA: Interpreting Whole Slide Image by Generative Question Answering"*, **ECCV 2024** / arXiv:2407.05603.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** Láminas gigapíxel SVS a $20\times$ y $40\times$ de resolución (~$50,000\times 40,000$ a $100,000\times 50,000$ píxeles) y matrices de embeddings de parches $256\times 256$ procesadas con CLAM/ResNet.
  - **Textual:** Preguntas clínicas en lenguaje natural con opciones múltiples (52.2%) y preguntas abiertas de predicción numérica y categórica (47.8%).
- **Número de Ejemplos / Preguntas / Láminas (Cifras Fácticas en Repositorio):**
  - **Total Registros:** **`8,672 preguntas Q&A`**.
  - **Total Láminas Gigapíxel:** **`976 WSIs únicas`** (cohorte TCGA-BRCA).
- **Splits Disponibles:**
  - `train` (`WsiVQA_train.json`): **7,139 preguntas** (82.3%) sobre 804 WSIs.
  - `val` (`WsiVQA_val.json`): **798 preguntas** (9.2%) sobre 87 WSIs.
  - `test` (`WsiVQA_test.json`): **735 preguntas** (8.5%) sobre 86 WSIs.
- **Distribución Temática de Tareas Clínicas:**
  - *Biomarcadores Moleculares / IHC (ER, PR, HER2):* 21.5% (1,533 preguntas).
  - *Supervivencia y Estado Vital (Alive/Dead, Días de Sobrevida):* 20.1% (1,433 preguntas).
  - *Subtipo Histológico y Diagnóstico de Carcinoma:* 13.6% (972 preguntas).
  - *Morfología, Tamaño y Márgenes Quirúrgicos:* 13.1% (936 preguntas).
  - *Gradación de Nottingham y Estadificación TNM:* 8.4% (598 preguntas).
  - *Otros Hallazgos Histopatológicos (DCIS, Necrosis, Calcificaciones):* 23.4% (1,667 preguntas).
- **Notas y Hallazgos del Proyecto:**
  - Modelo fundacional asociado: **W2T (Wsi2Text Transformer)**.
  - Visualización e inspección directa: Cada caso en el reporte incluye la miniatura panorámica real del tejido extraída mediante HTTP Range stream desde GDC y el enlace al visor oficial de láminas gigapíxel con zoom óptico $40\times$.
  - **Reporte Visual HTML:** [`reports/preview_cpystan_wsi_vqa.html`](../reports/preview_cpystan_wsi_vqa.html).

---

### 13. PathText (WsiCaption)

- **Tipo de Dato / Modalidad Principal:** Whole Slide Image (SVS gigapíxel, magnificación $20\times / 40\times$) + Reporte Quirúrgico y Diagnóstico Estructurado (*Whole Slide Image Captioning & Automated Pathology Report Generation*).
- **Descripción General:** Conjunto de datos a escala de lámina completa curado a partir de los reportes PDF de patología quirúrgica de The Cancer Genome Atlas (TCGA), procesados mediante un pipeline híbrido de OCR (PyMuPDF + Tesseract) y depuración/reestructuración con Modelos de Lenguaje Masivo (LLM/GPT), emparejados directamente con las láminas diagnósticas gigapíxel de NIH GDC.
- **Acceso / Licencia:** Código bajo Licencia MIT ([cpystan/Wsi-Caption](https://github.com/cpystan/Wsi-Caption)); anotaciones textuales en Google Drive (`PathText.json`); láminas diagnósticas SVS de acceso abierto vía NIH Genomic Data Commons (GDC).
- **Referencia Bibliográfica:** Pingyi Chen, Honglin Li, Chenglu Zhu, Sunyi Zheng, Zhongyi Shui, Lin Yang, *"WsiCaption: Multiple Instance Generation of Pathology Reports for Gigapixel Whole Slide Images"*, **MICCAI 2024 Oral / Best Paper Candidate** / arXiv:2311.16480.

#### 📋 Registro de Auditoría y Métricas Detalladas
- **Alineación Multimodal Verificada:** Cada registro vincula de forma determinista el identificador de paciente (`id: TCGA-XX-YYYY`) con su lámina diagnóstica histopatológica SVS (`TCGA-XX-YYYY-01Z-00-DX1...svs`) y su reporte textual clínico correspondiente.
- **Número Total de Pares WSI-Reporte Auditados:** **`9,009 registros`** (0 reportes vacíos, 9,009 pacientes únicos).
- **Diversidad de Cohortes y Proyectos Oncológicos:** Distribuido en **30 proyectos de cáncer de TCGA** y **55 sitios anatómicos primarios**:
  - `TCGA-BRCA` (Mama): 1,061 casos (11.8%)
  - `TCGA-KIRC` (Riñón - Células Claras): 513 casos (5.7%)
  - `TCGA-THCA` (Tiroides): 506 casos (5.6%)
  - `TCGA-UCEC` (Cuerpo Uterino): 504 casos (5.6%)
  - `TCGA-LUSC` (Pulmón - Células Escamosas): 478 casos (5.3%)
  - `TCGA-LUAD` (Pulmón - Adenocarcinoma): 476 casos (5.3%)
  - `TCGA-LGG` (Glioma de Bajo Grado): 466 casos (5.2%)
  - `TCGA-HNSC` (Cabeza y Cuello): 450 casos (5.0%)
  - `TCGA-COAD` (Colon): 450 casos (5.0%)
  - `TCGA-SKCM` (Melanoma Cutáneo): 431 casos (4.8%)
  - `TCGA-STAD` (Estómago): 416 casos (4.6%)
  - `TCGA-PRAD` (Próstata): 403 casos (4.5%)
  - Otros 18 proyectos (BLCA, LIHC, KIRP, CESC, SARC, PCPG, READ, ESCA, TGCT, THYM, OV, KICH, UVM, MESO, UCS, ACC, DLBC, CHOL): 2,255 casos (25.0%).
- **Métricas Cuantitativas de Texto:**
  - **Volumen Total:** ~1,078,000 palabras en el corpus.
  - **Longitud por Reporte:** Media de **119.7 palabras** (mediana: 107 palabras; rango: 9 a 539 palabras; desviación estándar: ~51.2 palabras).
  - **Estructura Sintáctica:** Media de **9.2 oraciones por reporte** (mediana: 8 oraciones; rango: 1 a 66 oraciones).
  - **Vocabulario Diagnóstico Único:** **12,046 tokens** con alta prevalencia de descriptores patológicos críticos:
    - *tumor*: 22,394 ocurrencias
    - *lymph / nodes*: 25,812 ocurrencias
    - *carcinoma / adenocarcinoma*: 14,873 ocurrencias
    - *invasion*: 7,173 ocurrencias
    - *margins*: 5,174 ocurrencias
    - *grade*: 4,110 ocurrencias
    - *resection*: 2,744 ocurrencias
    - *metastasis*: 2,004 ocurrencias
    - *biomarkers (ER, PR, HER2, S100, Melan-A)*: >3,500 menciones
- **Partición Oficial de Benchmark (Cohorte TCGA-BRCA):**
  - Total de láminas en split oficial (`splits_0.csv`): **1,041 láminas** (845 train / 98 val / 98 test).
  - Pacientes únicos: 804 train / 97 val / 98 test (100% solapamiento con PathText).
- **Pipeline de Extracción y Representación de Características:**
  - **Extracción de Parches:** Segmentación de tejido con umbralizado de Otsu en lámina completa downsampleada mediante OpenSlide; extracción de parches contiguos de $256 \times 256$ px sin solapamiento.
  - **Embeddings Visuales:** Red ResNet-50 truncada (CLAM) para codificar cada parche en un vector de características de 1024 dimensiones, guardado como tensores `.pt`.
- **Arquitectura de Modelo Propuesta (MI-Gen):**
  - Marco generativo de instancia múltiple (*Multiple Instance Generation*) con codificador visual multi-escala y decodificador con atención espacial consciente de la posición (*position-aware module*).
  - Rendimiento reportado en la literatura: superó modelos MIL clásicos (Attention MIL, CLAM-SB, TransMIL, MS2MIL) y modelos de subtipado, alcanzando **F1-score de 0.838** en subtipado molecular de mama a partir únicamente de la extracción semántica del reporte generado.
- **Relevancia Estratégica para la Tesis de Maestría:**
  - Constituye el conjunto de datos fundamental para la **Tarea 3 (Whole Slide Image Captioning / Automated Report Generation)**, permitiendo comparar arquitecturas fundacionales que operan sobre bolsas de características gigapíxel frente a modelos de visión-lenguaje densos basados en parches o ROIs.
- **Reporte Visual HTML:** [`reports/preview_cpystan_wsi_caption.html`](../reports/preview_cpystan_wsi_caption.html) (incluye 8 láminas gigapíxel reales de GDC con visor interactivo $40\times$).

---

### 14. SlideInstruction / SlideBench

- **Tipo de Dato / Modalidad Principal:** WSI + instrucciones multimodales / Benchmark de lámina completa.
- **Descripción General:** 4.9K WSI-reportes transformados en 4.2K captions y 176K preguntas VQA de TCGA; incluye benchmark de evaluación exhaustivo.
- **Acceso / Licencia:** Abierto con WSIs en GDC.
- **Referencia Bibliográfica:** Chen et al., *"SlideInstruction: Multi-granular Visual Instruction Tuning for Whole Slide Images"*, CVPR 2025 / arXiv:2410.11761.

#### 📋 Registro de Auditoría y Métricas Detalladas
- **Modalidades de Entrada:** Láminas completas de TCGA y secuencias multi-granulares de VQA (subtipos, biomarcadores, pronóstico).
- **Número de Ejemplos:** 4,900 láminas / 176,000 preguntas VQA.
- **Estado en el Proyecto:** ⏳ Pendiente de auditoría.

---

### 15. PatchGastricADC22 (Zenodo 6021442)

- **Tipo de Dato / Modalidad Principal:** Parche Histopatológico $300\times 300$ px (H&E) + Caption de Diagnóstico y Subtipo Patológico (*Histopathology Patch-Level Diagnostic Captioning*).
- **Descripción General:** Dataset multimodal curado a partir de 991 láminas histopatológicas completas (WSIs) de biopsias endoscópicas de adenocarcinoma gástrico humano. Las leyendas textuales provienen directamente de reportes diagnósticos hospitalarios reales elaborados por patólogos certificados según las directrices de la Asociación Japonesa de Cáncer Gástrico (JGCA) y la OMS.
- **Acceso / Licencia:** Acceso abierto y público en Zenodo ([DOI: 10.5281/zenodo.6021442](https://doi.org/10.5281/zenodo.6021442)).
- **Referencia Bibliográfica:** Masayuki Tsuneki & Fahdi Kanavati, *"Inference of captions from histopathological patches"*, **MIDL 2022** / PMLR 172:1235–1250, 2022 / arXiv:2202.03432.

#### 📋 Registro de Auditoría Factual y Métricas Verificadas
- **Modalidades de Entrada:**
  - **Visual:** **262,777 parches histológicos** ($300 \times 300$ píxeles, RGB, formato JPEG, 7.20 GB en `patches_captions.zip`) extraídos de regiones tumorales de 991 WSIs (promedio ~265 parches por lámina).
  - **Textual:** **1,305 reportes y descripciones diagnósticas** en `captions.csv` (media de 23.6 palabras por reporte; rango: 4 a 45 palabras).
- **Distribución de Subtipos Histopatológicos (JGCA / WHO):**
  1. *Well differentiated tubular adenocarcinoma (tub1):* 285 reportes (21.8%)
  2. *Moderately differentiated tubular adenocarcinoma (tub2):* 275 reportes (21.1%)
  3. *Poorly differentiated adenocarcinoma, non-solid (por2):* 182 reportes (13.9%)
  4. *Signet ring cell carcinoma (sig):* 142 reportes (10.9%)
  5. *Papillary adenocarcinoma (pap):* 135 reportes (10.3%)
  6. *Poorly differentiated adenocarcinoma, solid (por1):* 132 reportes (10.1%)
  7. *Moderately to poorly differentiated adenocarcinoma:* 86 reportes (6.6%)
  8. *Well to moderately differentiated tubular adenocarcinoma:* 61 reportes (4.7%)
  9. *Mucinous adenocarcinoma (muc):* 4 reportes (0.3%)
  10. *Variantes combinadas:* 3 reportes (0.2%)
- **Archivos Locales Auditados:**
  - `captions.csv` (339.8 KB) en `C:\Users\johan\OneDrive\Documentos\Projects`
  - `patches_captions.zip` (7.20 GB, 262,777 imágenes) en `C:\Users\johan\OneDrive\Documentos\Projects`
- **Reporte Visual HTML:** [`reports/preview_patch_gastric_adc22.html`](../reports/preview_patch_gastric_adc22.html) con 12 muestras visuales reales decodificadas y descripciones diagnósticas.

---

### 16. CAMELYON16 / 17

- **Tipo de Dato / Modalidad Principal:** WSI + anotación a nivel de píxel y slide (Metástasis en Ganglio Linfático Centinela de Cáncer de Mama).
- **Descripción General:** 400 WSIs (CAMELYON16) y 1,000 WSIs (CAMELYON17) de ganglio centinela con máscaras exhaustivas de metástasis trazadas a mano por patólogos expertos.
- **Acceso / Licencia:** **CC0 (Dominio Público)** / Acceso abierto directo vía Zenodo / Radboud University.
- **Referencia Bibliográfica:** Bejnordi et al., *"Diagnostic Assessment of Deep Learning Algorithms for Detection of Lymph Node Metastases in Women With Breast Cancer"*, JAMA, 2017.

#### 📋 Registro de Auditoría y Métricas Detalladas
- **Modalidades de Entrada:** Láminas completas de ganglio centinela en formato TIF multirresolución con máscaras binarias XML/PNG de metástasis macrometastásicas y micrometastásicas.
- **Número de Ejemplos:** 400 láminas (CAMELYON16) / 1,000 láminas (CAMELYON17).
- **Estado en el Proyecto:** ⏳ Benchmark cuantitativo de visión por computadora para detección de metástasis.

---

### 17. TCGA (Familia The Cancer Genome Atlas)

- **Tipo de Dato / Modalidad Principal:** Whole Slide Images (SVS) + Reportes Quirúrgicos PDF + Perfiles Moleculares y Clínicos.
- **Descripción General:** Repositorio multicéntrico y multi-canceroso de referencia mundial que contiene más de 30,000 láminas gigapíxel SVS junto con datos moleculares y reportes patológicos oficiales.
- **Acceso / Licencia:** Capa Open-Access disponible mediante NCI Genomic Data Commons (GDC Data Portal).
- **Referencia Bibliográfica:** National Cancer Institute (NCI) & National Human Genome Research Institute (NHGRI).

#### 📋 Registro de Auditoría y Métricas Detalladas
- **Modalidades de Entrada:** Láminas gigapíxel SVS a $20\times$ ($0.50\,\mu\text{m/px}$) y $40\times$ ($0.25\,\mu\text{m/px}$) cubriendo más de 33 tipos tumorales.
- **Número de Ejemplos:** >30,000 láminas diagnósticas (`DX`) y de corte por congelación (`TS`).
- **Estado en el Proyecto:** Base madre de la cual derivan datasets multimodales clave como HistGen, PathGen-1.6M, WSI-VQA y SlideInstruction.

---

### 18. HEST-1k

- **Tipo de Dato / Modalidad Principal:** WSI H&E + Perfiles de Transcriptómica Espacial (*Spatial Transcriptomics*).
- **Descripción General:** 1,200 perfiles de transcriptómica espacial ligados a láminas histopatológicas completas H&E en 26 órganos y 25 tipos de cáncer.
- **Acceso / Licencia:** Licencia **CC BY-NC-SA 4.0** / Acceso abierto vía Hugging Face y Zenodo.
- **Referencia Bibliográfica:** Jaume et al., *"HEST-1k: A Benchmark for Spatial Transcriptomics from Histology Images"*, NeurIPS 2024 / arXiv:2406.16192.

#### 📋 Registro de Auditoría y Métricas Detalladas
- **Modalidades de Entrada:** Láminas H&E de alta resolución vinculadas punto a punto con matrices de expresión génica espacial (Visium, ST).
- **Número de Ejemplos:** 1,200 perfiles espaciales en 26 órganos humanos.
- **Estado en el Proyecto:** ⏳ Frontera multimodal emergente (Histología + Genómica Espacial).

---

## 3. Matriz Metodológica de Tareas Multimodales y Datasets para la Tesis

| Tarea Estandarizada del Proyecto | Datasets Auditados Disponibles | Formato de Entrada Visual | Formato de Entrada / Salida Textual | Métrica de Evaluación Principal |
| :--- | :--- | :--- | :--- | :--- |
| **1. Visual Question Answering (VQA Abierta)** | `path-vqa`, `quilt-vqa` | Parche $224\times 224$ / $512\times 512$ px | Pregunta clínica abierta $\to$ Respuesta corta de patología | Accuracy exacta, F1-Score, BLEU-1 |
| **2. Benchmark VQA Multiple-Choice** | `pathmmu` | Parche de subfigura clínica | Pregunta + Opciones A/B/C/D $\to$ Clave de respuesta + Justificación | Accuracy por opción, Rationale BLEU/ROUGE |
| **3. Visual Instruction Tuning (SFT)** | `quilt-instruct`, `pathinstruct` | Parche anclado / Subfigura | Diálogo interactivo multi-turno (Humano $\leftrightarrow$ Modelo) | GPT-4 Judge Score, Human Pathologist Rating |
| **4. Image Captioning / VLP** | `pathcap`, `openpath`, `quilt-1m` | Parche H&E / IHC | Parche $\to$ Caption descriptivo del artículo | BLEU-4, ROUGE-L, METEOR, CIDEr |
| **5. Cross-Modal Image-Text Retrieval** | `openpath`, `pathcap` | Parche TIF / JPEG | Consulta de texto $\leftrightarrow$ Búsqueda de parches en espacio latente | Recall@1, Recall@5, Mean Reciprocal Rank (MRR) |
| **6. Zero-Shot Tissue Classification** | `openpath` (Kather, PanNuke, LUAD) | Parche TIF | Prompts de clases tisulares $\to$ Similitud coseno con parche | Zero-Shot Accuracy, Macro-F1 |
| **7. WSI-to-Diagnostic Report Generation** | `histgen`, `pathtext` | Embeddings WSI (DINOv2) | Matriz de lámina completa $\to$ Reporte quirúrgico completo | BLEU-1/4, ROUGE-L, F1-RadGraph clínico |
| **8. Dense Captioning Sintético** | `pathgen` | Coordenadas $(X, Y)$ en TCGA | Coordenada en lámina $\to$ Descripción morfológica densa GPT-4 | Perplejidad, Semantic Density Score |

---

## 4. Próximos Pasos de la Fase 1 (Consolidación y Auditoría)

1. **Generación de la Matriz Excel Formal (`docs/multimodal_datasets_matrix.xlsx`):**
   * Exportar el desglose de particiones, resoluciones, tamaños comprimidos/descomprimidos y licencias a la hoja de cálculo de control metodológico.
2. **Definición de Datasets Específicos para la Fase 2 y 3 (Selección de Modelos y Diseño Experimental):**
   * Seleccionar el *benchmark core* de evaluación (ej. `pathmmu` para razonamiento clínico de opción múltiple, `quilt-vqa` y `path-vqa` para VQA abierta, `openpath` para *zero-shot classification/retrieval*, e `histgen` para generación de reportes).
