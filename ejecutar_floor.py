rollout ventanaMuroRollout "Herramientas de Muro" width:220 height:100
(
    button btnMuro "Abrir Herramienta de Muro" width:200 height:40

    on btnMuro pressed do
    (
        -- Ejecuta el script Python
        python.executeFile @"C:\Users\Jordan\Desktop\Cursos Programacion\Max\floor.py"
    )
)

-- Crear el panel flotante
createDialog ventanaMuroRollout
