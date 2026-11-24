# Comprensión del problema e hipótesis

## Usuario, unidad de análisis y etiquetas
- **Usuario previsto:** estudiantes y docentes de la asignatura. Es un prototipo educativo, no una herramienta clínica ni de apoyo al diagnóstico.
- **Unidad de análisis:** una lesión (masa) representada por su recorte en la mamografía, con la patología confirmada como etiqueta. No es la paciente, ni la mama, ni el examen.
- **Etiquetas:** maligna = patología MALIGNANT. Benigna = BENIGN o BENIGN_WITHOUT_CALLBACK, porque en ambos casos la patología no encontró cáncer. Son etiquetas de la lesión, no un diagnóstico de la paciente.

## Costo de los errores
- **Falso negativo** (maligna clasificada como benigna): es el error más grave, porque una lesión sospechosa quedaría sin seguimiento.
- **Falso positivo** (benigna clasificada como maligna): genera ansiedad y estudios adicionales, pero es menos grave.
- Por eso priorizo la **sensibilidad** de la clase maligna, aceptando perder algo de especificidad.

## Hipótesis (reformuladas el 19/11/2026, con los resultados ya conocidos)
1. **H1 (modelo):** Esperaba que ResNet18 preentrenada superara a la CNN pequeña en AUC de validación, porque con solo 1.174 lesiones de entrenamiento una red desde cero tiene poco material para aprender texturas y la preentrenada ya trae filtros útiles. Criterio: diferencia de más de 0,05, que es mayor que la oscilación de ±0,03 que veo entre épocas. La refutaría una diferencia menor. Resultado: 0,836 frente a 0,634, así que se cumple.
2. **H2 (umbral y sensibilidad):** Con el umbral 0,5 esperaba una sensibilidad menor que la especificidad. Para llegar a sensibilidad ≥ 0,90 tendría que bajar el umbral y perder especificidad. La refutaría llegar a 0,90 sin perderla. Resultado: con 0,5, sensibilidad 0,689 y especificidad 0,792; con 0,045, sensibilidad 0,908 y especificidad 0,512, así que se cumple.

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
