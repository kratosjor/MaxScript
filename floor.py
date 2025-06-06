import pymxs
from PySide2 import QtWidgets
rt = pymxs.runtime

class VentanaMuro(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Herramientas de Muro")
        self.setFixedSize(300, 150)

        layout = QtWidgets.QVBoxLayout(self)

        self.btn_muro = QtWidgets.QPushButton("Crear Muro desde Línea (300x10 cm)")
        self.btn_muro.clicked.connect(self.crear_muro)
        layout.addWidget(self.btn_muro)

        self.btn_muro_ventana = QtWidgets.QPushButton("Crear Muro con Ventana (100-100-100)")
        self.btn_muro_ventana.clicked.connect(self.crear_muro_con_ventana)
        layout.addWidget(self.btn_muro_ventana)

    def crear_muro(self):
        if not rt.selection.count:
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona una línea primero.")
            return

        linea = rt.selection[0]

        if not rt.isKindOf(linea, rt.Line) and not rt.isKindOf(linea, rt.SplineShape):
            QtWidgets.QMessageBox.warning(self, "Error", "El objeto seleccionado no es una línea.")
            return

        self.configurar_muro(linea, 10.0, 300.0, 150.0)

        QtWidgets.QMessageBox.information(self, "Hecho", "Muro creado exitosamente.")

    def crear_muro_con_ventana(self):
        if not rt.selection.count:
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona una línea primero.")
            return

        base_line = rt.selection[0]

        if not rt.isKindOf(base_line, rt.Line) and not rt.isKindOf(base_line, rt.SplineShape):
            QtWidgets.QMessageBox.warning(self, "Error", "El objeto seleccionado no es una línea.")
            return

        # Crear las 3 partes
        z_positions = [50.0, 150.0, 250.0]  # Alturas Z
        alturas = [100.0, 100.0, 100.0]
        anchos = [10.0, 5.0, 10.0]

        for i in range(3):
            copia = rt.copy(base_line)
            self.configurar_muro(copia, anchos[i], alturas[i], z_positions[i])

        # Eliminar la línea original
        rt.delete(base_line)

        QtWidgets.QMessageBox.information(self, "Listo", "Se creó el muro con abertura de ventana.")

    def configurar_muro(self, linea, ancho, alto, z_position):
        linea.render_displayRenderMesh = True
        linea.render_displayViewportMesh = True
        linea.render_renderable = True
        linea.render_useRendererSettings = False
        linea.render_renderDisplay = True
        linea.render_viewportDisplay = True
        linea.render_useViewSize = False
        linea.render_useViewportSize = False
        linea.render_generateMappingCoords = True
        linea.render_renderOperator = rt.name('rectangular')
        linea.render_width = ancho
        linea.render_height = alto

        push = rt.Push()
        push.value = 0.0
        rt.addModifier(linea, push)

        rt.move(linea, rt.point3(0, 0, z_position))

# Mostrar ventana
try:
    ventana_muro.close()
except:
    pass

ventana_muro = VentanaMuro()
ventana_muro.show()
