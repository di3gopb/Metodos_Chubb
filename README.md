## README MÉTODOS
Para el análisis de este proyecto nos centraremos en la compañía Chubb a pesar de haber colocado otras dos empresas

Inciso a)
El código descarga automáticamente información histórica del activo seleccionado desde Yahoo Finance, tomando datos diarios desde el año 2010. A partir de los precios de cierre ajustados, se construye la base principal que se usa en todo el proceso de cálculos.
Inciso b)
Con los precios descargados, el código calcula los rendimientos diarios del activo. Después obtiene medidas descriptivas básicas de la serie: media, desviación estándar, sesgo y exceso de curtosis, las cuales se muestran dentro de Streamlit.
Para la acción de Chubb a día 1 de mayo se obtuvieron los siguientes resultados de los rendimientos:
Media: 0.000638
Esto indica que el rendimiento promedio diario es de 0.0638%, lo cual puede considerarse un rendimiento positivo moderado y consistente con un activo financiero estable en el largo plazo.
Desviación estándar: 0.013799
En términos porcentuales, equivale a aproximadamente 1.38% diario, lo que sugiere una volatilidad relativamente alta en comparación con la media. Esto implica que, aunque el rendimiento promedio es positivo, las fluctuaciones diarias pueden ser considerablemente mayores.
Exceso de Curtosis: 11.17
Este valor es significativamente mayor que cero, lo que indica que la distribución de los rendimientos presenta colas pesadas. En interpretación financiera, esto significa que existen mayores probabilidades de observar eventos extremos (grandes pérdidas o ganancias) en comparación con una distribución normal la cual tendría una curtosis de 3
Sesgo: -0.4170
El sesgo negativo indica que la distribución de los rendimientos está ligeramente inclinada hacia la izquierda, es decir, existe una mayor probabilidad de observar rendimientos negativos extremos que positivos. Esto es relevante notarlo en el análisis de riesgo, ya que sugiere mayor exposición a caídas fuertes.
Inciso c)
En este inciso el código calcula el VaR y el ES/CVaR para toda la serie completa de rendimientos diarios del activo seleccionado. Para ello, primero obtiene la media y la desviación estándar de los rendimientos, ya que estos parámetros son fundamentales en los métodos paramétricos. Para estos cálculos se utilizan las librerías NumPy y SciPy , que permiten trabajar con distribuciones de probabilidad y funciones estadísticas.
Para los métodos paramétricos, el código estima el VaR y el ES/CVaR suponiendo dos distribuciones distintas: la distribución normal y la t-Student. En ambos casos, se utilizan funciones de la librería spicy.stats, como norm.ppf y t.ppf, para calcular los cuantiles correspondientes a los niveles de confianza 95%, 97.5% y 99%, considerando la cola izquierda (porque estamos viendo las pérdidas). El ES/CVaR se calcula utilizando fórmulas analíticas basadas en la densidad de cada distribución.
Posteriormente, el código implementa el método histórico, en el cual no se asume ninguna distribución teórica. Aquí se utilizan funciones de Pandas que nos dan el cuantil para obtener directamente los cuantiles empíricos de los rendimientos observados, que representan el VaR. El ES/CVaR se calcula como el promedio de los rendimientos que se encuentran por debajo del VaR, capturando así el comportamiento de las pérdidas más extremas.
Finalmente, se aplica una aproximación por Monte Carlo, utilizando la librería NumPy. En este proceso, el código genera una gran cantidad de simulaciones (En nuestro código 1,000,000) de rendimientos aleatorios. Para el caso normal, se usa np.random.normal, tomando como parámetros la media y desviación estándar de los datos reales. Para el caso t-Student, se generan valores con np.random.standard_t y posteriormente se escalan usando la media y desviación estándar.
Una vez generadas las simulaciones, el VaR se calcula nuevamente como el percentil correspondiente de los rendimientos simulados , mientras que el ES/CVaR se obtiene como el promedio de los valores simulados que se encuentran por debajo del VaR. Este método permite aproximar la distribución de pérdidas sin depender completamente de supuestos teóricos, incorporando además mayor flexibilidad para modelar eventos extremos
Análisis de resultados (Chubb):

En primer lugar, se observa que el VaR bajo distribución normal y Monte Carlo normal presentan resultados muy similares en todos los niveles de confianza (por ejemplo, alrededor de -2.2% al 95% y -3.14% al 99%). Esto es consistente, ya que ambos métodos asumen implícitamente una distribución normal de los rendimientos.
Por otro lado, el modelo t-Student, tanto en su versión paramétrica como en Monte Carlo, tiende a generar valores más extremos, especialmente conforme aumenta el nivel de confianza. Esto se aprecia claramente en el caso del 99%, donde el VaR Monte Carlo t-Student alcanza aproximadamente -4.56%, siendo el más alto entre todos los métodos. Esto refleja la capacidad de esta distribución para capturar colas más pesadas.
El método histórico presenta un comportamiento intermedio en el VaR, pero en el caso del ES/CVaR se vuelve considerablemente más conservador. Por ejemplo, al 97.5%, el ES histórico es cercano a -4.00%, superando a los métodos paramétricos. Esto indica que, aunque el VaR histórico no siempre es el más extremo, el ES sí captura pérdidas más severas cuando se presentan eventos negativos en los datos reales.
Adicionalmente, se cumple que en todos los casos el ES/CVaR es más negativo que el VaR, lo cual es esperado, ya que el ES mide la pérdida promedio en los peores escenarios y no solo un percentil específico.
Finalmente, se observa que conforme aumenta el nivel de confianza (de 95% a 99%), tanto el VaR como el ES se vuelven más negativos en todos los métodos, lo que refleja un incremento en la severidad de las pérdidas extremas consideradas.
En conjunto, los resultados muestran que los métodos que consideran colas pesadas o datos históricos (t-Student y método histórico) tienden a ofrecer estimaciones de riesgo más conservadoras, mientras que la aproximación normal tiende a subestimar el riesgo en presencia de eventos extremos.



INCISO D)

Descripción del código 
El presente código implementa el cálculo y análisis de medidas de riesgo financiero a partir de una serie de rendimientos, específicamente el Value at Risk (VaR) y el Expected Shortfall (ES o CVaR), utilizando tanto enfoques paramétricos como históricos bajo un esquema de ventanas móviles de 252 observaciones.

A partir del DataFrame generado previamente, se extrae la columna correspondiente a los rendimientos mediante:

returns = df_precios["Rendimiento"].squeeze()

El método .squeeze() permite transformar la estructura en una Serie de pandas, lo cual facilita la aplicación de funciones como rolling, quantile y apply.
Posteriormente, se calculan la media y la desviación estándar móviles utilizando ventanas de tamaño 252, lo que corresponde aproximadamente a un año de datos bursátiles. Estas estadísticas móviles permiten capturar la evolución temporal del comportamiento de los rendimientos y, por lo tanto, del riesgo.


VaR paramétrico

El VaR paramétrico se calcula bajo el supuesto de que los rendimientos siguen una distribución normal. En este caso, el VaR se obtiene mediante:

VaR_alpha = mu - sigma * z_alpha

donde:

z_alpha = Phi^{-1}(1 - alpha)

En el código, esto se implementa mediante la función norm.ppf, la cual calcula el cuantil correspondiente dado el nivel de confianza, la media y la desviación estándar móviles.


VaR histórico

El VaR histórico no asume ninguna distribución, sino que utiliza directamente los cuantiles empíricos:

VaR_alpha = cuantil empírico de nivel (1 - alpha)

Esto permite capturar características reales de los datos como asimetría y colas pesadas.


Expected Shortfall (ES / CVaR)

El ES mide la pérdida promedio en los peores escenarios, es decir, aquellos en los que se supera el VaR.

El ES puede definirse como:

ES_alpha = E[L | L >= VaR_alpha]

donde L representa la pérdida.

Esta definición indica que el ES mide el valor esperado de las pérdidas dado que estas se encuentran en la cola de la distribución.

De manera equivalente, el ES también puede expresarse como:

ES_alpha = (1 / (1 - alpha)) * integral de alpha a 1 de q_u(L) du

donde q_u(L) representa el cuantil de nivel u de la distribución de pérdidas.

Esta expresión indica que el ES es el promedio de los cuantiles en la cola de la distribución, es decir, un promedio de los peores escenarios.


Ambas definiciones del ES son equivalentes: la primera lo interpreta como una esperanza condicional, mientras que la segunda lo interpreta como un promedio de cuantiles en la cola de la distribución.

En el código no trabajamos directamente con pérdidas L, sino con rendimientos R. Como las pérdidas corresponden a rendimientos negativos, la cola relevante se encuentra en la parte izquierda de la distribución de rendimientos.

Por ello, cuando se calcula el VaR y el ES con rendimientos, se utiliza:

1 - alpha

Por ejemplo:

- Para alpha = 0.95 → se usa el cuantil 0.05
- Para alpha = 0.99 → se usa el cuantil 0.01


Para el enfoque paramétrico se asume que los rendimientos siguen una distribución normal:

R ~ N(mu, sigma^2)

Esto puede reescribirse como:

R = mu + sigma * Z, con Z ~ N(0,1)

Esto significa que cualquier rendimiento puede expresarse como una combinación de su media, su desviación estándar y una variable normal estándar.

En el código, como se utilizan ventanas móviles, estos parámetros cambian en el tiempo:

media_movil = returns.rolling(window=252).mean()  
desviacion_movil = returns.rolling(window=252).std()

Por lo tanto:

R_t = mu_t + sigma_t * Z


Cuantiles de la normal estándar

Se calculan los valores:

z_95 = norm.ppf(1 - 0.95)  
z_99 = norm.ppf(1 - 0.99)

Estos representan cuantiles de la normal estándar en la cola izquierda:

- z_95 ≈ -1.645  
- z_99 ≈ -2.326  

Estos valores indican cuántas desviaciones estándar por debajo de la media se encuentran los eventos extremos.


Bajo el supuesto de normalidad, la expresión integral del ES puede resolverse analíticamente, obteniendo:

ES_alpha = mu - sigma * (phi(z_alpha) / (1 - alpha))

donde:

- phi(z_alpha) es la densidad de la normal estándar evaluada en z_alpha  
- 1 - alpha es la probabilidad de la cola  

En el código, esto se implementa como:

media_movil - desviacion_movil * (norm.pdf(z_alpha) / (1 - alpha))

Esto evita calcular la integral directamente y utiliza el resultado analítico.


 ES histórico

El ES histórico se calcula directamente a partir de los datos. Para cada ventana móvil:

1. Se obtiene el VaR histórico  
2. Se promedian los rendimientos menores o iguales a ese VaR  

Esto se implementa como:

x[x <= x.quantile(1 - alpha)].mean()

Este método no asume ninguna distribución y refleja directamente el comportamiento de los datos.


## Visualización

El código genera una gráfica que incluye:

- Rendimientos  
- VaR paramétrico (95% y 99%)  
- VaR histórico (95% y 99%)  
- ES paramétrico (95% y 99%)  
- ES histórico (95% y 99%)  

Esto permite comparar el comportamiento de las distintas metodologías y observar cómo evoluciona el riesgo en el tiempo.

# Análisis de resultados

El código genera como salida principal una serie de tablas que muestran los valores más recientes de las medidas de riesgo calculadas. En particular, se presentan los últimos valores del VaR y del ES (tanto paramétricos como históricos), los cuales se obtienen a partir de ventanas móviles de 252 observaciones. Esto implica que cada estimación refleja el comportamiento del riesgo considerando aproximadamente un año de información previa.

Sin embargo, la forma más clara de interpretar los resultados es a través de la gráfica, ya que permite analizar de manera conjunta los rendimientos y las distintas medidas de riesgo a lo largo del tiempo.

En la gráfica se identifica un evento particularmente relevante: una caída abrupta en los rendimientos durante el año 2020. Este comportamiento es consistente con el contexto de la pandemia de COVID-19. Dado que el activo analizado pertenece al sector asegurador, este resultado es coherente, ya que dicho sector se vio fuertemente afectado por el incremento en hospitalizaciones, siniestros y defunciones.

A partir de este punto, se pueden comparar las distintas medidas de riesgo.

En primer lugar, se observa que el ES/CVaR histórico al 99% es, en la mayoría de los casos, la medida más restrictiva, es decir, la que refleja mayores pérdidas. Esto se debe a que este indicador toma directamente los peores datos observados y calcula un promedio de esos escenarios extremos. Como resultado, es la medida que más se acerca a la magnitud de la caída observada en 2020.

No obstante, también se aprecia que en varios periodos esta misma medida tiende a ser demasiado conservadora, generando estimaciones más negativas que los rendimientos que realmente se presentan. Esto ocurre porque el método histórico incorpora eventos extremos pasados incluso cuando las condiciones actuales del mercado son más estables.

Por otro lado, las medidas paramétricas muestran un comportamiento más estable a lo largo del tiempo. En general, tanto el VaR como el ES paramétricos tienden a ubicarse por encima (es decir, menos negativos) que sus equivalentes históricos. Esto se debe a que el método paramétrico suaviza los datos al asumir una distribución normal, lo cual reduce el impacto de valores extremos.

Este efecto se observa con mayor claridad en el VaR paramétrico al 95%, que en muchos casos resulta ser la estimación menos conservadora. En varios periodos, este indicador se queda corto frente a caídas reales en los rendimientos, lo que indica que subestima el riesgo en escenarios adversos. Sin embargo, en condiciones normales, logra ajustarse de manera razonable al comportamiento promedio del mercado.

Asimismo, aunque el nivel de confianza aumenta al 99%, las versiones paramétricas siguen siendo menos extremas que las históricas en varios tramos de la gráfica, lo que refuerza la idea de que este enfoque no captura completamente eventos de alta severidad.

En conjunto, los resultados muestran que:

- El enfoque histórico reacciona con mayor fuerza a eventos extremos, lo que le permite capturar mejor caídas severas, aunque a veces exagera el riesgo en periodos tranquilos.
- El enfoque paramétrico es más estable y menos volátil, pero tiende a subestimar pérdidas importantes.

Finalmente, se observa que el ES es consistentemente más conservador que el VaR en todos los casos, lo cual es coherente con su definición, ya que considera el promedio de las pérdidas más extremas en lugar de un solo punto de corte.

En conclusión, el uso conjunto de estas medidas permite obtener una visión más completa del riesgo, combinando estabilidad en la estimación con sensibilidad ante eventos extremos.

INCISO E)

Descripción del código 
El presente código implementa el análisis de violaciones de medidas de riesgo financiero, específicamente del Value at Risk (VaR) y del Expected Shortfall (ES o CVaR), tanto bajo enfoques paramétricos como históricos.
A partir de los resultados previamente calculados (VaR y ES móviles), se construye un DataFrame que integra los rendimientos diarios junto con las distintas medidas de riesgo, todo expresado en porcentaje. Esto permite comparar directamente los valores observados con los umbrales de riesgo estimados.
Posteriormente, se identifica en qué momentos los rendimientos reales superan (en términos negativos) las medidas de riesgo, lo cual se conoce como violación.
Concepto de violaciones
Una violación ocurre cuando el rendimiento observado es menor que el nivel de riesgo estimado. En términos formales:
Violación ⇔ R_t < Medida de riesgo_t
Dado que los rendimientos negativos representan pérdidas, una violación indica que la pérdida real fue mayor a la estimada por el modelo.
Este concepto es fundamental en la validación de modelos de riesgo, ya que permite evaluar qué tan bien las medidas (VaR o ES) capturan eventos extremos.
Construcción del DataFrame
El código comienza creando una estructura que concentra toda la información relevante:
Rendimientos diarios (en porcentaje)
VaR paramétrico (95% y 99%)
VaR histórico (95% y 99%)
ES paramétrico (95% y 99%)
ES histórico (95% y 99%)
Esto se realiza mediante la integración de las tablas previamente calculadas.
Posteriormente, se eliminan las filas con valores faltantes utilizando:
df_violaciones = df_violaciones.dropna()
Esto asegura que todas las comparaciones se realicen sobre datos completos, evitando sesgos en el análisis.
Cálculo de violaciones 
Para cada medida de riesgo, se evalúa si ocurre una violación mediante una comparación directa:
df_violaciones["Rendimientos"] < df_violaciones[columna]
Este proceso se automatiza mediante un ciclo que recorre todas las medidas de riesgo consideradas:
VaR paramétrico (95% y 99%)
VaR histórico (95% y 99%)
ES paramétrico (95% y 99%)
ES histórico (95% y 99%)
Para cada una se calcula:
Número total de violaciones
Número total de observaciones
Porcentaje de violaciones
Además, se incluye una validación adicional:
¿El porcentaje es menor a 2.5%?
Este umbral sirve como referencia para evaluar si el modelo está subestimando el riesgo.
Interpretación del porcentaje de violaciones
Bajo un modelo bien calibrado:
Para VaR al 95% → se espera ≈ 5% de violaciones
Para VaR al 99% → se espera ≈ 1% de violaciones
Si el porcentaje observado es mayor, el modelo está subestimando el riesgo.
 Si es menor, el modelo es demasiado conservador.
En el código se utiliza un umbral de 2.5% como criterio adicional de evaluación, lo cual permite identificar modelos que podrían no ajustarse adecuadamente a los datos.
Visualización 
El código genera una gráfica que muestra:
La serie de rendimientos diarios
Los días en los que ocurren violaciones
Las violaciones se representan mediante puntos:
Rojo → violaciones del VaR 95% paramétrico
Azul → violaciones del VaR 99% paramétrico
Esto permite visualizar de forma clara en qué momentos los rendimientos exceden los niveles de riesgo estimados.
Análisis de resultados
A partir de la gráfica, se pueden identificar periodos en los que se concentran las violaciones, lo cual suele coincidir con episodios de alta volatilidad en el mercado.
En particular, es común observar agrupaciones de violaciones durante eventos extremos, donde los modelos, especialmente los paramétricos, pueden no capturar completamente la magnitud de las caídas.
Asimismo, el análisis de la tabla permite comparar el desempeño de los distintos enfoques:
El VaR histórico suele presentar menos violaciones en periodos de alta volatilidad, ya que incorpora eventos extremos pasados.
El VaR paramétrico, al asumir normalidad, puede generar más violaciones en presencia de colas pesadas.
El ES/CVaR, al ser más conservador, generalmente presenta menos violaciones que el VaR.
En conjunto, este análisis permite evaluar la calidad de las medidas de riesgo y detectar posibles fallas en los supuestos del modelo.
Conclusión 
El análisis de violaciones es una herramienta fundamental para validar modelos de riesgo, ya que permite comparar las pérdidas reales con las estimaciones teóricas.
A través de este código, se observa cómo distintas metodologías (paramétrica e histórica) presentan comportamientos diferentes frente a eventos extremos. Mientras que el enfoque paramétrico ofrece mayor estabilidad, el enfoque histórico captura mejor las colas de la distribución.
Finalmente, el uso conjunto de estas métricas proporciona una visión más completa del riesgo, permitiendo identificar tanto la frecuencia como la severidad de las pérdidas extremas.
INCISO F)
## Descripción del Código
Este inciso detalla la metodología y el análisis de resultados para la estimación del Valor en Riesgo (VaR) de la acción Chubb Limited (CB). El enfoque principal utiliza un modelo paramétrico adaptativo basado en una ventana móvil de un año bursátil.
1. Preparación de la Serie de Tiempo
El código inicia estructurando los rendimientos en un DataFrame específico para el análisis de riesgo:
df_var = pd.DataFrame(index=returns.index)
df_var['Returns'] = returns
df_var = df_var.dropna()

Este paso asegura la integridad de los datos, donde la función .dropna() es crítica para asegurar que no existan valores nulos que interrumpan los cálculos estadísticos posteriores.
2. Cuantiles de la Distribución Normal
Se definen los niveles de confianza alpha al 95% y 99%. Utilizando la función norm.ppf, se calculan los cuantiles teóricos de una distribución normal estándar:
Para el 95%, mi cuantil q_0.05 es de aproximadamente -1.645.
Para el 99%, mi cuantil q_0.01 es de aproximadamente -2.326.
Estos valores indican qué tan profundo en la "cola izquierda" de la distribución de retornos estoy buscando mi pérdida máxima.
3. Estimación de Volatilidad Móvil
df_var["Sigma_252"] = df_var["Returns"].rolling(window=252).std().shift(1)

Tenemos una ventana de 252 días que corresponde aproximadamente a un año de datos bursátiles. Esto permite que el modelo capture la evolución temporal de la volatilidad, adaptándose a periodos de calma o crisis.
La función .shift(1) asegura que el riesgo estimado para el día t se calcule utilizando únicamente información disponible hasta el día t-1,evitando el sesgo de supervivencia o anticipación (look-ahead bias).
4. Cálculo del VaR Paramétrico
El VaR se obtiene aplicando la fórmula bajo el supuesto de normalidad:
VaR_alpha = q_alpha * sigma_t

Donde q_alpha es el cuantil correspondiente y sigma_t es la desviación estándar móvil, es decir el VaR_alpha es igual al cuantil por la volatilidad.
5. Periodo de Calentamiento y Backtesting
Se eliminan los primeros 252 días del DataFrame final (df_results). Esto se hace porque el algoritmo requiere una historia previa de un año para generar su primera estimación de riesgo válida. Finalmente, se comparan los retornos reales contra el VaR para identificar violaciones (días donde la pérdida superó el umbral estimado).
6. Visualización
Finalmente, creamos una gráfica donde se pueden observar los rendimientos de la acción de Chubb Limited en conjunto con las líneas del VaR.
Para que la interpretación sea clara, decidí graficar los rendimientos diarios en un color gris claro de fondo, lo que permite resaltar las dos medidas de riesgo que calculamos: la línea azul para el VaR al 95% y la línea roja para el VaR al 99%. Lo que se busca observar en esta imagen es cómo las líneas de riesgo reaccionan ante la volatilidad.
## Análisis de Resultados
Al ejecutar el código, podemos observar que la salida nos arroja dos componentes principales: un resumen estadístico de eficiencia y una gráfica comparativa. 
Lo primero que analizo es el conteo de violaciones. Una violación ocurre cuando la pérdida real del día es mayor a lo que el modelo del VaR predijo. Según los datos obtenidos de los 3,854 días analizados:
- En el nivel de confianza del 95%, el código esperaba unas 193 violaciones, pero en la realidad ocurrieron 166. Esto me da un porcentaje real del 4.31%. Como este número es menor al 5% permitido, puedo decir que mi modelo es eficiente y ligeramente conservador, funcionando muy bien para situaciones normales de mercado.
- En el nivel de confianza del 99%, aquí es donde la situación cambia. el código esperaba solo 39 violaciones, pero ocurrieron 68, lo que nos da un 1.76%. Al ser casi el doble de lo esperado, esto me confirma que los rendimientos de esta acción tienen "colas pesadas"; es decir, ocurren eventos extremos con más frecuencia de lo que una distribución normal puede predecir.
Por otro lado, al observar la gráfica se ve claramente cómo las líneas de VaR (azul y roja) caen drásticamente durante el inicio de la pandemia. Esto me confirma que mi modelo de ventana móvil es efectivo, ya que fue capaz de detectar el pico de volatilidad en el sector asegurador y ajustar el nivel de riesgo en tiempo real.
La línea azul (95%) se mantiene más cerca de los rendimientos diarios, siendo una medida de riesgo para la operación común. En cambio, la línea roja (99%) se ubica mucho más abajo, actuando como una red de seguridad para eventos de crisis.
Noto que Chubb Limited, al ser una empresa de seguros, tiene periodos de mucha estabilidad, pero cuando hay crisis sistémicas, los rendimientos caen de forma agresiva, lo que explica por qué el VaR al 99% registró más violaciones de las esperadas.
En conclusión, considero que el enfoque paramétrico con ventana móvil es una herramienta sumamente útil por su estabilidad, ya que me permitió observar de manera clara cómo evoluciona el riesgo a largo plazo. Al ser un modelo menos volátil, facilita la toma de decisiones sin reaccionar de forma exagerada al ruido diario del mercado.
Sin embargo, los resultados me demostraron que para niveles de confianza extremos como el 99%, el modelo puede quedarse corto. Por lo tanto, mi recomendación sería complementar este estudio con un enfoque de Expected Shortfall (ES). De esta manera, no sólo sabríamos que se ha superado un límite de pérdida, sino que podríamos capturar con mayor precisión la severidad real de esas pérdidas en las colas de la distribución.
