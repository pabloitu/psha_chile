# Nota para Sergio: catálogo PSHA Chile (10 nov 2026)

Hola Sergio,

Avancé con el catálogo usando el orden de fuentes que conversamos: Ruiz y Madariaga (2018) para los grandes, Centennial, ISC-GEM, Potin, CSN y Cabello solo antes de 1900. El detalle por período y por propiedad (magnitud, epicentro, profundidad, mecanismo) está en la tabla adjunta (`PREFERENCES.md`). Te dejo algunas preguntas y lo que propongo en cada caso. Si no ves problema, sigo con eso.

## 1. Centennial vs ISC-GEM (1904–1999)

Revisando los dos catálogos encontré que:
- Las magnitudes del Centennial no están recalculadas. Para Chile antes de 1976 son Mw de Pacheco y Sykes (1992) en los eventos someros, y mB de Abe en los de profundidad intermedia (por ejemplo, Calama 1950 mB 7.7 y La Ligua 1965 mB 7.4).
- ISC-GEM recalculó Ms y mb desde las amplitudes y los convirtió a Mw con incertidumbre. Además relocalizó todos los eventos.
- El Centennial no está relocalizado en 1904–1917 ni en 1943–1955 (entre ellos Chillán 1939, Illapel 1943 y Magallanes 1949). En esos años el epicentro es el de G&R, Abe o ISS, a menudo en grados enteros y sin profundidad.

**Propuesta:**
- **Magnitud:** ISC-GEM primero, Centennial como control.
- **Epicentro:** Centennial donde está relocalizado por EHB (1918–1942 y desde 1956), ISC-GEM en 1904–1917 y 1943–1955.

¿Te parece, o tu orden "Centennial primero" vale también para la magnitud?

## 2. Eventos bajo los umbrales globales antes de 1982

El catálogo final se corta en Mw 4.5. Antes de 1982, los catálogos globales llegan solo a M ≈ 6.5 (antes de 1964) y a M ≈ 5.5 (1964–1981).

**Propuesta:**
- Para 1964–1981, tomar los eventos de M 4.5–5.5 del boletín ISC, con su mb convertido a Mw, y dejar que el análisis de completitud decida si ese período entra en los ajustes.
- Antes de 1964, no incluir eventos bajo los umbrales.

¿Lo harías distinto?

## 3. Fechas y datos de Ruiz y Madariaga (2018)

La Tabla 1 no coincide con el texto en algunos eventos. Donde hay una fuente independiente (Centennial, Lomnitz 2004, GCMT), uso la lectura que esa fuente confirma:

| evento | Tabla 1 / texto | usaré | apoyo |
|---|---|---|---|
| Copiapó 1918 | 4 dic (tabla) / 18 dic (texto), Mw 7.8 | 4 dic 1918 | Centennial: 1918-12-04 11:47, 27.27°S 73.46°W, Mw 7.5. Lomnitz tiene un evento el 18 dic en Copiapó (7–7.5, tsunami en Caldera): ¿podrían ser dos eventos? |
| Arauco 1975 | 14 oct | 10 may 1975 | Centennial: 1975-05-10 14:27, Mw 7.7; ningún M ≥ 7 chileno en octubre de 1975 |
| Copiapó 1983 | 4 nov, Mw 7.4 (tabla) / 4 oct, Mw 7.7 (texto) | 4 oct 1983, Mw 7.7 | Centennial y Harvard: 1983-10-04 18:52, Mw 7.7 |
| Antofagasta 1995 | 30 jul (tabla) / 31 jul (texto) | 30 jul 1995 | 1995-07-30 05:11 UTC |
| Copiapó "1959" | 5 oct 1959 (p. 9) | 5 oct 1859 | Lomnitz: 5 oct 1859, M 7.5 |

Hay tres puntos que no puedo resolver con otras fuentes:
- **Taltal 1966:** dominio B en la Tabla 1 y C (interfaz profunda) en el texto. ¿Cuál vale?
- **Pica:** 1768 en las secciones 3.1.3 y 3.1.5.1, y 1786 en el resumen y en la p. 16. ¿Cuál es el año?
- **Santiago 1647:** lo clasifican como intraplaca de profundidad intermedia citando a Lomnitz, pero Lomnitz (2004) sugiere una fuente cortical (falla San Ramón o del batolito costero). ¿Lo dejamos como intraplaca? Importa para el Mmax intraplaca.

## 4. CSN después de 2020-07-16

Potin et al. termina el 2020-07-16. Desde ahí uso el catálogo publicado del CSN (páginas diarias de sismologia.cl, desde 2020-01-01 para tener traslape con Potin). Ese catálogo no está relocalizado.

¿Existe una versión relocalizada después de 2020-07, o una extensión del catálogo de Potin, que pueda usar?

## 5. Magnitudes de Potin et al. (2024)

El archivo trae los códigos `l` (ML), `c` (coda), `ww` (W-phase, desde 2014), `W` (1995–2016) y `B` (9 eventos). El paper dice que las magnitudes se homogeneizaron, pero no da el método.

Mientras no tenga esa información, uso las magnitudes de Potin solo como control. La Mw de cada evento sale de GCMT, Mww de CSN o USGS, o de la ML de CSN y el mb del boletín ISC convertidos.

¿Me puedes confirmar:
- qué son `W` y `B`, en comparación con `ww`?
- si hubo alguna homogeneización entre Mc, ML y Mw?

## 6. Doble zona sísmica

Según la literatura, la doble zona no es solo de profundidad intermedia. Entre 19 y 24°S el plano inferior empieza a unos 45–50 km y los planos se juntan a 80–120 km. En Chile central va de 50 a 100–120 km. Al sur de unos 33–35°S no está documentada.

Propongo buscarla en los datos entre unos 45 y 120 km, y no solo en la intraplaca intermedia. ¿Estás de acuerdo? ¿Sabes de evidencia al sur de 35°S?

Saludos,
Pablo
