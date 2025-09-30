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
          se verifica que la data cohincide con lo declarado y que los atributos
          de tiempo son del tipo datatime

    -     test_bmodel_updated_at_setter, verificamos el recorrido exitoso del setter,
          luego de crear la instancia modificamos la data y vemos que cohincide.
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
          utilizado, que la clave id no esta en la respuesta (doc) y que el nombre cohincide

    -     se valida la creacion de una entidad, se configuran los datos del objeto y la respuesta del metodo.
          se verifica que el metodo fue llamado una vez y que la respuesta cohincide con el 
          inserted_id esperado

    -     find_by_id, se configura el mock, la respuesta del metodo y se llama a este, verificamos que
          el metodo fue llamado una vez y que la data llego completa.
          tambien se testio la posible respuesta none para terminar de cubrir el archivo.

    -     find_all, se crea una lista con datos validos y aca se utiliza el mock que simula a
          asynchronous iterator para generar una respuesta valida del metodo.
          se llama al metodo y se verifica que fue llamado una sola vez, que fue llamado con un diccionario 
          vacio, que la respuesta es una lista, que el largo de esa lista es de la misma cantidad de objetos
          y que la data cohincide.

    -     find_all_with_filters, mismos pasos que en el test anterior pero esta vez se llama al metodo
          con un diccionario que contiene dos filtros, se verifica que fue llamado una vez, que fue llamado con x filtros, que el largo de la lista cohincide con los filtros y que la data cohincide

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
          cohincidencia de documentos recibidos 
