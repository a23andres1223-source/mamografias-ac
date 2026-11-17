# Conclusiones del análisis exploratorio

- **Datos:** Se encontraron 1.696 filas en los CSV de masas, de las cuales 1.691 tienen imagen disponible (5 excluidas por no encontrarse el DICOM). El conjunto contiene 892 pacientes: 911 lesiones benignas (53,9 %) y 780 malignas (46,1 %).

- **Particiones (por paciente, semilla 42):** train contiene 1.174 lesiones (624 pacientes), val 244 (134 pacientes) y test 273 (134 pacientes). La proporción de malignas es del 46,5 % en train, 48,8 % en val y 42,1 % en test. No se encontraron pacientes compartidos entre las particiones.

- **Equilibrio:** Las clases están relativamente equilibradas. El conjunto de prueba tiene una proporción algo menor de lesiones malignas que entrenamiento y validación. Esta diferencia debe tenerse en cuenta al interpretar métricas como precisión y F1, que pueden verse afectadas por la proporción de clases. El AUC no depende directamente de la prevalencia de cada clase.

- **Lesiones por paciente:** Cada paciente tiene en promedio 1,9 lesiones, con un mínimo de 1 y un máximo de 14. Esto demuestra que algunos pacientes presentan varias lesiones, por lo que fue importante agrupar por paciente durante la partición para evitar fuga de datos.

- **Tamaños:** El ancho medio general es aproximadamente 367,1 px y el alto medio 360,6 px. Las lesiones malignas presentan promedios ligeramente mayores que las benignas: 381,1 frente a 355,2 px de ancho y 372,9 frente a 350,1 px de alto. El área media también es mayor en las malignas (154.124,4 frente a 135.910,9). Sin embargo, existe variabilidad y estos tamaños no permiten determinar por sí solos la malignidad.

- **Posibles atajos:** El AUC del área es 0,570 y el de la intensidad es 0,530. El ancho y el alto tienen AUC de 0,563 y 0,570, respectivamente. Todos están relativamente cerca de 0,5, por lo que ninguna de estas variables por sí sola tiene una capacidad discriminativa importante. No se observa una señal fuerte de que el modelo pueda resolver la clasificación utilizando únicamente estas características.

- **Vistas y lado:** Se encontraron imágenes en las vistas CC y MLO para ambas clases. La vista CC contiene 420 lesiones benignas y 359 malignas, mientras que MLO contiene 491 benignas y 421 malignas. También hay lesiones de ambos lados: 416 benignas y 400 malignas del lado izquierdo, y 495 benignas y 380 malignas del derecho. No se observa una ausencia de alguna vista o lado en una de las clases.

- **Origen de los datos:** La partición se realizó por paciente mezclando los CSV oficiales de entrenamiento y prueba. Por tanto, no se conserva la separación oficial de CBIS-DDSM; se construyeron nuevas particiones de entrenamiento, validación y prueba para este experimento.

- **Sesgos y limitaciones:** El proyecto utiliza únicamente lesiones de tipo masa, un subconjunto de CBIS-DDSM y datos procedentes de un único conjunto de origen. La partición de validación contiene 119 lesiones malignas y la de prueba 115, por lo que las métricas pueden presentar variabilidad. Además, las diferencias de distribución entre particiones y las características propias del conjunto limitan la generalización de los resultados a otros datos o instituciones.

- **Decisiones a partir del EDA:** Se trabajará con imágenes en escala de grises y se utilizará un tamaño de entrada uniforme de 224 × 224 píxeles, conservando la proporción de las imágenes mediante relleno antes del redimensionamiento. Se mantendrá la separación por paciente. Debido al equilibrio relativamente cercano entre las clases, se evaluará si es necesario utilizar pesos de clase en lugar de asumir que son obligatorios. También se revisarán visualmente los recortes para comprobar que correspondan a imágenes mamográficas y no a máscaras ROI.
