# Supuestos y limitaciones

- El documento docente no aporta ofertas, capacidades, distancias ni costos regionales completos. El botón de carga crea datos explícitamente **ficticios**, solo para demostración.
- Se adopta como predeterminado el modo BASE del modelo: oferta obligatoria (`=`) y capacidad máxima por planta (`≤`). Cada planta puede configurarse como demanda exacta o mínima; este supuesto requiere ratificación académica.
- Los costos directos son COP/t. Si se indica distancia y tarifa, el costo se calcula como distancia × tarifa, tal como define el modelo.
- El AG implementa el modo BASE para no reportar factibilidad errónea ante combinaciones aún no tratadas; el LP admite los tres tipos de demanda.
- HiGHS mediante `linprog` entrega duales locales, pero no rangos clásicos certificados sin cambio de base a través de esta interfaz; se implementan escenarios reoptimizados, no rangos simulados.
- HU-01 a HU-03, HU-53 y despliegue de HU-55 se descartan por la decisión fija de aplicación local sin autenticación ni API. La persistencia se realiza con SQLite y los errores de ejecución quedan en el estado e historial local.
