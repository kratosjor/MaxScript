try(destroyDialog ImportarModelosDialog) catch()

rollout ImportarModelosDialog "Importar Modelos" width:400 height:300
(
    local carpetaModelos = "C:\Users\Jordan\Desktop\Cursos Programacion\Max\modelos"
    local archivosModelos = getFiles (carpetaModelos + "\\*.max")
    local nombresModelos = for archivo in archivosModelos collect (getFilenameFile archivo)

    listBox lbModelos "Modelos Disponibles" items:nombresModelos pos:[10,10] width:380 height:200
    button btnImportar "Importar Modelo" pos:[150,230] width:100 height:30

    on btnImportar pressed do
    (
        print "Botón presionado"
        try (
            if lbModelos.selection.count > 0 then
            (
                local nombreSeleccionado = lbModelos.selection[1]
                print ("Modelo seleccionado: " + nombreSeleccionado)

                local indice = findItem nombresModelos nombreSeleccionado
                print ("Índice encontrado: " + indice as string)

                if indice > 0 do (
                    local modeloSeleccionado = archivosModelos[indice]
                    print ("Ruta seleccionada: " + modeloSeleccionado)

                    if doesFileExist modeloSeleccionado then
                    (
                        -- Cambiar importFile por merge para no cerrar la escena
                        mergeMaxFile modeloSeleccionado #noRedraw
                        messageBox ("Modelo importado exitosamente: " + nombreSeleccionado) title:"Éxito"
                    )
                    else
                    (
                        messageBox "El archivo seleccionado no existe." title:"Error"
                    )
                )
            )
            else
            (
                messageBox "Por favor, selecciona un modelo para importar." title:"Advertencia"
            )
        ) catch (
            messageBox ("Se produjo un error:\n" + getCurrentException()) title:"Error Crítico"
        )
    )
)

createDialog ImportarModelosDialog
