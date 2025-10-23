# PLAN DE TESTING
* covertura de codigo > 80% en back-end
* covertura unitaria front-end
* por el momento pruebas manuales de integracion 
>(si se puede definir flujos en cypress)

---
## pruebas para la aplicacion finalizada:
- probar el magicLink.
- cargar el cv en formato pdf --> testiar las excepciones
- hacer lo mismo con cv de linkedin --> testiar excepciones
- probar la accion de github --> saltear esta opcion

##### admin:
- cargar csv 
> testiar excepciones 
- probar cada links del footer
- probar las opciones del menu desplegable
- ingresar a la seccion dashboard
- probar el filtro de tecnologias
    - ingresar nombre de la tecnologia deseada
    - seleccionar de los tags sugeridos
    - finalizar proceso de filtrado por tecnologia
    - checkear resultados
- probar el filtro de idioma
    - ingresar nivel requerido
    - seleccionar de las tags sugeridas
    - finalizar proceso de filtrado por idioma
    - checkear resultados
- probar el another filtro
    - ingresar habilidad blandas???
    - seleccionar de las tags sugeridas
    - finalizar proceso de filtrado
    - checkear resultados
- probar filtro last update
    - finalizar proceso de filtrado
    - checkear resultados
- probar el filtro por feedback??? (alumnis con feedback)   
    - ingresar nombre de docente???
    - seleccionar tag sugerido???
    - finalizar proceso de filtrado por feddback
    - checkear resultados
- seleccionar multiples tags para filtrar
    - seleccionar tecnologias -> elegir tags
    - seleccionar idioma -> elegir tag
    - seleccionar another filtro -> elegir tags
    - finalizar proceso de filtrado grupal
    - checkear resultados
    - probar diferentes convinaciones y repetir proceso
- probar las cards
    - click en una card
    - click en logo linkedin -> checkear resultado
    - click en logo (mensaje, contacto) -> checkear resultado
    - click en logo github -> checkear resultado
    - probar todas las posibles rutar para abortar accion
    - probar que hacen los ... de la esquina superior derecha
    - probar etiquetas (tutor anotation)
    - probar etiqueta (own anotation)
- probar seccion de feedback
    - ingresar un feedback y guardarlo -> manager
    - seleccionar campo de calificacion -> tutors


----------------------------------- BACK END -----------------------------------------------
### para ejecutar los test en el back-end:
> es necesario descargar -> pytest, pytest-cov
>>comando para ejecutar `pytest`\
comando para tener mas informacion y data de cobertura `pytest --cov=.`

### progreso hasta ahora:
- **test_invitation_and_bmodel**
>En este archivo se testio la creacion exitosa de una instancia de Invitation, simulando (mocks) las dependencias que utiliza (secrets, uuid, datatime). tambien se testea la clase base (bmodel.py), creando una clase que hereda de la misma para podes hacerle pruebas al constructor de Bmodel y tambien se testean los casos exitosos y las excepciones posibles de las funciones.

    -     Se verifico la exitosa creacion comparando la igualdad de los valores ingresados (y simulados)
          con los valores que guardo la instancia creada.
          Tambien se testio y verifico el estado del token y del log, se verificaron las
          excepciones TypeError de log y token state.
          En la mismo prueba se testio la respuesta de to_dict() verificando que devuelve un dict, que contiene
          los misma cantidad campos, se verifica que siertas claves requeridas estan dentro de la respuesta y
          que alguna clave contiene el mismo valor que fue ingresado en la creacion de la instancia

    -     se testio las posibles excepciones dentro de cada campo forzandolas con datos o acciones invalidas.
          TypeError en full_name y en cohort
          ValueError en full_name, cohort y email

    -     se testio las dos posibles respuesta de la funcion interna is_valid() que se
          encarga de validar el estado del token```

    -     se testiaron las posibles excepciones de el campo expires_at verificando la respuesta exitosa
          con una fecha invalida y con una fecha anterior a la creacion de la instancia.

    -     test_bmodel_constructor_with_data_from_db, aca es donde probamos el
          constructor de Bmodel utilizando la simulacion para aislar la prueba,
          se verifica que la data coincide con lo declarado y que los atributos
          de tiempo son del tipo datatime

    -     test_bmodel_updated_at_setter, verificamos el recorrido exitoso del setter,
          luego de crear la instancia modificamos la data y vemos que coincide.
          (arreglar esta funcion, caso exitoso con str)

    -     test_validate_uuid, validamos el funcionamiento de dicha funcion, 
          hacemos el test exitoso utilizando una id valida, y luego se hacen saltar
          dos excepciones (ValueError) por una id que no es valida y por una id
          que no es un string, en ambos casos se verifica el mensaje mostrado

    -     test_validate_number, aca verificamos las excepciones de la funcion y
          los mensajes que devuelven, ingresando un valor de cohorte negativo y
          y booleano (este ultimo para validar la intencion de back-end)

- **test_csv_invitation**
>simulando las dependencias que el archivo csv_invitation necesita se testio cada funcion interna y por ultimo una prueba de integracion en la cual recorremos todo el proceso
>>se necesita instalar pytest-asyncio para que funcione

    -     la validacion del csv, creando una prueba exitosa y verificando que el tipo de dato de la respuesta
          es una lista, se comprobo que contiene la misma cantidad de objetos que ingresamos en el csv
          y verificando que dentro de cada objeto existan las claves requeridas.
          tambien se testiaron exitosamente las posibles excepciones que puede generar la funcion 
          (MissibgColumnsException, InvalidCSVException)

    -     la generacion de invitaciones (simulando una exitosa respuesta de la previa funcion) se 
          testio que la funcion devuelve una lista con la misma cantidad de objetos ingresados 
          en la ficticia respuesta exitosa.
          se verifico que la cantidad de veces que se llamo al mock (simulacion) de Invitation es igual a la
          cantidad de objetos y se comprobo que las llamadas fueron echas con los mismo valores que utilizamos
          en la ficticia respuesta exitosa.

    -     envio de invitaciones, simulando FRE (Ficticia Respuesta Exitosa) de la anterior funcion se testio
          que la cantidad de veces que fue llamado el servicio de email para mandar las invitaciones es igual
          a la cantidad de objetos en la FRE, ademas se verifico la concordancia entre los valores esperados
          (y los valores que la funcion utilizo para llamar al mock (simulacion) de el servicio de email.) NO SE TESTEA
          se verifica que la funcion al fallar llama correctamente al logger

    -     test_save_invitations_handles_exceptions, se testio la funcion 
          que guarda las invitaciones, se verifica que la funcion llama a 
          invitation_repo la misma cantidad que invitaciones y se verifica 
          el correcto llamado a logger con los mensajes esperados

    -     process_csv se hizo una prueba de integracion aislada (con mocks) del recorrido de la data por todo
          el archivo, se simulo (mock) un csv y fuimos verificando las distintas llamadas que hace la funcion,
          con el mock de invitacion verificamos cuantas veces fue llamado para instanciar y verificamos que
          hubo igualdad con los datos de nuestro csv(mock) en una de las llamadas.
          con el mock del servicio de email verificamos que fue llamado la misma cantidad de veces como
          instancias teniamos e igual a la cantidad de objetos en el csv, tambien verificamos que una
          de las llamadas contiene los valores esperados segun nuestra data en el csv.
          ademas verificamos que el servicio de invitation_repo fue llamado 
          dos veces

- **test_base_repository**
>para ejecutar exitosamente este archivo de test es necesario instalar `pytest-asyncio`
>>NO(en este archivo se simula (mocks) el modelo y la coleccion para poder generar una instancia del repo con mocks)NO, se intercepta la funcion RealObjectId para forzarla a retornar objetos ficticios que eluden las excepciones y tambien se creo un mock para simular el comportamiento de `__aiter__`

    -     primero se valido la funcionalidad de to_dict() la cual se encarga de convertir la clave del id
          a la forma esperada por nuestra base de datos. se verifica que la clave _id contiene el id 
          utilizado, que la clave id no esta en la respuesta (doc) y que el nombre coincide

    -     se valida la creacion de una entidad, se configuran los datos del objeto y la respuesta del metodo.
          se verifica que el metodo fue llamado una vez y que la respuesta coincide con el 
          inserted_id esperado

    -     find_by_id, se configura el mock, la respuesta del metodo y se llama a este, verificamos que
          el metodo fue llamado una vez y que la data llego completa.
          tambien se testio la posible respuesta none para terminar de cubrir el archivo.

    -     find_all, se crea una lista con datos validos y aca se utiliza el mock que simula a
          asynchronous iterator para generar una respuesta valida del metodo.
          se llama al metodo y se verifica que fue llamado una sola vez, que fue llamado con un diccionario 
          vacio, que la respuesta es una lista, que el largo de esa lista es de la misma cantidad de objetos
          y que la data coincide.

    -     find_all_with_filters, mismos pasos que en el test anterior pero esta vez se llama al metodo
          con un diccionario que contiene dos filtros, se verifica que fue llamado una vez, que fue llamado con x filtros, que el largo de la lista coincide con los filtros y que la data coincide

    -     update, se simula una id valida y se crea un objeto simulado que contiene el atributo a testiar,
          se simula la respuesta esperada y se llama al metodo.
          se verifica que el metodo fue llamado una vez, que la llamada se solicito con los atributos y
          la forma esperada (incluyendo las claves requeridas), que la respuesta fue un booleano y fue True

    -     update_not_modified, misma logica que en test previo, solo que ahora definimos el atributo a      
          testiar en false para simular un objeto que no fue encontrado.
          se realizan la mayoria de verificaciones anteriores y la verificacion de false en la respuesta

    -     update_failure, se fuerza a levantar una excepcion utilizando un id que no es valido.
          se verifica la correcta conexion del metodo con las excepciones de la libreria involucrada

    -     delete, la respuesta es la misma que update asi que se aplica la misma logica, se simula un id
          valido, se crea un objeto simulado con el atributo que nesecitamos y se llama al metodo.
          se verifica que el metodo fue llamado una vez y que la llamada se realizo de la forma esperada,
          ademas de verificar que la respuesta es un booleano y es true

    -     not object_to_delete, misma logica pero se simula que no se encontro al objeto, se verifica que
          el metodo fue llamado una vez, de la forma esperada y que la respuesta fue un booleano en false

    -     test_exists_true, test_exists_false, test_exists_exception, estos
          test cubren la funcion exists, la cual verifica que el documento
          exita, se con simulaciones se testea que el documento existe,
          un documento inexistente y se verifica una excepcion.

    -     test_count_with_filters, test_count_without_filters. con estos
          test cubrimos la funcion count con filtros y sin filtros, la cual 
          cuenta documentos. se verifica que la funcion hizo la llamada con
          los atributos esperados en el primer caso y verificando la
          coincidencia de documentos recibidos 

- **test_routes**
>este archivo contiene test para validar el funcionamiento de cada archivo (por el momento) dentro de la carpeta routes. el archivo consta de varias secciones, primero contiene la configuracion inicial e imports necesarios, luego los moks y fixturs que se van a usar y por ultimo la seccion de test para admin, auth, health, singup

    -     successful_csv_upload, verifica el camino exitoso al cargar el csv con
          las personas a invitar, se valida la coincidencia del status code y
          mensaje devuelvo, tambien se valida la correcta llamada a las
          funciones process_csv y send_invitation

    -     non_csv_file_upload, se valida el fallo al ingresar un archivo que
          que no es de tipo csv, se verifica la coincidencia del status code
          y el mensaje devuelto, tambien se verifica que la funcion
          process_csv no fue llamada.

    -     handles_invalid_csv_exception, se valida la exepcion por csv mal formado,
          se comprueba la coincidencia del status code y el mensaje devueltos
          y ademas se verifica que esta ves si fue llamada la funcion process_csv, encargada de lanzar la excepcion.

    -     handles_missing_columns_exception, se valida la excepcion por falta
          de columnas dentro del csv, se verifica la coincidencia del
          status code y mensaje devueltos y tambien la correcta llamada a la
          funcion process_csv, encargada de lanzar la excepcion.

    -     login_success, valida el flujo exitoso del login, se verifica la
          coincidencia del status code, la data dentro del json de la 
          respuesta y tambien la correcta llamada a la funcion login con
          cierto argumento.

    -     login_user_not_registered, se valida la excepcion lanzada por login
          cuando un usuario no esta registrado, se verifica la coincidencia en
          el status code y el mensaje devuelto. ademas se verifica que la
          funcion login fue llamada.

    -     auth_me_success, se valida el flujo exitozo de autentificacion, se
          verifica la coincidencia del status code, usando una funcion auxiliar para eliminar las claves created y update at se verifica
          que la data devuelta coincide y se verifica la llamada a la
          funcion verify con cierto argumento.

    -     auth_me_unauthorized, se valida la excepcion de verify cuando el
          token es invalido o esta expirado, se verifica la coincidencia del
          status code y el mensaje devuelto, tambien la llamada a la funcion
          verify con cierto argumento.

    -     auth_me_missing_token, se valida el correcto fallo cuando no 
          proporcionamos un token de autenticacion, se verifica la
          coincidencia del status code y del mensaje devuelto

    -     health_check_success, se valida la respuesta exitosa desde health,
          se verifica la coincidencia del status code y la información de diagnóstico básica de la aplicación.

    -     liveness_check_success, se valida la respuesta exitosa desde
          health/live, se verifica la coincidencia del status code y el 
          mensaje devuelto por el endpoint.

    -     test_readiness_check_success, se valida la respuesta exitosa desde
          health/ready, se verifica la coincidencia del status code, el mensaje devuelto y ademas que la base de datos fue llamada con 
          el argumento ping

    -     readiness_check_db_failure, inverso al test anterior aca se valida
          la respuesta de health/ready cuando la base de datos falla, se 
          verifica la coincidencia del status code, los nuevos valores en la
          respuesta devuelta, que el mensaje de error coincide y que la 
          base de datos fue llamada con el argumento ping

    -     root_endpoint_debug_true, se valida que el endpoint root funciona 
          correctamente en modo debug, se verifica la coincidencia del 
          status code y la data dentro de los campos devueltos por el endpoint.

    -     root_endpoint_debug_false, se valida que el endpoint root funciona
          correctamente en modo produccion, se verifica la coincidencia 
          del estatus code y la data dentro de los campos devueltos por
          el endpoint.

    -     test_check_invitation_success, se valida la respuesta exitosa de 
          /sing-up/invite, se verifica la coincidencia del status code 
          y la respuesta devuelta, ademas se verifica que la funcion 
          check_invitation fue llamada con cierto argumento pasado como 
          query param.

    -     test_check_invitation_not_found, se valida el flujo donde el token
          no fue encontrado, se verifica la coincidencia del status code, el
          mensaje devuelto y que la funcion check_invitatin fue llamada con
          cierto argumento

    -     check_invitation_expired, se hace saltar la ultima excepcion posible
          validando el flujo donde el token esta expirado, se verifica la 
          coincidencia de status code, el mensaje devuelto y la llamada a la 
          funcion check_invitation con cierto argumento

    -     signup_successful_validation, se valida la respuesta exitosa de 
          /sing-up/, se verifica que el status code devuelto por el endpoint
          es efectivamente un 201 created 

    -     signup_invalid_cv_type, se valida la respuesta cuando ingresamos un
          CV que no es tipo PDF, se verifica la coincidencia del status code
          y el mensaje de error devuelto

    -     signup_invalid_linkedin_cv_type, se valida la respuesta cuando 
          ingresamos un linkedin CV que no es tipo PDF, se verifica la 
          coincidencia del status code y el mensaje de error devuelto

    -     signup_invalid_avatar_type, se valida la correcta respuesta cuando
          ingresamos una avatar que no es una imagen, se verifica la 
          coincidencia del status code y el mensaje devuelto 
