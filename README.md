## README MÉTODOS
Para el análisis de este proyecto nos centraremos en la compañía Chubb a pesar de haber colocado otras dos empresas

INCISO A)
INCISO B)
# INCISO C)

# INCISO D)
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


Definición como esperanza condicional

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


Supuesto de normalidad

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



Fórmula cerrada del ES paramétrico

Bajo el supuesto de normalidad, la expresión integral del ES puede resolverse analíticamente, obteniendo:

ES_alpha = mu - sigma * (phi(z_alpha) / (1 - alpha))

donde:

- phi(z_alpha) es la densidad de la normal estándar evaluada en z_alpha  
- 1 - alpha es la probabilidad de la cola  

En el código, esto se implementa como:

media_movil - desviacion_movil * (norm.pdf(z_alpha) / (1 - alpha))

Esto evita calcular la integral directamente y utiliza el resultado analítico.


## ES histórico

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


INCISIO E)
INCISO F)

