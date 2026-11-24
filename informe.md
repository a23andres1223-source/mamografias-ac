# Clasificación de lesiones mamográficas benignas y malignas con transferencia de aprendizaje (CBIS-DDSM)

**Aprendizaje Computacional – Ingeniería de Sistemas, Universidad de Córdoba**
**Autor:** [tu nombre completo] · **Fecha:** [fecha de entrega] · **Repositorio:** https://github.com/a23andres1223-source/mamografias-ac

> **Prototipo académico; no apto para diagnóstico ni decisiones clínicas.**

> **Cómo usar este borrador.** Las tablas, cifras y figuras salen de los archivos del repositorio y están verificadas. Los bloques marcados **[BORRADOR]** son notas con las ideas y los datos que debe cubrir cada párrafo: **redáctalos tú con tus palabras** y borra la marca. Extensión máxima: 10 páginas. Al terminar, genera el PDF y el Word (ver el final del archivo).

---

## Resumen

**[BORRADOR]** Un párrafo de 120–180 palabras que diga: qué clasificas (recortes de masas, benigna/maligna según patología), con qué datos (CBIS-DDSM, 1.691 lesiones de 892 pacientes), qué comparaste (CNN pequeña, ResNet18 con y sin aumento), el resultado en **prueba** del modelo final (AUC 0,821; sensibilidad 0,896; especificidad 0,500 con umbral 0,045 elegido en validación) y la limitación principal (muchos falsos positivos; no es herramienta clínica).

## 1. Problema y alcance

**[BORRADOR]** Explica:
- Qué es la unidad de análisis: una **lesión (masa)** recortada; la etiqueta es la patología, no BI-RADS ni un diagnóstico de la paciente.
- Usuario previsto: estudiantes y docentes; prototipo educativo.
- Por qué el **falso negativo** es el error más costoso y por eso priorizas la sensibilidad (ver `hipotesis.md`).

## 2. Datos

| Aspecto | Valor |
|---|---|
| Fuente | CBIS-DDSM (TCIA), versión 1 (actualizada 2017/09/14), licencia CC BY 3.0 |
| Cita | Lee et al. (2016), DOI 10.7937/K9/TCIA.2016.7O02S9CY |
| Subconjunto | Solo masas: recortes y máscaras ROI de los CSV oficiales de train y test (1.799 series, 3.382 DICOM, ≈27 GB) |
| Filas en CSV / con imagen | 1.696 / 1.691 (5 excluidas por no encontrarse el DICOM) |
| Pacientes | 892 (1,9 lesiones por paciente en promedio; máximo 14) |
| Clases | 911 benignas (53,9 %) y 780 malignas (46,1 %) |

**Mapeo de etiquetas** (`mapeo_etiquetas.md`): `BENIGN` y `BENIGN_WITHOUT_CALLBACK` → 0 (benigna); `MALIGNANT` → 1 (maligna). 141 de las 911 benignas son `BENIGN_WITHOUT_CALLBACK`.

**Particiones por paciente** (`GroupShuffleSplit`, semilla 42; `check_split.py`: 0 pacientes y 0 imágenes compartidos):

| Partición | Lesiones | Pacientes | % malignas |
|---|---|---|---|
| Entrenamiento | 1.174 | 624 | 46,5 % |
| Validación | 244 | 134 | 48,8 % |
| Prueba | 273 | 134 | 42,1 % |

**[BORRADOR]** Explica por qué partiste por paciente y no por imagen (fuga de datos) y que mezclaste los CSV oficiales de train/test para hacer tus propias particiones (no se conserva la partición oficial).

## 3. Análisis exploratorio

Figuras: `eda/clases_por_particion.png`, `eda/ejemplos.png`, `eda/tamanos_intensidad.png`.

| Variable como único predictor | AUC |
|---|---|
| Área del recorte | 0,570 |
| Ancho / alto | 0,563 / 0,570 |
| Intensidad media | 0,530 |

**[BORRADOR]** Interpreta: las clases están casi equilibradas; ninguna variable simple separa las clases (AUC cercano a 0,5), así que no hay un "atajo" evidente; hay vistas CC y MLO y ambos lados en las dos clases. Menciona la decisión que tomaste por el EDA: rellenar a cuadrado antes de redimensionar a 224×224 para no deformar la lesión (ver `eda_conclusiones.md`).

## 4. Metodología

- **Preprocesamiento** (`imaging.py`, `dataset.py`): DICOM → PNG de 8 bits con recorte de percentiles 1–99; relleno a cuadrado; 224×224; 3 canales; normalización ImageNet. Aumentos solo en entrenamiento.
- **Modelos** (`models.py`): (a) CNN pequeña desde cero (línea base, lr 1e-3); (b) ResNet18 preentrenada en ImageNet, ajuste de todas las capas (lr 1e-4, Adam, 15 épocas, lote 32).
- **Selección**: mejor época por ROC-AUC de **validación**; pesos de clase en la pérdida.
- **Umbral**: elegido en validación como el mayor que logra sensibilidad ≥ 0,90 (`evaluate.py --target-sensitivity 0.90`). La prueba se usó **una sola vez** al final.

**[BORRADOR]** Justifica con tus palabras por qué transferencia de aprendizaje con tan pocos datos, y por qué el umbral se elige en validación y no en prueba.

## 5. Experimentos (validación, 244 lesiones: 119 malignas y 125 benignas)

| Modelo | Mejor val_AUC | Umbral (sens ≥ 0,90) | Sensibilidad | Especificidad | FP | FN |
|---|---|---|---|---|---|---|
| CNN pequeña (línea base) | 0,634 | 0,344 | 0,908 | 0,128 | 109 | 11 |
| ResNet18 con aumento | 0,836 | 0,045 | 0,908 | 0,512 | 61 | 11 |
| ResNet18 sin aumento | 0,837 | 0,075 | 0,908 | 0,592 | 51 | 11 |

Con umbral 0,5 la línea base solo detecta 23 de 119 malignas (sensibilidad 0,193; especificidad 0,864).

**Sobreajuste** (`runs/*/history.csv`):

| Modelo | train_loss final | val_loss mínima → final |
|---|---|---|
| CNN pequeña | ≈0,66 | ≈0,69 → 0,71 (casi no aprende) |
| ResNet18 con aumento | 0,113 | 0,52 (ép. 2) → 0,69; máx. 0,85 |
| ResNet18 sin aumento | 0,011 | máx. 1,14 |

**Efecto del umbral en ResNet18 con aumento** (`runs/resnet18_base/umbrales_val.md`):

| Umbral | TN | FP | FN | TP | Sensibilidad | Especificidad | Exactitud |
|---|---|---|---|---|---|---|---|
| 0,50 | 99 | 26 | 37 | 82 | 0,689 | 0,792 | 0,742 |
| 0,30 | 90 | 35 | 28 | 91 | 0,765 | 0,720 | 0,742 |
| 0,045 | 64 | 61 | 11 | 108 | 0,908 | 0,512 | 0,705 |

**[BORRADOR]** Discute: (1) la transferencia mejora claramente a la línea base; (2) el experimento controlado de aumento (una sola variable cambiada, misma semilla) no cambió el AUC pero sí el sobreajuste y los FP; (3) por qué elegiste el modelo **con aumento** como final aunque el sin aumento tenía 10 FP menos (tu razón: estabilidad); (4) que cada maligna recuperada al bajar el umbral cuesta 1–1,5 falsos positivos y que la exactitud sola no sirve para decidir.

## 6. Evaluación final en prueba (una sola vez)

Modelo `resnet18_base`, umbral 0,045 fijado en validación. Prueba: 273 lesiones (115 malignas, 158 benignas).

| Métrica | Validación | **Prueba** |
|---|---|---|
| ROC-AUC | 0,836 | **0,821** |
| Sensibilidad | 0,908 | **0,896** |
| Especificidad | 0,512 | **0,500** |
| Precisión | 0,639 | **0,566** |
| F1 | 0,750 | **0,694** |
| Exactitud | 0,705 | **0,667** |
| TN / FP / FN / TP | 64 / 61 / 11 / 108 | **79 / 79 / 12 / 103** |

Figuras: `runs/resnet18_base/confusion_test.png`, `roc_test.png`, `fn_grid_test.png`, `fp_grid_test.png`.

**[BORRADOR]** Interpreta: el resultado de prueba es muy cercano al de validación (AUC −0,015; sensibilidad −0,012), lo que sugiere que el umbral elegido en validación se mantiene; la precisión baja más porque la prueba tiene menos malignas (42,1 % frente a 48,8 %). La mitad de las benignas se marcan como malignas: en un uso real eso serían muchos estudios adicionales.

## 7. Análisis de errores

**Falsos negativos en prueba (12)** — `runs/resnet18_base/errors_test.csv`:
- Todos con puntuación < 0,039 (umbral 0,045); 5 de ellos por debajo de 0,002. Bajar un poco el umbral no los recuperaría.
- Vista: 6 CC y 6 MLO. Lado: 8 derecho y 4 izquierdo. Cada uno de una paciente distinta.
- En validación hubo 11 FN, también con puntuaciones 0,00–0,03 (8 MLO, 3 CC), y uno de ellos (P_01534) en dos vistas.

**[BORRADOR]** Mira `fn_grid_test.png` y `fp_grid_test.png` y describe con prudencia qué tienen en común (p. ej., tejido denso, bordes poco definidos, recortes pequeños). Plantéalo como hipótesis, no como conclusión: son pocos casos.

## 8. Verificación de hipótesis

| Hipótesis | Criterio | Resultado | ¿Se cumple? |
|---|---|---|---|
| H1: ResNet18 supera a la CNN pequeña | val_AUC con diferencia > 0,05 | 0,836 frente a 0,634 | Sí |
| H2: con 0,5 la sensibilidad < especificidad, y llegar a 0,90 cuesta especificidad | sens/espec con 0,5 y con el umbral elegido | 0,689/0,792 → 0,908/0,512 | Sí |
| H3: sin aumento hay más sobreajuste y menor AUC | val_loss y val_AUC | más sobreajuste (1,14 frente a 0,85), AUC igual (0,837 frente a 0,836) | Parcialmente |

**[BORRADOR]** Comenta qué aprendiste de que H3 se cumpliera solo en parte, y aclara que H1/H2 se reformularon el 19/11 con los resultados ya conocidos (está en el historial de Git).

## 9. Interfaz

`python app.py --run resnet18_base` (Gradio). Acepta PNG/JPG/BMP/WEBP de un recorte, muestra la clase, la puntuación, el umbral, el aviso de que la puntuación no es una probabilidad calibrada y el descargo de responsabilidad. Rechaza imágenes vacías o menores de 32×32. Evidencia: `runs/resnet18_base/prueba_interfaz.md` (una maligna con puntuación 0,206 → maligna; una benigna con 0,036 → benigna; imagen vacía → rechazada).

**[BORRADOR]** Agrega una captura de la interfaz (puedes tomarla de la celda C6 del cuaderno).

## 10. Limitaciones y consideraciones éticas

**[BORRADOR]** Cubre al menos:
- Solo masas, un único dataset (película digitalizada), subconjunto descargado; no generaliza a otras instituciones o equipos.
- Clasifica recortes ya localizados por un radiólogo; no detecta lesiones.
- Una sola semilla y un solo entrenamiento por configuración; el AUC oscila ±0,03 entre épocas.
- Especificidad de 0,50: muchos falsos positivos.
- La puntuación no es una probabilidad clínica calibrada; el umbral 0,045 es tan bajo porque el modelo sobreajustado da puntuaciones extremas.
- No apto para decisiones clínicas.

## 11. Reproducibilidad

- Semilla 42 (particiones y entrenamiento); configuración de cada corrida en `runs/<run>/config.json`.
- Entorno del cierre: Python 3.13.16, torch 2.14.1+cu130, torchvision 0.29.1+cu130, GPU Tesla T4 (`entorno.json`); versiones exactas en `requirements-lock.txt`.
- ResNet18 con aumento: 15 épocas en 167,7 s.
- Pasos: `prepare_data.py` → `check_split.py` → `train.py` → `evaluate.py` (ver `README.md`).

## 12. Conclusiones

**[BORRADOR]** 4–6 líneas tuyas: qué respondiste, qué funcionó (transferencia, partición por paciente, umbral elegido en validación), qué no (especificidad baja, sobreajuste) y qué harías después (más datos o calcificaciones, varias semillas, calibración, validación externa).

## Referencias

- Lee, R. S., Gimenez, F., Hoogi, A., Rubin, D. (2016). *Curated Breast Imaging Subset of DDSM* [Data set]. The Cancer Imaging Archive. https://doi.org/10.7937/K9/TCIA.2016.7O02S9CY
- Lee, R. S. et al. (2017). A curated mammography data set for use in computer-aided detection and diagnosis research. *Scientific Data*, 4, 170177.
- Clark, K. et al. (2013). The Cancer Imaging Archive (TCIA). *Journal of Digital Imaging*, 26(6), 1045–1057.
- He, K., Zhang, X., Ren, S., Sun, J. (2016). Deep residual learning for image recognition. *CVPR*.
- [Agrega las que uses en tu redacción.]

---

### Generar PDF y Word (cuando termines de redactar)

En Colab, desde la carpeta del proyecto:

```bash
!apt-get -qq install pandoc > /dev/null
!pandoc informe.md -o informe.docx
```
Abre `informe.docx` en Word o Google Docs, revisa el formato y expórtalo a PDF.
