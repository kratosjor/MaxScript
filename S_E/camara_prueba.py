rollout changeFocalLengthRollout "Focal Length Control" width:200 height:100
(
    spinner spn_focal "Focal Length (mm):" range:[1,300,35] type:#float scale:1 align:#left
    button btn_apply "Aplicar a Cámaras Seleccionadas"

    on btn_apply pressed do
    (
        local updated = 0

        for obj in selection do
        (
            format "→ Objeto seleccionado: %, tipo: %\n" obj.name (classof obj)

            try
            (
                if isProperty obj #focal_length_mm then
                (
                    obj.focal_length_mm = spn_focal.value
                    updated += 1
                    format "✅ %: focal_length_mm cambiado a % mm\n" obj.name spn_focal.value
                )
                else if isProperty obj.baseObject #focal_length_mm then
                (
                    obj.baseObject.focal_length_mm = spn_focal.value
                    updated += 1
                    format "✅ % (baseObject): focal_length_mm cambiado a % mm\n" obj.name spn_focal.value
                )
                else
                (
                    format "⚠️ %: No tiene propiedad 'focal_length_mm'. Clase: %\n" obj.name (classof obj)
                )
            )
            catch (format "❌ Error modificando %: %\n" obj.name (getCurrentException()))
        )

        if updated == 0 then
            messageBox "No se modificó ninguna cámara válida." title:"Resultado"
        else
            messageBox ("Se actualizó la distancia focal en " + updated as string + " cámara(s).") title:"Éxito"
    )
)

createDialog changeFocalLengthRollout
