import os
import pymxs
from PySide2 import QtWidgets, QtCore, QtGui

rt = pymxs.runtime
carpeta_modelos = r"C:\Users\irghhd\OneDrive - Trane Technologies\Desktop\Max\modelos"
imagen_default = "default.jpg"

class OpcionesImportacionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Opciones de importación")
        self.setFixedSize(300, 120)
        layout = QtWidgets.QVBoxLayout(self)

        self.chk_ignorar_luces = QtWidgets.QCheckBox("Ignorar luces")
        self.chk_ignorar_camaras = QtWidgets.QCheckBox("Ignorar cámaras")
        layout.addWidget(self.chk_ignorar_luces)
        layout.addWidget(self.chk_ignorar_camaras)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(btns)

        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

class TarjetaModelo(QtWidgets.QWidget):
    def __init__(self, nombre, ruta_modelo, ruta_imagen, callback_importar):
        super().__init__()
        self.ruta_modelo = ruta_modelo
        self.callback_importar = callback_importar

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        if ruta_imagen and os.path.exists(ruta_imagen):
            pixmap = QtGui.QPixmap(ruta_imagen).scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        else:
            ruta_imagen_default = os.path.join(carpeta_modelos, imagen_default)
            if os.path.exists(ruta_imagen_default):
                pixmap = QtGui.QPixmap(ruta_imagen_default).scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            else:
                pixmap = QtGui.QPixmap(100, 100)
                pixmap.fill(QtCore.Qt.lightGray)

        label_img = QtWidgets.QLabel()
        label_img.setPixmap(pixmap)
        label_img.setAlignment(QtCore.Qt.AlignCenter)

        label_nombre = QtWidgets.QLabel(nombre)
        label_nombre.setAlignment(QtCore.Qt.AlignCenter)

        btn = QtWidgets.QPushButton("Importar")
        btn.clicked.connect(self.importar)

        layout.addWidget(label_img)
        layout.addWidget(label_nombre)
        layout.addWidget(btn)

    def importar(self):
        self.callback_importar(self.ruta_modelo)

class ImportarModelosDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biblioteca de Modelos")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("font-size: 14px;")

        layout_principal = QtWidgets.QVBoxLayout(self)

        # ComboBox para seleccionar la categoría
        self.combo_categoria = QtWidgets.QComboBox()
        self.combo_categoria.addItem("Selecciona una categoría")
        self.combo_categoria.currentTextChanged.connect(self.cargar_modelos)
        layout_principal.addWidget(self.combo_categoria)

        # Scroll con tarjetas
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.contenedor = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.contenedor)
        self.scroll.setWidget(self.contenedor)

        layout_principal.addWidget(self.scroll)

        self.setLayout(layout_principal)
        self.cargar_categorias()

    def cargar_categorias(self):
        try:
            carpetas = [f for f in os.listdir(carpeta_modelos) if os.path.isdir(os.path.join(carpeta_modelos, f))]
            self.combo_categoria.addItems(carpetas)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error al cargar carpetas", str(e))

    def limpiar_grid(self):
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def cargar_modelos(self, categoria):
        if categoria == "Selecciona una categoría":
            self.limpiar_grid()
            return

        ruta_categoria = os.path.join(carpeta_modelos, categoria)
        if not os.path.exists(ruta_categoria):
            QtWidgets.QMessageBox.warning(self, "Categoría no encontrada", "La carpeta seleccionada no existe.")
            return

        self.limpiar_grid()

        try:
            archivos = [f for f in os.listdir(ruta_categoria) if f.lower().endswith(".max")]
            archivos.sort()
            fila, columna = 0, 0

            for archivo in archivos:
                nombre = os.path.splitext(archivo)[0]
                ruta_modelo = os.path.join(ruta_categoria, archivo)

                ruta_imagen = None
                for ext in [".jpg", ".png"]:
                    posible_imagen = os.path.join(ruta_categoria, nombre + ext)
                    if os.path.exists(posible_imagen):
                        ruta_imagen = posible_imagen
                        break

                tarjeta = TarjetaModelo(nombre, ruta_modelo, ruta_imagen, self.importar_modelo)
                self.grid.addWidget(tarjeta, fila, columna)

                columna += 1
                if columna >= 3:
                    columna = 0
                    fila += 1

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error al cargar modelos", str(e))

    def importar_modelo(self, ruta):
        if not os.path.exists(ruta):
            QtWidgets.QMessageBox.warning(self, "Archivo no encontrado", "El archivo seleccionado no existe.")
            return

        opciones_dialog = OpcionesImportacionDialog()
        if opciones_dialog.exec_():
            ignorar_luces = opciones_dialog.chk_ignorar_luces.isChecked()
            ignorar_camaras = opciones_dialog.chk_ignorar_camaras.isChecked()

            try:
                objetos_antes = set(rt.objects)
                rt.mergeMaxFile(ruta, rt.name('select'), quiet=True)
                objetos_despues = set(rt.objects)
                nuevos_objetos = objetos_despues - objetos_antes

                eliminados = []
                for obj in nuevos_objetos:
                    if ignorar_luces and rt.isKindOf(obj, rt.Light):
                        rt.delete(obj)
                        eliminados.append("Luz")
                    elif ignorar_camaras and rt.isKindOf(obj, rt.Camera):
                        rt.delete(obj)
                        eliminados.append("Cámara")

                mensaje = f"Modelo importado:\n{ruta}"
                if eliminados:
                    mensaje += f"\nObjetos eliminados: {', '.join(set(eliminados))}"
                QtWidgets.QMessageBox.information(self, "Importación Exitosa", mensaje)

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error al importar", str(e))

# Mostrar diálogo principal
try:
    dialogo.close()
except:
    pass

dialogo = ImportarModelosDialog()
dialogo.show()
