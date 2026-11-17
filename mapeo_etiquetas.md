# Mapeo de etiquetas (dataset → proyecto)

Fuente: CBIS-DDSM (TCIA), columna `pathology` de los CSV `calc_*` y `mass_*`.

| Etiqueta original | Significado | Etiqueta del proyecto |
|---|---|---|
| `BENIGN` | Lesión benigna con patología | 0 – benigna |
| `BENIGN_WITHOUT_CALLBACK` | Benigna, sin necesidad de volver a citar | 0 – benigna |
| `MALIGNANT` | Lesión maligna con patología | 1 – maligna |

Notas:
- No se usa la columna `assessment` (BI-RADS) como etiqueta.
- Filas con otra patología o sin imagen encontrada se **excluyen** y se cuentan en la salida de `prepare_data.py` (anótalas en el informe).
- La etiqueta describe la **lesión**, no a la paciente.

Datos a documentar en el informe (rellena): versión del dataset ____ | licencia ____ | nº pacientes ____ | nº lesiones ____ | vistas CC/MLO ____ | subconjunto descargado ____

## Datos del dataset 
- Versión: Version 1: Updated 2017/09/14
- Licencia: CC BY 3.0 
- Cita: Lee et al. (2016), Curated Breast Imaging Subset of DDSM, TCIA, DOI 10.7937/K9/TCIA.2016.7O02S9CY
- Subconjunto descargado: solo recortes y máscaras de masas ([2 CSV / solo el CSV de entrenamiento])
- Calcificaciones: no usadas en este proyecto

## Datos del dataset 
- Versión: Version 1: Updated 2017/09/14
- Licencia: CC BY 3.0 
- Cita: Lee et al. (2016), Curated Breast Imaging Subset of DDSM, TCIA, DOI 10.7937/K9/TCIA.2016.7O02S9CY
- Subconjunto descargado: solo recortes y máscaras de masas ([2 CSV / solo el CSV de entrenamiento])
- Calcificaciones: no usadas en este proyecto

## Datos del dataset 
- Versión: Version 1: Updated 2017/09/14
- Licencia: CC BY 3.0 
- Cita: Lee et al. (2016), Curated Breast Imaging Subset of DDSM, TCIA, DOI 10.7937/K9/TCIA.2016.7O02S9CY
- Subconjunto descargado: solo recortes y máscaras de masas ([2 CSV / solo el CSV de entrenamiento])
- Calcificaciones: no usadas en este proyecto
