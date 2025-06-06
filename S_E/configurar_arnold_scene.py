import os
import pymxs
from PySide2 import QtWidgets, QtCore

rt = pymxs.runtime

# --- CONFIGURACIÓN DE LAS RUTAS DE LOS ARCHIVOS ---
ARNOLD_SKYDOME_FILE = r"C:\Users\irghhd\OneDrive - Trane Technologies\Desktop\Max\Max\S_E\Arnold_Skydome_Light.max"
CAMARA_S_E_FILE = r"C:\Users\irghhd\OneDrive - Trane Technologies\Desktop\Max\Max\S_E\Camera_S_E.max"
ARNOLD_GPU_PRESET_FILE = r"C:\Users\irghhd\OneDrive - Trane Technologies\Desktop\Max\Max\S_E\Arnold_GPU_Preset.rps"

# --- CONFIGURACIÓN DEL TAMAÑO DE RENDER ---
RENDER_WIDTH = 1613
RENDER_HEIGHT = 788

def escape_path(path):
    return path.replace("\\", "\\\\")

class ImportSceneElementsUI(QtWidgets.QDialog):
    def __init__(self):
        super(ImportSceneElementsUI, self).__init__()
        self.setWindowTitle("Importar/Configurar Escena")
        self.setFixedSize(300, 450)
        
        # --- Configuración para mantener la ventana siempre encima y con botones de control ---
        self.setWindowFlags(QtCore.Qt.Window | 
                            QtCore.Qt.WindowStaysOnTopHint | 
                            QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowCloseButtonHint)
        # --- Fin de la configuración de ventana ---

        layout = QtWidgets.QVBoxLayout()

        # Botones de configuración
        self.btn_load_gpu_preset = QtWidgets.QPushButton("Cargar Preset Render (GPU)")
        self.btn_load_gpu_preset.clicked.connect(self.cargar_render_preset_gpu)
        self.btn_load_gpu_preset.setToolTip("Carga una configuración de render predefinida y optimizada para renderizado por GPU.")
        layout.addWidget(self.btn_load_gpu_preset)

        self.btn_configurar_render_size = QtWidgets.QPushButton("Configurar Tamaño de Render")
        self.btn_configurar_render_size.clicked.connect(self.configurar_tamano_render)
        self.btn_configurar_render_size.setToolTip("Abre una ventana para establecer las dimensiones de la imagen a renderizar (resolución).")
        layout.addWidget(self.btn_configurar_render_size)

        # Botones de importación
        self.btn_importar_luz = QtWidgets.QPushButton("Importar Luz Skydome Arnold")
        self.btn_importar_luz.clicked.connect(self.importar_luz_skydome)
        self.btn_importar_luz.setToolTip("Importa una luz Skydome de Arnold para iluminación ambiental en la escena.")
        layout.addWidget(self.btn_importar_luz)

        self.btn_importar_camara = QtWidgets.QPushButton("Importar Cámara")
        self.btn_importar_camara.clicked.connect(self.importar_camara)
        self.btn_importar_camara.setToolTip("Importa una cámara predefinida en la escena.")
        layout.addWidget(self.btn_importar_camara)        

        # Etiqueta de estado
        self.status_label = QtWidgets.QLabel("Listo para importar/configurar.")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setToolTip("Muestra mensajes sobre el estado de las operaciones de la herramienta.")
        
        # --- OPCIONES DE CÁMARA ---
        camera_options_group = QtWidgets.QGroupBox("Opciones de cámara")
        camera_options_group.setToolTip("Configuraciones y ajustes para las cámaras Physical Camera en la escena.")
        camera_options_layout = QtWidgets.QVBoxLayout()

        self.btn_auto_tilt = QtWidgets.QPushButton("Activar Perspectiva Vertical Automática")
        self.btn_auto_tilt.clicked.connect(self.activar_auto_tilt)
        self.btn_auto_tilt.setToolTip("Activa/Desactiva la corrección automática de la perspectiva vertical en cámaras físicas. Evita la distorsión al fotografiar edificios altos.")
        camera_options_layout.addWidget(self.btn_auto_tilt)
        
        self.btn_auto_tilt_off = QtWidgets.QPushButton("Desactivar Perspectiva Vertical Automática")
        self.btn_auto_tilt_off.clicked.connect(self.desactivar_auto_tilt)
        self.btn_auto_tilt_off.setToolTip("Activa/Desactiva la corrección automática de la perspectiva vertical en cámaras físicas. Evita la distorsión al fotografiar edificios altos.")
        camera_options_layout.addWidget(self.btn_auto_tilt_off)

        # --- Focal Length dentro de Opciones de cámara ---
        h_layout = QtWidgets.QHBoxLayout()
        label_focal_length = QtWidgets.QLabel("Focal Length (mm):")
        label_focal_length.setToolTip("Define la longitud focal de la lente de la cámara en milímetros. Afecta el campo de visión.")
        self.spinner = QtWidgets.QDoubleSpinBox()
        self.spinner.setRange(1.0, 300.0)
        self.spinner.setValue(35.0)
        self.spinner.setSingleStep(1.0)
        self.spinner.setDecimals(1)
        self.spinner.setToolTip("Ajusta la longitud focal de las cámaras. Valores más bajos para gran angular, más altos para teleobjetivo.")
        h_layout.addWidget(label_focal_length)
        h_layout.addWidget(self.spinner)

        camera_options_layout.addLayout(h_layout)

        # Botón para aplicar focal length
        self.btn_apply = QtWidgets.QPushButton("Aplicar a Cámaras Seleccionadas")
        self.btn_apply.clicked.connect(self.apply_focal_length)
        self.btn_apply.setToolTip("Aplica la longitud focal especificada a las cámaras físicas actualmente seleccionadas.")
        camera_options_layout.addWidget(self.btn_apply)

        camera_options_group.setLayout(camera_options_layout)

        layout.addWidget(camera_options_group)

        # --- F-Number (F-Stop) dentro de Opciones de cámara ---
        h_layout_fnumber = QtWidgets.QHBoxLayout()
        label_fnumber = QtWidgets.QLabel("F-Number (F-Stop):")
        label_fnumber.setToolTip("El número f (F-Stop) controla la apertura de la cámara, afectando la exposición y la profundidad de campo.")
        self.spinner_fnumber = QtWidgets.QDoubleSpinBox()
        self.spinner_fnumber.setRange(0.5, 32.0)
        self.spinner_fnumber.setValue(8.0)
        self.spinner_fnumber.setSingleStep(0.1)
        self.spinner_fnumber.setDecimals(1)
        self.spinner_fnumber.setToolTip("La Longitud Focal (Focal Length) determina el ángulo de visión de la cámara. Valores bajos dan un ángulo amplio (gran angular), valores altos dan un ángulo estrecho (teleobjetivo).")
        h_layout_fnumber.addWidget(label_fnumber)
        h_layout_fnumber.addWidget(self.spinner_fnumber)
        
        camera_options_layout.addLayout(h_layout_fnumber) 

        self.btn_apply_fnumber = QtWidgets.QPushButton("Aplicar F-Number a Cámaras Seleccionadas")
        self.btn_apply_fnumber.clicked.connect(self.apply_f_number)
        self.btn_apply_fnumber.setToolTip("El F-Number (F-Stop) controla la apertura de la cámara (cantidad de luz que entra) y la profundidad de campo (qué tan desenfocados aparecen los elementos fuera de foco). Valores bajos (ej. f/2.8) dan más luz y un desenfoque mayor; valores altos (ej. f/16) dan menos luz y mayor nitidez en toda la escena.")
        camera_options_layout.addWidget(self.btn_apply_fnumber)
        
        ##### boton para herramienta de importacion
        self.btn_importar = QtWidgets.QPushButton("Abrir Importar Modelos")
        self.btn_importar.setFixedSize(270, 40)
        self.btn_importar.clicked.connect(self.ejecutar_script_python)
        self.btn_importar.setToolTip("Abre una herramienta externa para importar modelos 3D a la escena.")

        ######################################################################################################################
        #CAMERA AA
        # --- SECCIÓN: OPCIONES DE CALIDAD DE RENDER ---
        render_quality_group = QtWidgets.QGroupBox("Calidad de Render (Arnold)")
        render_quality_group.setToolTip("Ajustes de calidad para el renderizador Arnold activo.")
        render_quality_layout = QtWidgets.QVBoxLayout()

        # Camera (AA) Samples
        h_layout_aa = QtWidgets.QHBoxLayout()
        label_aa = QtWidgets.QLabel("Camera (AA) Samples:")
        label_aa.setToolTip("Controla la calidad general del anti-aliasing y el muestreo de la imagen. Un valor más alto reduce el ruido y mejora la nitidez.")
        self.spinner_aa_samples = QtWidgets.QSpinBox()
        self.spinner_aa_samples.setRange(1, 15) 
        self.spinner_aa_samples.setValue(5)    
        h_layout_aa.addWidget(label_aa)
        h_layout_aa.addWidget(self.spinner_aa_samples)
        render_quality_layout.addLayout(h_layout_aa)
        
        # Botón para aplicar la calidad de render
        self.btn_apply_render_quality = QtWidgets.QPushButton("Aplicar Calidad de Render")
        self.btn_apply_render_quality.clicked.connect(self.apply_render_quality) 
        self.btn_apply_render_quality.setToolTip("Camera (AA) Samples controla la calidad general del renderizado y el suavizado de bordes (anti-aliasing). Un valor más alto reduce el ruido visual y mejora la nitidez de la imagen.")
        render_quality_layout.addWidget(self.btn_apply_render_quality)

        render_quality_group.setLayout(render_quality_layout)
        layout.addWidget(render_quality_group) 

        layout.addWidget(self.status_label) 
        self.setLayout(layout) 
        
        layout.addWidget(self.btn_importar)
        
        self.setLayout(layout)
        
    def ejecutar_script_python(self):
        ruta_script = r"C:\Users\irghhd\OneDrive - Trane Technologies\Desktop\Max\Max\importar.py" 
        
        if os.path.exists(ruta_script):
            try:
                with open(ruta_script, 'r', encoding='utf-8') as file:
                    exec(file.read(), globals()) 
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error de ejecución del script Python secundario", str(e))
        else:
            QtWidgets.QMessageBox.warning(self, "Archivo Python no encontrado", f"No se encontró el archivo:\n{ruta_script}")

    def importar_luz_skydome(self):
        self.status_label.setText("Importando luz, por favor espere...")
        QtWidgets.QApplication.processEvents()

        try:
            if not os.path.exists(ARNOLD_SKYDOME_FILE):
                raise FileNotFoundError(f"El archivo de luz Skydome de Arnold no se encontró en: {ARNOLD_SKYDOME_FILE}")
            objetos_antes = set(rt.objects)
            rt.mergeMaxFile(ARNOLD_SKYDOME_FILE)
            objetos_despues = set(rt.objects)
            nuevos_objetos = objetos_despues - objetos_antes

            luz_skydome_importada = False
            for obj in nuevos_objetos:
                if rt.isKindOf(obj, rt.light) and ("skydome" in obj.name.lower() or "arnold" in obj.name.lower()):
                    luz_skydome_importada = True
                    break

            if not luz_skydome_importada:
                self.status_label.setText("⚠️ Luz importada, pero no se encontró Skydome. Revisa el archivo.")
            else:
                self.status_label.setText("✅ ¡Luz Skydome Arnold importada con éxito!")

        except Exception as e:
            self.status_label.setText(f"❌ Error durante la importación de la luz: {e}")

    def importar_camara(self):
        self.status_label.setText("Importando cámara, por favor espere...")
        QtWidgets.QApplication.processEvents()

        try:
            if not os.path.exists(CAMARA_S_E_FILE):
                raise FileNotFoundError(f"El archivo de la cámara no se encontró en: {CAMARA_S_E_FILE}")
            
            objetos_antes = set(rt.objects)
            rt.mergeMaxFile(CAMARA_S_E_FILE)
            objetos_despues = set(rt.objects)
            nuevos_objetos = objetos_despues - objetos_antes

            camara_importada = False
            # Aquí, ya no intentamos activar el control de exposición individual
            # ni el control de exposición global de la escena.
            for obj in nuevos_objetos:
                if rt.isKindOf(obj, rt.Camera):
                    camara_importada = True
                    # Opcional: Si quieres un mensaje de consola para indicar que la cámara fue importada
                    rt.format("✅ Cámara importada: %s\n", obj.name) 
                    
            if not camara_importada:
                self.status_label.setText("⚠️ Cámara importada, pero no se encontró. Revisa el archivo.")
            else:
                # Mensaje actualizado para reflejar que la configuración de exposición es externa
                self.status_label.setText("✅ ¡Cámara importada con éxito! La exposición se maneja por preset.")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error durante la importación de la cámara: {e}")

    # Eliminamos la función configurar_exposure_control_escena ya que no es necesaria
    # def configurar_exposure_control_escena(self):
    #    ... (código anterior de esta función) ...


    def configurar_tamano_render(self):
        self.status_label.setText("Configurando tamaño de render...")
        QtWidgets.QApplication.processEvents()

        try:
            rt.renderWidth = RENDER_WIDTH
            rt.renderHeight = RENDER_HEIGHT
            self.status_label.setText(f"✅ ¡Tamaño de render configurado a {RENDER_WIDTH}x{RENDER_HEIGHT}!")
        except Exception as e:
            self.status_label.setText(f"❌ Error al configurar el tamaño de render: {e}")

    def cargar_render_preset_gpu(self):
        self.status_label.setText("Cargando preset de render GPU desde archivo...")
        QtWidgets.QApplication.processEvents()

        try:
            if not os.path.exists(ARNOLD_GPU_PRESET_FILE):
                raise FileNotFoundError(f"El archivo de preset de render GPU no se encontró en: {ARNOLD_GPU_PRESET_FILE}")

            escaped_path = escape_path(ARNOLD_GPU_PRESET_FILE)
            maxscript_command = f'renderPresets.LoadAll 0 @"{escaped_path}"'
            rt.execute(maxscript_command)

            current_renderer = rt.renderers.current
            if hasattr(current_renderer, 'className') and "Arnold" in current_renderer.className:
                try:
                    device_type = rt.execute("renderers.current.renderDevice.deviceType as string")
                    if "GPU" in device_type.upper():
                        self.status_label.setText("✅ ¡Preset de Render GPU cargado con éxito!")
                    else:
                        self.status_label.setText(f"⚠️ Preset cargado, pero el dispositivo no es GPU. Dispositivo actual: {device_type}")
                except Exception:
                    self.status_label.setText("⚠️ Preset cargado, pero no se pudo verificar el dispositivo.")
            else:
                self.status_label.setText("⚠️ Preset cargado, pero Arnold no es el renderizador activo o no se pudo verificar.")

        except Exception as e:
            self.status_label.setText(f"❌ Error durante la carga del preset de render: {e}")

    def activar_auto_tilt(self):
        self.status_label.setText("Activando Auto Vertical Tilt Correction...")
        QtWidgets.QApplication.processEvents()

        try:
            camaras_afectadas = 0
            for obj in rt.objects:
                if hasattr(obj, 'autoVerticalTiltCorrection'):
                    try:
                        obj.autoVerticalTiltCorrection = True
                        camaras_afectadas += 1
                    except:
                        pass

            if camaras_afectadas > 0:
                self.status_label.setText(f"✅ Auto Vertical Tilt Correction activado en {camaras_afectadas} cámara(s).")
            else:
                self.status_label.setText("⚠️ No se encontró ninguna cámara compatible.")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")
            
    def desactivar_auto_tilt(self):
        self.status_label.setText("Desactivando Auto Vertical Tilt Correction y reiniciando inclinación vertical...")
        QtWidgets.QApplication.processEvents()

        try:
            camaras_afectadas = 0
            for obj in rt.objects:
                if hasattr(obj, 'autoVerticalTiltCorrection') and hasattr(obj, 'verticalTiltCorrection'):
                    try:
                        obj.autoVerticalTiltCorrection = False
                        obj.verticalTiltCorrection = 0.0 
                        camaras_afectadas += 1
                    except:
                        pass

            if camaras_afectadas > 0:
                self.status_label.setText(f"✅ Se desactivó Auto Vertical Tilt y se reinició inclinación en {camaras_afectadas} cámara(s).")
            else:
                self.status_label.setText("⚠️ No se encontró ninguna cámara compatible.")
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")
            
            
    ########################################################################################################
    def apply_focal_length(self):
        focal_value = self.spinner.value()
        updated = 0

        selected_objs = rt.selection
        for obj in selected_objs:
            rt.format("→ Objeto seleccionado: %, tipo: %\n", obj.name, rt.classof(obj))

            try:
                if rt.isProperty(obj, "focal_length_mm"):
                    obj.focal_length_mm = focal_value
                    updated += 1
                    rt.format("✅ %: focal_length_mm cambiado a % mm\n", obj.name, focal_value)
                elif rt.isProperty(obj, "focalLength"):
                    obj.focalLength = focal_value
                    updated += 1
                    rt.format("✅ %: focalLength cambiado a % mm\n", obj.name, focal_value)
                else:
                    rt.format("⚠️ % no tiene propiedad focal_length_mm ni focalLength.\n", obj.name)
            except Exception as e:
                rt.format("❌ Error al cambiar focal length de %: %\n", obj.name, str(e))

        self.status_label.setText(f"Se actualizaron {updated} cámaras con focal length = {focal_value} mm.")

    ########################################################################################################
    def apply_f_number(self):
        f_number_value = self.spinner_fnumber.value()
        updated = 0
        skipped = 0

        selected_objs = rt.selection
        for obj in selected_objs:
            obj_class = rt.classof(obj)
            rt.format("→ Objeto seleccionado: %, tipo: %\n", obj.name, obj_class)

            if str(obj_class) == "Physical":
                try:
                    if rt.isProperty(obj, "f_number"):
                        obj.f_number = f_number_value 
                        updated += 1
                        rt.format("✅ %: f_number cambiado a %\n", obj.name, f_number_value)
                    else:
                        rt.format("⚠️ % (Physical Camera) no tiene la propiedad 'f_number'.\n", obj.name)
                        skipped += 1
                except Exception as e:
                    rt.format("❌ Error al cambiar F-Number de %: %\n", obj.name, str(e))
            else:
                rt.format(" skipping %: No es una Physical Camera (tipo: %).\n", obj.name, obj_class)
                skipped += 1

        self.status_label.setText(f"Se actualizaron {updated} cámaras con F-Number = {f_number_value}. (Ignoradas: {skipped})")
    ############################################################################################################################
    def apply_render_quality(self):
        try:
            renderer_class_name = str(rt.classof(rt.renderers.current))
            rt.format("Clase del renderizador actual: %s\n", renderer_class_name) 
        except Exception as e:
            self.status_label.setText(f"Error al obtener la clase del renderizador: {str(e)}")
            rt.format("❌ Error al obtener la clase del renderizador: %\n", str(e))
            return 

        if renderer_class_name == "Arnold": 
            aa_samples = self.spinner_aa_samples.value()

            try:
                rt.renderers.current.AA_samples = aa_samples

                self.status_label.setText(f"Calidad de render Arnold actualizada: Camera (AA) Samples = {aa_samples}.")
                rt.format("✅ Calidad de render Arnold actualizada: Camera (AA) Samples = %s\n", aa_samples)

            except Exception as e:
                self.status_label.setText(f"Error al configurar Camera (AA) Samples de Arnold: {str(e)}")
                rt.format("❌ Error al configurar Camera (AA) Samples de Arnold: %\n", str(e))
        else:
            self.status_label.setText(f"El renderizador activo no es Arnold ({renderer_class_name}). No se aplicaron los ajustes de calidad.")
            rt.format("⚠️ El renderizador activo no es Arnold (%s). No se aplicaron los ajustes de calidad.\n", renderer_class_name)

def main():
    global dialog
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = ImportSceneElementsUI()
    dialog.show()

if __name__ == "__main__":
    main()