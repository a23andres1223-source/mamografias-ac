# Bitácora de proceso

Una fila por decisión o dificultad relevante. Escríbela **el mismo día**, con tus palabras. Enlaza la evidencia (commit, captura, archivo de `runs/`).

| Fecha | Dificultad / situación | Alternativas consideradas | Decisión | Evidencia | Contribución individual |
|---|---|---|---|---|---|
| 16/11/2026 | Configurar el entorno de trabajo | PC local sin GPU / Colab con GPU | Colab con GPU, Drive para respaldo y repo en GitHub | primer commit | Creé el repositorio en GitHub, generé el token de acceso, configuré Colab con GPU y conecté Drive con la carpeta Proyecto_Mamografias. Entendí que cada commit queda registrado con fecha y que data/ no se sube por el .gitignore. |
| 16/11/2026 | Definir qué clasifica el modelo y con qué etiquetas | Clasificar imagen completa, paciente o lesión | Lesión (recorte) con patología como etiqueta | hipotesis.md y mapeo_etiquetas.md |  elegí la unidad de análisis, redacté las hipótesis, entendí por qué se agrupan las etiquetas |
| 16/11/2026 | El dataset completo pesa ~163,6 GB y no cabe en Colab | Bajar todo, bajar solo recortes de masas, o usar una copia derivada | Solo recortes y máscaras de masas filtrando el manifiesto con los UID de los CSV | 1779 series a bajar de 6775 del manifiesto completo | Analicé el tamaño del dataset y decidí descargar únicamente los recortes de masas y sus máscaras ROI, filtrando el manifiesto mediante los UID de los CSV para evitar descargas innecesarias y optimizar el almacenamiento. |
| 16/11/2026 | Descargar las imágenes filtradas | NBIA Data Retriever o copia derivada en Kaggle | NBIA Data Retriever con el manifiesto filtrado, carpetas clásicas (-cd) | 3.382 archivos .dcm y 27 GB descargados | Tuve inconvenientes al organizar los archivos en Google Colab porque algunas rutas de las carpetas no coincidían con la estructura real del proyecto. Revisé la organización de los directorios para identificar las rutas correctas y evitar errores al copiar los archivos. |
