# Actividad 2. Construcción de un sistema RAG para búsqueda semántica de documentos

Objetivos:
Comprender el funcionamiento básico de un sistema Retrieval-Augmented Generation (RAG).
Preparar documentos de texto para su utilización como fuente de conocimiento.
Dividir documentos en fragmentos (chunks).
Generar embeddings utilizando un modelo de lenguaje accesible mediante OpenRouter.
Almacenar embeddings y contenido en PostgreSQL utilizando pgvector.
Realizar búsquedas mediante similitud semántica.
Integrar el motor de búsqueda semántica en una aplicación web sencilla mediante FastAPI.
Comprender la diferencia entre recuperar información y generar una respuesta con un LLM.
Familiarizarse, de forma opcional, con LlamaIndex como biblioteca especializada en sistemas de RAG.

Aspectos básicos / Escenario
En la actividad anterior se construyó un pequeño chat capaz de comunicarse con un modelo de lenguaje. En esta ocasión se pretende resolver una limitación habitual de los LLM: no disponen necesariamente de la información específica que queremos consultar.

Se proporcionará una aplicación web básica ya preparada. El alumno deberá completar las partes marcadas con # TODO para construir un pequeño sistema RAG capaz de ingerir documentos de texto, convertir sus fragmentos en representaciones vectoriales y almacenarlos en PostgreSQL + pgvector. Posteriormente, la aplicación permitirá introducir una consulta y recuperar los fragmentos de documentos cuyo significado sea más próximo a la consulta.

La interfaz web, incluyendo HTML, CSS y JavaScript, se proporciona ya preparada. El objetivo de la actividad no es aprender desarrollo web, sino trabajar sobre el procesamiento semántico de documentos y comprender las diferentes etapas que intervienen en un sistema RAG.

Recursos necesarios
Ordenador con Python 3.11 o superior.
Terminal y editor de código o IDE.
Docker y Docker Compose.
Cuenta de OpenRouter proporcionada para el curso.
Clave API de OpenRouter.
Repositorio o carpeta inicial proporcionada por el docente.
Documentos de texto en formato .txt para realizar las pruebas.
PostgreSQL con extensión pgvector, proporcionado mediante el entorno preparado para la actividad.
Los ficheros Python contienen comentarios # TODO que indican los puntos en los que debe intervenir el alumno. El fichero schema.sql contiene el esquema inicial de la base de datos.

Parte 1: Preparar el entorno
En esta primera parte se pondrá en funcionamiento la aplicación proporcionada y se preparará la base de datos.

Paso 1.1: Crear el entorno virtual
Crear un entorno virtual mediante venv dentro del proyecto:

python -m venv .venv
Activarlo y comprobar que se está utilizando el intérprete del entorno virtual.

Paso 1.2: Instalar las dependencias
Instalar las dependencias indicadas en requirements.txt:

pip install -r requirements.txt
Revisar las librerías utilizadas en el proyecto e identificar cuáles están relacionadas con:

FastAPI.
PostgreSQL.
pgvector.
Peticiones HTTP.
Configuración mediante variables de entorno.
Paso 1.3: Configurar las variables de entorno
Crear el fichero .env a partir de .env.example.

Configurar los valores necesarios para:

La conexión con PostgreSQL.
La clave API de OpenRouter.
El modelo de embeddings que se utilizará.
No modificar .env.example para almacenar las credenciales personales.

Paso 1.4: Preparar la base de datos
Poner en funcionamiento el servicio PostgreSQL proporcionado para la actividad.

Revisar schema.sql para identificar las tablas y campos que utilizará el sistema RAG.

Comprobar especialmente cómo se almacena el vector asociado a cada fragmento de documento.

Utilizar este esquema para crear las tablas necesarias en la base de datos antes de proceder con la ingesta de documentos, mediante la ejecución de schema.sql en PostgreSQL sobre una base de datos previamente creada.

Parte 2: Construir el motor de ingesta
En esta parte se completará ingest.py para transformar los documentos de texto de la carpeta documents/ en información que pueda ser consultada mediante búsqueda semántica.

Paso 2.1: Leer los documentos
Completar el # TODO correspondiente a la lectura de documentos.

El programa deberá localizar los ficheros .txt existentes en la carpeta documents/ dentro del proyecto y obtener su contenido. Para cada documento será necesario conservar, al menos, información que permita identificar su procedencia.

Paso 2.2: Dividir los documentos en chunks
Completar en rag.py la función encargada de dividir un documento en fragmentos.

Experimentar con un tamaño de fragmento razonable y observar qué ocurre cuando:

Los fragmentos son demasiado grandes.
Los fragmentos son demasiado pequeños.
El objetivo es conseguir unidades suficientemente pequeñas para realizar búsquedas precisas, pero que conserven el contexto necesario para resultar útiles.

Paso 2.3: Generar los embeddings
Para cada fragmento se deberá generar un embedding mediante una llamada a un modelo disponible a través de OpenRouter.

Completar la función correspondiente en rag.py.

El resultado será un vector numérico que representa semánticamente el contenido del fragmento.

Comprobar que:

Se realiza una llamada al modelo.
Se obtiene un vector.
El vector puede asociarse al fragmento correspondiente.
Paso 2.4: Almacenar los fragmentos
Completar la función encargada de almacenar los chunks en PostgreSQL.

Cada registro deberá conservar la información necesaria para realizar posteriormente una búsqueda, incluyendo:

El contenido del fragmento.
La información del documento de procedencia.
Los metadatos disponibles.
El embedding generado.
Comprobar en PostgreSQL que los documentos han sido realmente incorporados.

Parte 3: Construir la búsqueda semántica
Una vez realizada la ingesta, se implementará la segunda parte fundamental del sistema RAG: recuperar los fragmentos más relacionados con una consulta.

Paso 3.1: Generar el embedding de una consulta
Completar en rag.py la funcionalidad necesaria para transformar una pregunta del usuario en un embedding utilizando el mismo modelo empleado durante la ingesta.

Por ejemplo, una consulta como:

¿Qué medidas de seguridad recomienda el documento del proveedor X sobre el producto Y?

deberá convertirse en un vector que pueda compararse con los vectores almacenados en la base de datos.

Paso 3.2: Realizar la búsqueda en pgvector
Completar la función de búsqueda semántica.

La consulta deberá:

Recibir una pregunta.
Generar su embedding.
Compararlo con los embeddings almacenados.
Recuperar los fragmentos más similares.
Ordenarlos según su similitud.
Devolver los resultados.
Probar diferentes valores para el número de resultados recuperados.

Paso 3.3: Comprobar la calidad de la recuperación
Realizar diferentes preguntas relacionadas con los documentos disponibles.

Comprobar si los fragmentos recuperados contienen realmente información relevante.

Realizar también preguntas sobre información que no aparece en los documentos y observar el resultado.

Parte 4: Integrar el buscador en la aplicación web
En esta parte se utilizará FastAPI para conectar el motor RAG con la interfaz web proporcionada.

Paso 4.1: Revisar la aplicación
Examinar main.py e identificar:

La creación de la aplicación FastAPI.
Las rutas ya definidas.
La plantilla HTML.
Los recursos estáticos.
No es necesario modificar el HTML, CSS ni JavaScript proporcionados.

Paso 4.2: Conectar la búsqueda semántica
Completar los # TODO correspondientes de main.py para que la aplicación reciba una consulta y utilice las funciones de rag.py.

La ruta de búsqueda deberá:

Recibir la consulta.
Ejecutar la búsqueda semántica.
Obtener los fragmentos relevantes.
Devolverlos en el formato esperado por la interfaz.
Paso 4.3: Probar la aplicación
Arrancar FastAPI mediante uvicorn siguiendo las instrucciones del README.

Abrir la aplicación desde el navegador y realizar diferentes consultas.

Comprobar que los resultados mostrados corresponden a los documentos previamente ingeridos.

Parte 5: Construir el RAG completo
Hasta este momento la aplicación permite recuperar información, pero todavía no está utilizando necesariamente el LLM para generar una respuesta.

Paso 5.1: Incorporar el contexto recuperado
Modificar el flujo de búsqueda para utilizar los fragmentos recuperados como contexto para una nueva petición al LLM.

El flujo completo será:

Recuperar la pregunta
Obtener embedding de la pregunta, llamando a la API de OpenRouter
Búsqueda semántica en PostgreSQL con pgvector
Seleccionar fragmentos relevantes
Construir el contexto a partir de los fragmentos relevantes
Consultar al LLM
Devolver la respuesta
Paso 5.2: Comparar búsqueda y generación
Comparar:

Los fragmentos recuperados por pgvector.
La respuesta final generada por el LLM.
Comprobar si la respuesta está realmente respaldada por los fragmentos recuperados.

Paso 5.3: Probar preguntas sin respuesta
Realizar preguntas cuya respuesta no se encuentre en los documentos.

Observar si el sistema:

Reconoce que no dispone de información suficiente.
Intenta responder utilizando conocimiento general del modelo.
Genera una respuesta aparentemente correcta pero que no procede de los documentos.
Este comportamiento servirá como introducción al problema de las alucinaciones y la fiabilidad de los sistemas basados en LLM.

Ampliación 1: LlamaIndex
Como ampliación, investigar cómo podría realizarse el proceso de ingesta y recuperación utilizando LlamaIndex.

Instalar la biblioteca y localizar las abstracciones que proporciona para:

Cargar documentos.
Dividirlos.
Generar embeddings.
Crear un índice.
Realizar consultas.
Comparar la solución implementada manualmente en rag.py con la solución proporcionada por LlamaIndex.

La finalidad de esta ampliación no es sustituir el trabajo realizado, sino comprender qué partes del proceso RAG estamos delegando en una biblioteca especializada.

Ampliación 2: Mejorar el proceso de ingesta
Modificar ingest.py para proporcionar información sobre el progreso de la ingesta. Por ejemplo, mostrar en la terminal información de los documentos y chunks a medida que se van procesando.

Como ampliación adicional, estudiar cómo modificar el sistema para admitir otros formatos de documentos, como:

PDF.
DOCX.
ODT.
Otros formatos que permitan extraer texto.
Conservar, cuando sea posible, los metadatos asociados al documento (nombre, título, autor, fecha, tipo de documento, etc.) y utilizarlos posteriormente en los resultados de búsqueda.

Reflexión / Conclusiones
¿Qué diferencia existe entre una búsqueda tradicional por palabras y una búsqueda semántica?
¿Qué representa un embedding?
¿Por qué necesitamos utilizar el mismo modelo de embeddings para los documentos y para las consultas?
¿Qué influencia tiene el tamaño de los chunks sobre los resultados?
¿Qué ocurre cuando recuperamos demasiados o demasiado pocos fragmentos?
¿Qué diferencia existe entre la fase de retrieval y la fase de generation?
¿Qué problemas pueden aparecer cuando la información necesaria no se encuentra en los documentos?
¿Qué información adicional aportan los metadatos de los documentos?
¿Qué funcionalidades de LlamaIndex podrían ahorrarnos trabajo respecto a nuestra implementación?
Pensando en vuestro entorno profesional, ¿qué conjunto de documentos podría convertirse en una base de conocimiento mediante un sistema RAG?
