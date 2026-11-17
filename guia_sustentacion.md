# Guía de sustentación: preguntas probables y cómo pensarlas

Practica respondiéndolas **en voz alta con tus palabras**. Si no puedes explicar una respuesta, vuelve al código correspondiente y ejecútalo.

## Problema y datos
1. **¿Qué clasifica tu modelo?** Recortes de lesiones mamográficas en benigna/maligna según patología. No diagnostica pacientes.
2. **¿Por qué la lesión como unidad y no la imagen o la paciente?** Porque CBIS-DDSM trae patología por lesión; la etiqueta es de la lesión.
3. **¿Qué significa maligna/benigna aquí?** Resultado de patología (`pathology`), no BI-RADS. BI-RADS sería sospecha radiológica, no cáncer confirmado.
4. **¿Por qué CBIS-DDSM?** Tiene patología y ROI por lesión; es el recomendado para tarea binaria. (Di también sus límites: subconjunto, un solo origen.)
5. **¿Qué excluiste y por qué?** Filas con patología desconocida, duplicados y lesiones sin imagen. (Mira la salida de `prepare_data.py`.)

## Fuga de datos y partición
6. **¿Qué es fuga de datos?** Que información de prueba influya en el entrenamiento; aquí, imágenes de la misma paciente en train y test.
7. **¿Cómo la evitaste?** `GroupShuffleSplit` agrupando por `patient_id` en `prepare_data.py`, y lo compruebo con `check_split.py`.
8. **¿Por qué importa si la exactitud sube?** El modelo podría reconocer a la paciente y no la lesión; la métrica sería engañosa y no generalizaría.
9. **¿Para qué sirve cada partición?** Train ajusta pesos; val elige época, hiperparámetros y umbral; test se usa una vez al final.

## Preprocesamiento
10. **¿Por qué percentiles 1–99 al pasar a 8 bits?** Evita que píxeles extremos aplasten el contraste (`imaging.py`).
11. **¿Por qué `PadToSquare` y 224×224?** Para no deformar la lesión y por el tamaño esperado por ResNet18.
12. **¿Por qué normalizar con media/desv. de ImageNet?** Los modelos preentrenados se entrenaron así.
13. **¿Por qué aumentos solo en train?** Aumentar val/test cambiaría lo que mides. Los aumentos regularizan el entrenamiento.
14. **¿Por qué 3 canales si es escala de grises?** El modelo preentrenado espera RGB; se repite el canal.

## Modelado
15. **¿Qué es transferencia de aprendizaje y por qué aquí?** Reutilizar filtros aprendidos en ImageNet y ajustar la capa final (y/o el resto); útil con pocos datos.
16. **¿Qué es tu línea base y para qué?** Una CNN pequeña desde cero; da una referencia para saber si la transferencia aporta.
17. **¿Qué hacen los pesos de clase?** Penalizan más los errores en la clase minoritaria para compensar el desbalance.
18. **¿Cómo elegiste la mejor época?** Por ROC-AUC de **validación**, nunca por prueba.
19. **¿Qué experimento controlado hiciste?** Cambié una sola decisión (ej. aumentos sí/no) manteniendo semilla y partición; compara val_AUC y sensibilidad.

## Evaluación
20. **Define sensibilidad, especificidad, precisión, F1.** Sensibilidad = TP/(TP+FN); especificidad = TN/(TN+FP); precisión = TP/(TP+FP); F1 = media armónica de precisión y sensibilidad.
21. **¿Qué es ROC-AUC?** Probabilidad de que una maligna reciba mayor puntuación que una benigna; no depende del umbral.
22. **¿Qué pasa si bajas el umbral?** Sube la sensibilidad, bajan la especificidad y la precisión; más falsos positivos.
23. **¿Cómo elegiste el umbral?** Con validación (`--target-sensitivity`), nunca con prueba.
24. **¿Puntuación del modelo = probabilidad clínica?** No; no está calibrada y depende del conjunto de entrenamiento.
25. **Muéstrame un falso negativo y qué crees que pasó.** Usa `errors_val.csv` y `fn_grid_val.png`; da una hipótesis prudente (lesión sutil, calidad, recorte).
26. **¿Qué riesgos de sobreajuste hay?** Pocos pacientes, modelo grande; mira la curva train_loss vs val_loss en `history.csv`.
27. **¿Qué limita la generalización?** Un solo dataset, sesgo de selección, subconjunto descargado, un tipo de escáner/digitalización.

## Ética y alcance
28. **¿Por qué no sirve para decisiones médicas?** Es un prototipo educativo, sin validación clínica ni calibración, entrenado con pocos datos.
29. **¿Qué parte de tu trabajo usó IA?** Revisa `registro_ia.md` y sé honesto sobre qué entiendes y qué contrastaste.

## Cambios en vivo (practícalos)
- Subir/bajar umbral y ver cómo cambia la matriz de confusión.
- Encontrar un falso negativo concreto y abrir su imagen.
- Mostrar que ningún `patient_id` se repite entre particiones.
- Quitar o cambiar una transformación en `get_transforms()` y explicar el efecto esperado.
