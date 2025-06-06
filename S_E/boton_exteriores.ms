-- Script MAXScript para ejecutar un script Python
try (
    -- Define la ruta COMPLETA a tu archivo .py
    -- ¡Asegúrate de que esta ruta apunte DIRECTAMENTE al archivo .py, incluyendo su nombre y extensión!
    local pythonScriptToRunPath = @"C:\Users\irghhd\OneDrive - Trane Technologies\Desktop\Max\Max\S_E\configurar_arnold_scene.py" 
    -- ^^^ CAMBIA "mi_script_de_python.py" por el nombre real de tu archivo Python

    -- 1. Primero, verifica si el archivo Python existe para un mensaje de error más claro
    if not doesFileExist pythonScriptToRunPath then (
        messageBox ("El archivo Python no se encontró en la ruta especificada:\n" + pythonScriptToRunPath) title:"Error: Script Python No Encontrado"
    ) else (
        -- 2. Si el archivo existe, procede a ejecutarlo con python.ExecuteFile
        python.ExecuteFile pythonScriptToRunPath
        
        -- ¡HE ELIMINADO LA LÍNEA DEL messageBox DE ÉXITO AQUÍ!
    )
) catch (
    -- 3. Si ocurre algún error durante la ejecución de python.ExecuteFile (ya sea que el archivo no se encuentre
    -- o haya un error dentro del script Python mismo), este bloque lo capturará y mostrará el mensaje de error completo.
    messageBox ("Se produjo un error al ejecutar el script Python:\n" + (getCurrentException())) title:"Error de Ejecución de Python"
)