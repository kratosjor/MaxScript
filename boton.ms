-- Crear un bot�n en el Panel de Utilidades o un Panel flotante
rollout importarModelosRollout "Importar Modelos" width:200 height:100
(
    button btnImportar "Abrir Importar Modelos" width:180 height:40

    on btnImportar pressed do
    (
        -- Ejecutar el script Python cuando el bot�n se presiona
        python.executeFile "C:\Users\irghhd\OneDrive - Trane Technologies\Desktop\Max\Max"  -- Cambia la ruta al lugar donde tienes tu script Python
    )
)

-- Crear el panel flotante para el bot�n
createDialog importarModelosRollout
