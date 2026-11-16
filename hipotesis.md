# Comprensión del problema e hipótesis

> Los textos de ejemplo son un punto de partida. **Reescríbelos con tus palabras y tu criterio** antes de experimentar: la guía exige hipótesis propias.

## Usuario, unidad de análisis y etiquetas
- **Usuario previsto:** estudiantes/educación (contexto académico). No es una herramienta clínica.
- **Unidad de análisis:** la **lesión** (recorte/ROI de una mamografía) con patología conocida. No es la paciente, ni la mama, ni el examen.
- **Etiquetas:** *maligna* = lesión con patología MALIGNANT; *benigna* = BENIGN o BENIGN_WITHOUT_CALLBACK. Son etiquetas de **patología de una lesión**, no un diagnóstico de la paciente.

## Costo de los errores
- **Falso negativo** (maligna clasificada como benigna): el error más grave; un caso sospechoso quedaría sin seguimiento.
- **Falso positivo** (benigna clasificada como maligna): genera ansiedad, pruebas y biopsias innecesarias, pero suele ser menos grave.
- Por eso se prioriza la **sensibilidad de malignidad**, aceptando perder algo de especificidad.

## Hipótesis (reescribe con tus palabras)
1. **H1 (modelo):** [Ej.] ResNet18 con transferencia superará a la línea base en ROC-AUC de validación, porque dispone de filtros preentrenados y el conjunto es pequeño.
2. **H2 (umbral/sensibilidad):** [Ej.] Con umbral 0.5 la sensibilidad de malignidad será menor que la especificidad; bajar el umbral hasta lograr sensibilidad ≥ 0.90 en validación reducirá la especificidad.

## Limitaciones
- Pocos pacientes y un subconjunto posiblemente sesgado; escáneres/digitalización de un solo conjunto de datos.
- Se clasifica el recorte ya localizado por un radiólogo; no se detecta la lesión.
- La puntuación del modelo no es una probabilidad clínica calibrada.
