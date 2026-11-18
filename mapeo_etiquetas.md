# Mapeo de etiquetas (dataset → proyecto)

Fuente: CBIS-DDSM (TCIA), columna `pathology` de los CSV `mass_case_description_train_set.csv` y `mass_case_description_test_set.csv` (solo masas).

| Etiqueta original | Significado | Etiqueta del proyecto |
|---|---|---|
| `BENIGN` | Lesión benigna con patología | 0 – benigna |
| `BENIGN_WITHOUT_CALLBACK` | Benigna, sin necesidad de volver a citar | 0 – benigna |
| `MALIGNANT` | Lesión maligna con patología | 1 – maligna |

Notas:
- No se usa la columna `assessment` (BI-RADS) como etiqueta.
- La etiqueta describe la **lesión**, no a la paciente.
- Se excluyeron 5 lesiones por no encontrarse su DICOM (1.696 filas en los CSV y 1.691 con imagen).
- Se agrupan BENIGN y BENIGN_WITHOUT_CALLBACK (141 de las 911 benignas); es una simplificación a documentar en las limitaciones.

## Datos del dataset
- Versión: Version 1: Updated 2017/09/14
- Licencia: CC BY 3.0
- Cita: Lee et al. (2016), Curated Breast Imaging Subset of DDSM, TCIA, DOI 10.7937/K9/TCIA.2016.7O02S9CY
- Subconjunto descargado: solo recortes y máscaras de masas, de los dos CSV oficiales (train y test): 1.799 series y 3.382 archivos DICOM (≈ 27 GB)
- Calcificaciones y mamografías completas: no usadas en este proyecto

## Datos del proyecto
- **Tamaño:** 892 pacientes y 1.691 lesiones (911 benignas y 780 malignas)
- **Vistas:** CC 779 y MLO 912
- **Particiones (por paciente, semilla 42):** train 1.174, val 244, test 273
