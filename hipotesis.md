# Comprensión del problema e hipótesis

## Usuario, unidad de análisis y etiquetas
- **Usuario previsto:** estudiantes y docentes de la asignatura. Es un prototipo educativo, no una herramienta clínica ni de apoyo al diagnóstico.
- **Unidad de análisis:** una lesión (masa) representada por su recorte en la mamografía, con la patología confirmada como etiqueta. No es la paciente, ni la mama, ni el examen.
- **Etiquetas:** maligna = patología MALIGNANT. Benigna = BENIGN o BENIGN_WITHOUT_CALLBACK, porque en ambos casos la patología no encontró cáncer. Son etiquetas de la lesión, no un diagnóstico de la paciente.

## Costo de los errores
- **Falso negativo** (maligna clasificada como benigna): es el error más grave, porque una lesión sospechosa quedaría sin seguimiento.
- **Falso positivo** (benigna clasificada como maligna): genera ansiedad y estudios adicionales, pero es menos grave.
- Por eso priorizo la **sensibilidad** de la clase maligna, aceptando perder algo de especificidad.

## Hipótesis
1. **H1 (modelo):** ResNet18 con transferencia de aprendizaje obtendrá un ROC-AUC de validación mayor que la línea base (CNN pequeña desde cero), porque parte de filtros ya entrenados y mi conjunto es pequeño. Se verifica comparando el `val_AUC` de ambos entrenamientos.
2. **H2 (umbral):** con umbral 0.5 la sensibilidad de la clase maligna será menor que la especificidad. Al bajar el umbral hasta lograr sensibilidad ≥ 0.90 en validación, la especificidad disminuirá, porque el modelo marcará como malignas más lesiones dudosas. Se verifica comparando sensibilidad y especificidad con ambos umbrales.

## Limitaciones
- Uso solo masas y un subconjunto de CBIS-DDSM, con pocos pacientes y un único origen de datos, por lo que los resultados pueden no generalizar.
- El modelo clasifica recortes ya localizados por un radiólogo. No detecta lesiones.
- La puntuación del modelo no es una probabilidad clínica calibrada.

## H3 (aumento de datos) — escrita el 18/11/2026
- **Hipótesis:** sin aumento de datos, ResNet18 sobreajustará más: el val_loss subirá más y el val_AUC será menor que con aumento.
- **Cómo la contrasté:** entrené `resnet18_sin_aug` (mismo modelo, semilla y épocas, con `--no-augment`) y comparé con `resnet18_base`.
- **Resultado:** el sobreajuste fue mayor (train_loss final 0,011 frente a 0,113; val_loss máximo 1,14 frente a 0,85), pero el mejor val_AUC fue igual (0,837 frente a 0,836).
- **Conclusión:** se cumple la parte del sobreajuste, no la del AUC. 
- **Limitaciones:** un solo entrenamiento por modelo, una semilla y 244 lesiones de validación; el AUC varía ±0,03 entre épocas.
