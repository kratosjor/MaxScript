import pymxs
from PySide2 import QtWidgets, QtCore, QtGui
import os
import tempfile
import time

rt = pymxs.runtime

# --- RUTAS DE CONFIGURACIÓN ---
# ¡IMPORTANTE! Nombre del objeto que se va a MERGEAR desde el archivo de referencia.
AO_REFERENCE_OBJECT_NAME = "Ambient_Occlusion" 

# ¡IMPORTANTE! Ruta completa al archivo .max donde reside el objeto de referencia.
# Asegúrate de que esta ruta sea EXACTA y esté actualizada.
REFERENCE_MAX_FILE_PATH = r"C:\Users\irghhd\OneDrive - Trane Technologies\Desktop\Max\Max\S_E\Ambient_Occlusion.max"

class AdditionalOptionsUI(QtWidgets.QDialog):
    def __init__(self):
        super(AdditionalOptionsUI, self).__init__()
        self.setWindowTitle("Opciones Adicionales de Render")
        self.setFixedSize(350, 280) 
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.ao_material = None
        self.temp_original_scene_path = ""
        self.ao_scene_path = ""
        self.reference_object_merged = False 

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # Sección: Carga de Material (Fusionando Objeto de Referencia)
        load_material_group = QtWidgets.QGroupBox("Cargar Material AO")
        load_material_group.setToolTip(f"Fusiona el objeto '{AO_REFERENCE_OBJECT_NAME}' del archivo de referencia y toma su material para AO.")
        load_material_layout = QtWidgets.QVBoxLayout()
        load_material_layout.setSpacing(5)

        self.btn_load_ao_material_from_merge = QtWidgets.QPushButton(f"1. Fusionar Objeto '{AO_REFERENCE_OBJECT_NAME}' y Cargar Material")
        self.btn_load_ao_material_from_merge.clicked.connect(self.merge_object_and_load_material)
        load_material_layout.addWidget(self.btn_load_ao_material_from_merge)

        load_material_group.setLayout(load_material_layout)
        self.main_layout.addWidget(load_material_group)

        # Sección de Render de Ambient Occlusion
        ao_render_group = QtWidgets.QGroupBox("Render de Ambient Occlusion")
        ao_render_group.setToolTip("Opciones para generar renders de Ambient Occlusion de la escena.")
        ao_render_layout = QtWidgets.QVBoxLayout()
        ao_render_layout.setSpacing(5)

        self.btn_apply_ao_render = QtWidgets.QPushButton("2. Generar Render AO")
        self.btn_apply_ao_render.clicked.connect(self.apply_ao_material_and_render)
        self.btn_apply_ao_render.setEnabled(False)
        ao_render_layout.addWidget(self.btn_apply_ao_render)

        ao_render_group.setLayout(ao_render_layout)
        self.main_layout.addWidget(ao_render_group)

        # Sección de Restauración
        restore_group = QtWidgets.QGroupBox("Restaurar Escena Original")
        restore_group.setToolTip("Carga la escena a su estado original.")
        restore_layout = QtWidgets.QVBoxLayout()
        restore_layout.setSpacing(5)

        self.btn_restore_scene = QtWidgets.QPushButton("3. Restaurar Escena Original")
        self.btn_restore_scene.clicked.connect(self.restore_original_scene)
        self.btn_restore_scene.setEnabled(False)
        restore_layout.addWidget(self.btn_restore_scene)

        restore_group.setLayout(restore_layout)
        self.main_layout.addWidget(restore_group)

        # Etiqueta de estado
        self.status_label = QtWidgets.QLabel("Listo. Fusiona el objeto para cargar el material.")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setToolTip("Muestra el estado de las operaciones.")
        self.main_layout.addWidget(self.status_label)

        self.main_layout.addStretch()

        self.setLayout(self.main_layout)

        self.update_button_states()

    def update_button_states(self):
        """Actualiza el estado de los botones."""
        material_loaded = self.ao_material is not None and not rt.isDeleted(self.ao_material) 
        scene_backed_up = os.path.exists(self.temp_original_scene_path) and os.path.exists(self.ao_scene_path)
        
        self.btn_load_ao_material_from_merge.setEnabled(not self.reference_object_merged or self.ao_material is None) 

        self.btn_apply_ao_render.setEnabled(material_loaded)
        self.btn_restore_scene.setEnabled(scene_backed_up)
        
        status_text = "Listo. Fusiona el objeto para cargar el material."
        if material_loaded:
            status_text = f"✅ Material '{self.ao_material.name}' cargado. Listo para renderizar."
        if self.reference_object_merged:
            status_text = f"✅ Objeto '{AO_REFERENCE_OBJECT_NAME}' mergido. " + status_text
        if scene_backed_up:
            status_text += " Escena AO generada y respaldada."
        
        self.status_label.setText(status_text)

    def merge_object_and_load_material(self):
        """
        Fusiona el objeto AO_REFERENCE_OBJECT_NAME desde el archivo .max de referencia
        y luego intenta obtener su material.
        """
        self.status_label.setText(f"Intentando fusionar objeto '{AO_REFERENCE_OBJECT_NAME}' desde '{os.path.basename(REFERENCE_MAX_FILE_PATH)}'...")
        QtWidgets.QApplication.processEvents()

        if not os.path.exists(REFERENCE_MAX_FILE_PATH):
            error_msg = f"❌ Error: El archivo de referencia no existe:\n'{REFERENCE_MAX_FILE_PATH}'\nPor favor, verifica la ruta en el script."
            self.status_label.setText(error_msg)
            QtWidgets.QMessageBox.critical(self, "Error de Archivo de Referencia", error_msg)
            self.update_button_states()
            return

        try:
            rt.mergeMaxFile(REFERENCE_MAX_FILE_PATH, objects=AO_REFERENCE_OBJECT_NAME, prompt=False) 
            
            ao_ref_object = rt.getNodeByName(AO_REFERENCE_OBJECT_NAME)

            if ao_ref_object is not None and not rt.isDeleted(ao_ref_object): 
                if hasattr(ao_ref_object, 'material') and \
                   ao_ref_object.material is not None and \
                   not rt.isDeleted(ao_ref_object.material): 
                    
                    self.ao_material = ao_ref_object.material
                    self.reference_object_merged = True 
                    self.status_label.setText(f"✅ Objeto '{AO_REFERENCE_OBJECT_NAME}' fusionado (o ya existente) y material '{self.ao_material.name}' cargado con éxito.")
                    
                else:
                    self.ao_material = None
                    self.reference_object_merged = False
                    raise ValueError(f"El objeto '{AO_REFERENCE_OBJECT_NAME}' existe pero no tiene un material válido asignado.")
            else:
                self.ao_material = None
                self.reference_object_merged = False
                raise ValueError(f"No se pudo encontrar o fusionar el objeto '{AO_REFERENCE_OBJECT_NAME}' después de intentar el merge. Asegúrate de que el objeto existe en '{os.path.basename(REFERENCE_MAX_FILE_PATH)}'.")

        except Exception as e:
            self.ao_material = None
            self.reference_object_merged = False
            self.status_label.setText(f"❌ Error al fusionar objeto o cargar material: {e}")
            QtWidgets.QMessageBox.critical(self, "Error de Carga de Material", str(e) + "\nPor favor, revisa el MAXScript Listener (F11) para más detalles.")
        
        self.update_button_states()

    def apply_ao_material_and_render(self):
        """
        Guarda la escena original temporalmente, guarda la escena actual con "_AO",
        asigna el material de AO y realiza un render.
        """
        if self.ao_material is None or rt.isDeleted(self.ao_material): 
            self.status_label.setText("❌ Error: Material no cargado. Carga el material primero.")
            QtWidgets.QMessageBox.warning(self, "Material Faltante", "El material no está disponible. Cárgalo primero usando el botón 'Fusionar Objeto...'.")
            return

        current_max_file = rt.maxFilePath + rt.maxFileName
        if not current_max_file:
            self.status_label.setText("❌ Error: Guarda tu escena de trabajo actual antes de generar un render AO.")
            QtWidgets.QMessageBox.warning(self, "Escena no Guardada", "Por favor, guarda tu escena de trabajo actual antes de proceder.")
            return

        temp_dir = tempfile.gettempdir()
        base_name = os.path.splitext(rt.maxFileName)[0]
        timestamp = int(time.time())
        self.temp_original_scene_path = os.path.join(temp_dir, f"{base_name}_original_temp_{os.getpid()}_{timestamp}.max")
        self.ao_scene_path = os.path.splitext(current_max_file)[0] + "_AO.max"

        try:
            self.status_label.setText("Guardando escena original temporalmente...")
            QtWidgets.QApplication.processEvents()
            rt.saveMaxFile(self.temp_original_scene_path, quiet=True)
            rt.format("✅ Escena original de trabajo guardada temporalmente en: %s\n", self.temp_original_scene_path)

            self.status_label.setText(f"Guardando escena con '_AO' como: {os.path.basename(self.ao_scene_path)} y aplicando material...")
            QtWidgets.QApplication.processEvents()

            rt.saveMaxFile(self.ao_scene_path, quiet=True)
            rt.format("✅ Escena AO guardada en: %s\n", self.ao_scene_path)

            for obj in rt.objects:
                if not obj.isHidden and not obj.isFrozen:
                    obj.material = self.ao_material

            self.status_label.setText("Material aplicado. Iniciando render...")
            QtWidgets.QApplication.processEvents()

            rt.render() 
            self.status_label.setText(f"✅ Render de Ambient Occlusion iniciado con el renderizador actual. Escena guardada como: {os.path.basename(self.ao_scene_path)}")

        except Exception as e:
            self.status_label.setText(f"❌ Error al aplicar material y renderizar: {e}")
            QtWidgets.QMessageBox.critical(self, "Error de Render", str(e))
            if os.path.exists(self.temp_original_scene_path):
                try:
                    os.remove(self.temp_original_scene_path)
                    rt.format("Limpiado archivo temporal original: %s\n", self.temp_original_scene_path)
                except Exception as clean_e:
                    rt.format("❌ Error al limpiar archivo temporal: %s\n", str(clean_e))
            self.temp_original_scene_path = ""
            self.ao_scene_path = ""

        self.update_button_states()

    def restore_original_scene(self):
        """
        Carga la escena original que fue guardada temporalmente
        y elimina los archivos de la escena AO y el temporal.
        También intenta eliminar el objeto de referencia si fue mergido.
        """
        if not self.temp_original_scene_path or not os.path.exists(self.temp_original_scene_path):
            self.status_label.setText("⚠️ No se encontró una escena original temporal para restaurar.")
            QtWidgets.QMessageBox.information(self, "Sin Restauración", "No hay una escena original guardada para restaurar. Abre tu archivo manualmente.")
            return

        self.status_label.setText("Restaurando escena original...")
        QtWidgets.QApplication.processEvents()

        temp_original_path_to_load = self.temp_original_scene_path
        ao_scene_path_to_delete = self.ao_scene_path

        try:
            rt.loadMaxFile(temp_original_path_to_load, quiet=True)
            self.status_label.setText("✅ Escena original restaurada con éxito.")

            if self.reference_object_merged:
                obj_to_delete = rt.getNodeByName(AO_REFERENCE_OBJECT_NAME)
                if obj_to_delete is not None and not rt.isDeleted(obj_to_delete): 
                    try:
                        rt.delete(obj_to_delete)
                        rt.format("✅ Objeto de referencia '%s' eliminado de la escena restaurada.\n", AO_REFERENCE_OBJECT_NAME)
                    except Exception as e_del_obj:
                        rt.format("⚠️ No se pudo eliminar el objeto de referencia '%s': %s\n", AO_REFERENCE_OBJECT_NAME, str(e_del_obj))
                        QtWidgets.QMessageBox.warning(self, "Advertencia", f"No se pudo eliminar el objeto de referencia '{AO_REFERENCE_OBJECT_NAME}'. Elimínalo manualmente si es necesario.")
                self.reference_object_merged = False 

            if os.path.exists(temp_original_path_to_load):
                try:
                    os.remove(temp_original_path_to_load)
                    rt.format("✅ Archivo temporal original eliminado: %s\n", temp_original_path_to_load)
                except Exception as e_del:
                    rt.format("⚠️ No se pudo eliminar el archivo temporal original %s: %s\n", temp_original_path_to_load, str(e_del))

            if ao_scene_path_to_delete and os.path.exists(ao_scene_path_to_delete):
                try:
                    os.remove(ao_scene_path_to_delete)
                    rt.format("✅ Archivo de escena AO eliminado: %s\n", ao_scene_path_to_delete)
                except Exception as e_del_ao:
                    rt.format("⚠️ No se pudo eliminar el archivo de escena AO %s: %s\n", ao_scene_path_to_delete, str(e_del_ao))
                    QtWidgets.QMessageBox.warning(self, "Advertencia", f"No se pudo eliminar el archivo _AO.max: {os.path.basename(ao_scene_path_to_delete)}\nPor favor, elimínalo manualmente si es necesario.")
            else:
                rt.format("ℹ️ No se encontró el archivo de escena AO para eliminar: %s\n", ao_scene_path_to_delete)

            self.temp_original_scene_path = ""
            self.ao_scene_path = ""
            
            # ***** NUEVA VENTANA EMERGENTE AQUÍ *****
            QtWidgets.QMessageBox.information(self, "Guardar Escena", 
                                              "La escena original ha sido restaurada.\n"
                                              "Recuerda GUARDAR tu archivo actual para no perder cambios recientes.",
                                              QtWidgets.QMessageBox.Ok)

        except Exception as e:
            self.status_label.setText(f"❌ Error al restaurar la escena original: {e}")
            QtWidgets.QMessageBox.critical(self, "Error al Restaurar Escena", str(e))

        self.update_button_states()

def run_additional_options_ui():
    """
    Función para ejecutar la UI de opciones adicionales.
    Maneja el cierre de instancias previas para evitar duplicados.
    """
    global additional_options_dialog
    try:
        if 'additional_options_dialog' in globals() and additional_options_dialog and hasattr(additional_options_dialog, 'close') and hasattr(additional_options_dialog, 'deleteLater'):
            additional_options_dialog.close()
            additional_options_dialog.deleteLater()
            additional_options_dialog = None
    except Exception as e:
        print(f"Error al intentar cerrar la UI existente de opciones adicionales: {e}")
        pass

    additional_options_dialog = AdditionalOptionsUI()
    additional_options_dialog.show()

if __name__ == "__main__":
    run_additional_options_ui()