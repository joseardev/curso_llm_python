# Actividad 1. Construcción de un chat con un LLM mediante Python

## Objetivos:

- Configurar un entorno virtual de Python para trabajar con modelos de lenguaje.
- Acceder a un LLM mediante una API desde Python.
- Comprender la estructura básica de una petición a un modelo de lenguaje.
- Utilizar `requests` para realizar peticiones HTTP a OpenRouter.
- Representar los mensajes de una conversación mediante `dataclass`.
- Construir un pequeño chat interactivo en la terminal.
- Mantener el contexto de una conversación mediante un historial de mensajes.
- Experimentar con diferentes instrucciones y modelos de lenguaje.

## Aspectos básicos / Escenario

En esta actividad se construirá desde cero un pequeño **chat en Python capaz de comunicarse con un modelo de lenguaje** a través de OpenRouter. El programa funcionará desde la terminal: el usuario introducirá mensajes y el modelo generará las respuestas correspondientes.

Se utilizará inicialmente la librería `requests`, sin utilizar todavía frameworks específicos para agentes. El objetivo es comprender qué ocurre en una comunicación con un LLM y construir una primera aplicación funcional sobre la que posteriormente se podrán incorporar nuevas capacidades. Esta aproximación constituye la base para el desarrollo posterior de agentes capaces de trabajar con información y herramientas externas.

## Recursos necesarios

- Ordenador con Python 3.11 o superior.
- Terminal.
- Editor de código o IDE.
- Cuenta de OpenRouter proporcionada para el curso.
- Clave API de OpenRouter.
- Conexión a Internet.
- Repositorio o carpeta inicial proporcionada por el docente.

# Parte 1: Preparar el entorno de trabajo

Crear un pequeño proyecto Python para la actividad y preparar un entorno virtual independiente.

### Paso 1.1: Crear el proyecto

Crear una carpeta para la actividad, por ejemplo:

```text
actividad-1/
```

Dentro de ella se utilizará inicialmente la siguiente estructura:

```text
actividad-1/
├── .env
├── .gitignore
├── requirements.txt
└── main.py
```

El fichero `main.py` contendrá todo el código Python de la actividad. Se mantendrá deliberadamente una estructura sencilla para poder concentrarse en el funcionamiento del agente.

### Paso 1.2: Crear el entorno virtual

Desde la terminal, situarse en la carpeta del proyecto y crear un entorno virtual utilizando `venv`:

```bash
python -m venv .venv
```

Activar el entorno virtual.

En Linux/macOS:

```bash
source .venv/bin/activate
```

En Windows:

```powershell
.venv\Scripts\activate
```

Comprobar que el intérprete utilizado pertenece al entorno virtual.

### Paso 1.3: Instalar las dependencias

Para este proyecto únicamente se necesitan las siguientes dependencias:

* requests
* python-dotenv

Se pueden instalar manualmente en el entorno virtual o mediante el fichero `requirements.txt` que ya contiene las dependencias necesarias. Se recomienda hacerlo de este último modo para asegurar que todas las dependencias se instalen de manera consistente. Se procedería con la siguiente orden:

```bash
pip install -r requirements.txt
```

Comprobar que el programa puede importar correctamente ambas librerías.

# Parte 2: Configurar el acceso a OpenRouter

Antes de realizar la primera petición, preparar las credenciales necesarias para acceder a la API.

### Paso 2.1: Configurar la clave API

Crear un fichero `.env` en la raíz del proyecto y almacenar en él la clave proporcionada para el curso:

```text
OPENROUTER_API_KEY=...
```

La clave **no debe escribirse directamente en `main.py`**.

### Paso 2.2: Cargar la configuración desde Python

La configuración del programa depende de las variables de entorno definidas en el fichero `.env`. Si se utiliza Visual Studio Code como entorno de desarrollo, se recomienda instalar la extensión "Python" y asegurarse de que el intérprete seleccionado corresponde al entorno virtual creado y que tiene activada la opción de cargar las variables de entorno desde el fichero `.env`.

(Otra opción es instalar e importar `load_dotenv` desde `main.py` para cargar las variables de entorno.)

Utilizar `os.getenv()` para obtener el valor de `OPENROUTER_API_KEY`.

Comprobar que la aplicación obtiene correctamente la clave.

### Paso 2.3: Proteger las credenciales

Si se va a utilizar un control de versiones Git, es importante asegurarse de que las credenciales no se incluyan en el repositorio. Para ello, es necesario crear un fichero denominado `.gitignore` que contenga, como mínimo:

```text
.env
.venv/
__pycache__/
```

Reflexionar sobre por qué las credenciales no deberían formar parte del código fuente ni incorporarse a un repositorio.

# Parte 3: Realizar la primera llamada al LLM

En esta parte se realizará una petición HTTP directamente desde Python utilizando `requests`.

### Paso 3.1: Preparar los mensajes

Crear una estructura `Message` utilizando `dataclass` para representar los mensajes de la conversación.

Como mínimo, cada mensaje deberá contener:

- `role`: papel que desempeña el mensaje.
- `content`: contenido textual del mensaje.

Por ejemplo, los roles utilizados en una conversación serán:


- `system`: instrucciones o contexto del sistema.
- `user`: mensaje del usuario.
- `assistant`: respuesta generada por el modelo.


Crear inicialmente una lista de mensajes que contenga una instrucción de sistema y una pregunta del usuario.

### Paso 3.2: Preparar la petición HTTP

Utilizar `requests.post()` para realizar una petición al endpoint de chat de OpenRouter.

La petición deberá incluir:

- La URL del endpoint.
- La clave API mediante la cabecera `Authorization`, con el valor `Bearer <API_KEY>`, donde `<API_KEY>` es la clave obtenida de acceso a OpenRouter que debe generarse desde el panel de control de OpenRouter.
- La cabecera `Content-Type`, con el valor `application/json`.
- El modelo que se desea utilizar, por ejemplo `gpt-4o-mini`.
- Los mensajes de la conversación: una lista de objetos `Message` que representen cada mensaje de la conversación.

El cuerpo de la petición deberá enviarse en formato JSON.

**Pista:** consultar la documentación de la API proporcionada por el docente para comprobar el endpoint, los nombres de los campos y el formato esperado.

### Paso 3.3: Procesar la respuesta


Identificar dentro del JSON:

- La respuesta generada por el modelo.
- La información relacionada con el uso de tokens, si está disponible.
- Otros datos que puedan resultar relevantes.

La información relevante se encuentra dentro del JSON devuelto por la API, que presenta una estructura anidada con diferentes campos, entre los que se incluyen la respuesta generada por el modelo y los datos de uso de tokens:

```json
{
  "id": "gen-1791137533-xxxxx...",
  "object": "chat.completion",
  "created": 1791137533,
  "model": "openai/gpt-5.4-mini",
  ...
  "choices": [
    {
      ...
      "message": {
        "role": "assistant",
        "content": "(AQUI VA EL TEXTO GENERADO POR EL MODELO)",
        ...
      }
    }
  ],
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 165,
    "total_tokens": 178,
    "cost": 0.00075225,
    ...
  }
}
```

Interesa obtener únicamente el texto generado por el modelo, sin necesidad de mostrar toda la estructura del JSON. Esto se puede lograr accediendo al campo `content` dentro del objeto `message` del primer elemento del array `choices`.

Puede ser útil mostrar temporalmente por pantalla la respuesta completa recibida para observar su estructura. Luego, ha de modificarse el programa para que muestre únicamente el texto generado por el modelo.

### Paso 3.4: Probar diferentes preguntas

Modificar la pregunta enviada al modelo y realizar varias llamadas.

Probar preguntas de diferentes tipos y observar si el comportamiento del modelo es el esperado.

# Parte 4: Construir un chat interactivo

La llamada realizada anteriormente es puntual. Ahora se convertirá el programa en un pequeño chat que permita mantener una conversación.

### Paso 4.1: Crear el bucle principal

Implementar en `main.py` un bucle que:

1. Muestre un indicador para solicitar una entrada al usuario.
2. Lea el mensaje introducido mediante `input()`.
3. Envíe el mensaje al modelo.
4. Muestre la respuesta.
5. Vuelva a solicitar una nueva entrada.

Utilizar una orden como `exit` o `quit` para finalizar el programa.

El resultado esperado será similar a:

```text
Chat IA
Escribe 'exit' para terminar.

Tú: Hola
IA: ¡Hola! ¿En qué puedo ayudarte?

Tú: ...
IA: ...
```

No es necesario implementar ninguna interfaz gráfica ni características avanzadas.

### Paso 4.2: Mantener el historial

Modificar el programa para conservar los mensajes de la conversación en una lista.

Cada vez que el usuario escriba un mensaje:

1. Crear un `Message` con `role="user"`.
2. Añadirlo al historial.
3. Enviar el historial completo al modelo.
4. Recibir la respuesta.
5. Crear un `Message` con `role="assistant"`.
6. Añadirlo también al historial.

De esta manera, cada nueva petición incluirá el contexto de la conversación anterior.

### Paso 4.3: Comprobar el contexto

Mantener una conversación en la que la segunda pregunta dependa de la primera.

Por ejemplo:

```text
Tú: Estoy aprendiendo Python y quiero practicar listas.
IA: ...

Tú: Ponme un ejercicio sobre ellas.
IA: ...
```

Comprobar que el modelo puede interpretar correctamente la segunda pregunta gracias al historial.

# Parte 5: Experimentar con el comportamiento del modelo

Una vez construido el chat básico, realizar diferentes experimentos para observar cómo afectan las instrucciones y la configuración al resultado.

### Paso 5.1: Modificar el mensaje de sistema

Modificar el mensaje `system` para convertir el chat en un asistente especializado.

Por ejemplo:

- Asistente de programación Python.
- Asistente de soporte técnico.
- Asistente para documentación.
- Asistente para redactar textos profesionales.

Realizar las mismas preguntas con diferentes instrucciones y comparar las respuestas.

### Paso 5.2: Cambiar el modelo

Probar, cuando sea posible, diferentes modelos disponibles en OpenRouter.

Comparar de forma cualitativa:

- Calidad de las respuestas.
- Velocidad de respuesta.
- Longitud de las respuestas.
- Consumo de tokens.
- Coste de las llamadas.

No se pretende realizar una comparación exhaustiva de modelos, sino observar que **el modelo utilizado es también una decisión de diseño de la aplicación**.

### Paso 5.3: Observar el consumo

Realizar una conversación relativamente larga y observar cómo evoluciona el consumo de tokens.

Reflexionar sobre qué ocurre cuando enviamos cada vez más historial al modelo.

# Reflexión / Conclusiones

- ¿Qué información necesita una aplicación Python para realizar una llamada a un LLM?
- ¿Qué papel desempeñan los mensajes `system`, `user` y `assistant`?
- ¿Por qué tenemos que enviar el historial de la conversación para mantener el contexto?
- ¿Qué ventajas aporta utilizar un `dataclass` para representar los mensajes?
- ¿Qué riesgos implica almacenar directamente una API key en el código?
- ¿Qué diferencias has observado entre los distintos modelos probados?
- ¿Qué relación existe entre la cantidad de contexto enviado y el consumo de tokens?
- ¿Qué ocurre si eliminamos el historial antes de realizar una nueva pregunta?
- Pensando en tu actividad profesional o cotidiana, ¿qué tarea podría resolverse mediante un chat como el que acabas de construir?

### Ampliación opcional

Modificar el programa para incorporar alguna de las siguientes funcionalidades:

- Permitir borrar el historial y comenzar una nueva conversación sin cerrar el programa.
- Permitir seleccionar el modelo al iniciar el chat.
- Mostrar información básica sobre el consumo de tokens de cada petición.
- Añadir una opción para guardar una conversación en un fichero.

Como paso posterior, se podrá reproducir el mismo ejercicio utilizando **LangChain** y comparar la implementación directa mediante `requests` con la abstracción proporcionada por el framework.

## Ejemplo con memoria en PostgreSQL

`clase_2/tools_memoria_postgres.py` reproduce el agente de
`clase_2/tools_memoria_corto_plazo.py`
con las mismas herramientas de clima y fecha, usando `PostgresSaver`.

1. Instala las dependencias en el entorno virtual:

   ```powershell
   python -m pip install -r requirements.txt
   ```

2. Prepara una base de datos PostgreSQL existente y añade su conexión a `.env`,
   junto con `OPENROUTER_API_KEY` y `OPENROUTER_MODEL`:

   ```text
   POSTGRES_URI=postgresql://usuario:password@localhost:5432/chat_memoria
   ```

   Sustituye los valores por los de tu servidor. El usuario necesita permisos
   para crear las tablas del checkpointer; el script ejecuta `setup()` al arrancar.

3. Inicia una conversación:

   ```powershell
   python -m clase_2.tools_memoria_postgres --thread-id conversacion-1
   ```

Escribe `exit` o `quit` para salir. Ejecuta el mismo comando para recuperar el
historial después de reiniciar. Usa otro `--thread-id` para empezar una conversación
distinta. Si omites el argumento, se reutiliza la conversación `clima-demo`.

PostgreSQL conserva los puntos de control, pero no recorta ni resume el historial:
el contexto enviado al modelo sigue creciendo con cada turno.

El script muestra las etapas de arranque y limita la espera de conexión a
5 segundos por destino. Si falla, comprueba que PostgreSQL esté arrancado y que
el host, puerto, credenciales y base de datos de `POSTGRES_URI` sean correctos.

Implementación basada en la [documentación de memoria de LangChain](https://docs.langchain.com/oss/python/langchain/short-term-memory).
