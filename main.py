import sys
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from datetime import date
from functools import partial
import pymysql
from PIL import Image, ImageTk
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER, landscape, LEGAL
from os import startfile

guardar_img = Image.open('guardar.png')
cancelar_img = Image.open('cancelar.png')
pdf_img = Image.open('pdf.png')

contador_btn = 0

# host = 'localhost'
# user = 'Zaid'
# passw = 'admin'
database = 'autotransportes_pantaco'

host = ''
user = ''
passw = ''


def ventana_login():

    login_wndw = tk.Toplevel()
    login_wndw.title('Inicio de Sesion')
    login_wndw.maxsize(320, 220)
    login_wndw.minsize(320, 220)
    login_wndw.attributes('-topmost', 'true')

    titulo = tk.Label(login_wndw, text="Autotransportes Pantaco S.A. de C.V.", font='Segoe 12 bold')

    host_lbl = tk.Label(login_wndw, text='Host:')
    host_entry = tk.Entry(login_wndw)

    usuario_lbl = tk.Label(login_wndw, text='Nombre de Usuario:')
    usuario_entry = tk.Entry(login_wndw)

    contrasena_lbl = tk.Label(login_wndw, text='Contraseña:')
    contrasena_entry = tk.Entry(login_wndw, show='*')

    iniciar_btn = tk.Button(login_wndw, text='Iniciar Sesion')
    salir_btn = tk.Button(login_wndw, text='Salir')

    titulo.grid(column=0, row=0, columnspan=2, padx=10, pady=10)
    host_lbl.grid(column=0, row=1, padx=10, pady=10)
    host_entry.grid(column=1, row=1, padx=10, pady=10)

    usuario_lbl.grid(column=0, row=2, padx=10, pady=10)
    usuario_entry.grid(column=1, row=2, padx=10, pady=10)

    contrasena_lbl.grid(column=0, row=3, padx=10, pady=10)
    contrasena_entry.grid(column=1, row=3, padx=10, pady=10)

    iniciar_btn.grid(column=0, row=4, padx=10, pady=10,)
    salir_btn.grid(column=1, row=4, padx=10, pady=10)

    def conectar():
        global host
        global user
        global passw
        host = host_entry.get()
        user = usuario_entry.get()
        passw = contrasena_entry.get()

        try:
            db = pymysql.connect(host=host, user=user, passwd=passw, database=database)

            if db.open is True:

                crear_tablas()
                main = MainView(root)
                main.pack(side="top", fill="both", expand=True)
                login_wndw.destroy()

        except pymysql.err.OperationalError:
            messagebox.showerror('Error!', 'Nombre de usuario o contraseña invalido(s)')

    iniciar_btn.configure(relief='flat', bg='white', bd=1, font='Segoe 10 bold', command=conectar)
    salir_btn.config(relief='flat', bg='white', bd=1, font='Segoe 10 bold', command=sys.exit)


def crear_tablas():
    try:
        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
        c = db.cursor()

        c.execute("CREATE DATABASE IF NOT EXISTS autotransportes_pantaco")

        c.execute("""CREATE TABLE IF NOT EXISTS Personal(
                        n_empleado SMALLINT UNSIGNED PRIMARY KEY,
                        nombres VARCHAR(20),
                        apellido1 VARCHAR(15),
                        apellido2 VARCHAR(15),
                        rfc VARCHAR(13),
                        correo VARCHAR(30),
                        tel VARCHAR(15),
                        id VARCHAR(15),
                        n_id VARCHAR(25),
                        vencimiento_id DATE,
                        imss VARCHAR(25),
                        alta DATE,
                        baja DATE,
                        tipo VARCHAR(10),
                        banco VARCHAR(20),
                        n_cuenta VARCHAR(20),  
                        domicilio VARCHAR(255)
                        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS Unidades(
                        n_economico SMALLINT UNSIGNED PRIMARY KEY,
                        n_motor VARCHAR(20),
                        placas VARCHAR(20),
                        modelo VARCHAR(20),
                        niv VARCHAR(20),
                        descripcion VARCHAR(255)                
                        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS Navieras(
                        n_naviera SMALLINT UNSIGNED PRIMARY KEY,
                        nombre VARCHAR(50),
                        rfc VARCHAR(13),
                        domicilio VARCHAR(255),
                        m_pago VARCHAR(20),
                        uso_cfdi varchar(20)
                        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS Clientes(
                        n_cliente SMALLINT UNSIGNED PRIMARY KEY,
                        nombre VARCHAR(50),
                        rfc VARCHAR(13),
                        domicilio VARCHAR(255),
                        m_pago VARCHAR(20),
                        uso_cfdi varchar(20)
                        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS Contenedores(
                        tipo VARCHAR(50) PRIMARY KEY,
                        ancho DECIMAL(5,2),
                        largo DECIMAL(5,2),
                        alto DECIMAL(5,2),
                        peso DECIMAL(5,2)
                        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS Mantenimiento(
                        id SMALLINT UNSIGNED,
                        n_economico SMALLINT UNSIGNED,
                        ubicacion VARCHAR(50),
                        fecha_inicio DATE,
                        fecha_cierre DATE,
                        descripcion VARCHAR(255),
                        costo DECIMAL(8,2),
                        PRIMARY KEY (id),
                        FOREIGN KEY (n_economico) REFERENCES Unidades(n_economico)
                        );""")

        c.execute("""CREATE TABLE IF NOT EXISTS Ciudades(
                        clave VARCHAR(5) PRIMARY KEY,
                        nombre VARCHAR(20),
                        estado VARCHAR(20)
                        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS Liquidaciones(
                        folio MEDIUMINT UNSIGNED PRIMARY KEY,
                        fecha_inicio DATE,
                        fecha_cierre DATE,
                        n_empleado SMALLINT UNSIGNED,
                        importe DECIMAL(6,2),
                        FOREIGN KEY (n_empleado) REFERENCES Personal(n_empleado)
                        );""")

        c.execute("""CREATE TABLE IF NOT EXISTS Comprobaciones(
                        concepto VARCHAR(20),
                        comprobado DECIMAL(8,2),
                        autorizado DECIMAL(8,2),
                        liquidacion MEDIUMINT UNSIGNED,
                        FOREIGN KEY (liquidacion) REFERENCES Liquidaciones(folio)
                        );""")

        c.execute("""CREATE TABLE IF NOT EXISTS Anticipos(
                        serie VARCHAR(3),
                        folio MEDIUMINT UNSIGNED,
                        fecha DATE,
                        liquidacion MEDIUMINT UNSIGNED,
                        n_empleado SMALLINT UNSIGNED,
                        n_economico SMALLINT UNSIGNED,
                        concepto VARCHAR(255),
                        importe DECIMAL(7,2),
                        PRIMARY KEY (serie, folio),
                        FOREIGN KEY (n_empleado) REFERENCES Personal(n_empleado),
                        FOREIGN KEY (liquidacion) REFERENCES Liquidaciones(folio)
                        );""")

        c.execute("""CREATE TABLE IF NOT EXISTS Facturas(
                        serie VARCHAR(3),
                        folio MEDIUMINT UNSIGNED,
                        fecha DATE,
                        receptor VARCHAR(50),
                        estatus VARCHAR(15),
                        total DECIMAL(8,2),
                        PRIMARY KEY (serie, folio)
                        );""")

        c.execute("""CREATE TABLE IF NOT EXISTS Ordenes(
                        serie VARCHAR(3),
                        folio MEDIUMINT UNSIGNED,
                        liquidacion MEDIUMINT UNSIGNED,
                        factura_serie VARCHAR(3),
                        factura_folio MEDIUMINT UNSIGNED,
                        fecha DATE,
                        n_empleado SMALLINT UNSIGNED,
                        ruta VARCHAR(20),
                        n_economico SMALLINT UNSIGNED,
                        distancia DECIMAL(7,2),
                        n_naviera SMALLINT UNSIGNED,
                        contenedor VARCHAR(15),
                        tamano VARCHAR(50),
                        tipo_servicio VARCHAR(15),
                        n_cliente SMALLINT UNSIGNED,
                        booking VARCHAR(20),
                        sello VARCHAR(20),
                        estatus VARCHAR(10),                    
                        notas VARCHAR(255),
                        peso DECIMAL(4,2),
                        origen VARCHAR(255),
                        consignatario VARCHAR(255),
                        destino VARCHAR(255),
                        flete DECIMAL(7,2),
                        maniobra DECIMAL(7,2),
                        almacenaje DECIMAL(8,2),
                        ffalso DECIMAL(7,2),
                        reexp DECIMAL(7,2),
                        difkm DECIMAL(7,2),
                        subtotal DECIMAL(7,2),
                        iva DECIMAL(7,2),
                        retencion DECIMAL(7,2),
                        total DECIMAL(8,2),
                        comision DECIMAL(7,2),
                        PRIMARY KEY (serie, folio),
                        FOREIGN KEY (liquidacion) REFERENCES Liquidaciones(folio),
                        FOREIGN KEY (factura_serie, factura_folio) REFERENCES Facturas(serie, folio),
                        FOREIGN KEY (n_empleado) REFERENCES Personal(n_empleado),
                        FOREIGN KEY (n_economico) REFERENCES Unidades(n_economico),
                        FOREIGN KEY (n_naviera) REFERENCES Navieras(n_naviera),
                        FOREIGN KEY (tamano) REFERENCES Contenedores(tipo),
                        FOREIGN KEY (n_cliente) REFERENCES Clientes(n_cliente)
                        );""")
        db.commit()
    finally:
        c.close()

# GENERACION DE GUI DE CATALOGOS

class Marco(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.configure(bd=1, relief='raised')

    def show(self):
        self.lift()


class Ordenes(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global pdf_img
        global guardar_img
        global cancelar_img

        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)
        pdf_icono = self.image2 = ImageTk.PhotoImage(pdf_img)

        titulo = tk.Label(self, text="Ordenes de Servicio", font='Segoe 12 bold')

        serie_lbl = tk.Label(self, text='Serie')
        serie_entry = tk.Entry(self, width=3)
        folio_lbl = tk.Label(self, text='Folio')
        folio_entry = tk.Entry(self, widt=5)
        serie_folio_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        liquidacion_lbl = tk.Label(self, text='Liquidación')
        liquidacion_entry = tk.Entry(self, width=5, state='readonly')
        facturas_lbl = tk.Label(self, text='Facturas')
        facturas_serie = tk.Entry(self, width=3, state='readonly')
        facturas_folio = tk.Entry(self, width=5, state='readonly')
        fecha_lbl = tk.Label(self, text='Fecha')
        fecha_entry = tk.Entry(self, width=10)
        fecha_entry.insert(0, date.today())

        operador_n_lbl = tk.Label(self, text='No. de Operador')
        operador_n_entry = tk.Entry(self, width=4)
        operador_box = ttk.Combobox(self, width=17)
        ruta_lbl = tk.Label(self, text='Ruta')
        ruta_entry = tk.Entry(self)
        unidad_lbl = tk.Label(self, text='Unidad')
        unidad_entry = tk.Entry(self, width=4)
        placas_lbl = tk.Label(self, text='Placas')
        placas = tk.Entry(self, width=12, state='readonly')
        distancia_lbl = tk.Label(self, text='Distancia (Km)')
        distancia_entry = tk.Entry(self, width=5)

        naviera_n_lbl = tk.Label(self, text='No. de Naviera')
        naviera_n_entry = tk.Entry(self, width=4)
        naviera_box = ttk.Combobox(self, width=17)
        contenedor_lbl = tk.Label(self, text='Contenedor')
        contenedor_entry = tk.Entry(self)
        tamano_lbl = tk.Label(self, text='Tamaño')
        tamano_box = ttk.Combobox(self, width=17, state='readonly')
        servicio_lbl = tk.Label(self, text='Tipo de Servicio')
        servicio_box = ttk.Combobox(self, width=17, values=('Importación', 'Exportación'))

        cliente_n_lbl = tk.Label(self, text='No. de Cliente')
        cliente_entry = tk.Entry(self, width=4)
        cliente_box = ttk.Combobox(self, width=17)
        booking_lbl = tk.Label(self, text='Booking / BL')
        booking_entry = tk.Entry(self)
        sello_lbl = tk.Label(self, text='Sello')
        sello_entry = tk.Entry(self)
        estatus_lbl = tk.Label(self, text='Estatus')
        estatus_entry = ttk.Combobox(self, width=17, values=('', 'Activo', 'Concluido', 'Cancelado'), state='readonly')

        notas_lbl = tk.Label(self, text='Notas')
        notas_entry = tk.Entry(self, width=30)
        peso_lbl = tk.Label(self, text='Peso (ton)')
        peso_entry = tk.Entry(self, width=6)

        origen_lbl = tk.Label(self, text='Origen')
        origen_txt = tk.Text(self, width=17, height=5)
        consignatario_lbl = tk.Label(self, text='Consignatario')
        consignatario_txt = tk.Text(self, width=17, height=5)
        destino_lbl = tk.Label(self, text='Destino')
        destino_txt = tk.Text(self, width=17, height=5)

        flete_lbl = tk.Label(self, text='Flete')
        maniobra_lbl = tk.Label(self, text='Maniobra')
        almacenaje_lbl = tk.Label(self, text='Almacenaje')
        ffalso_lbl = tk.Label(self, text='F. Falso')
        reexpedicion_lbl = tk.Label(self, text='Reexp')
        difkm_lbl = tk.Label(self, text='Dif Km')
        subtotal_lbl = tk.Label(self, text='Subtotal')
        iva_lbl = tk.Label(self, text='I.V.A.')
        retencion_lbl = tk.Label(self, text='Retención')
        total_lbl = tk.Label(self, text='Total')

        flete_entry = tk.Entry(self, width=9)
        maniobra_entry = tk.Entry(self, width=9)
        almacenaje_entry = tk.Entry(self, width=9)
        ffalso_entry = tk.Entry(self, width=9)
        reexpedicion_entry = tk.Entry(self, width=9)
        difkm_entry = tk.Entry(self, width=9)
        subtotal_entry = tk.Entry(self, width=9, state='readonly')
        iva_entry = tk.Entry(self, width=9, state='readonly')
        retencion_entry = tk.Entry(self, width=9, state='readonly')
        total_entry = tk.Entry(self, width=9, state='readonly')

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        serie_lbl.place(relx=1 / 24, rely=2 / 11)
        serie_entry.place(relx=2 / 24, rely=2 / 11)
        folio_lbl.place(relx=3 / 24, rely=2 / 11)
        folio_entry.place(relx=4 / 24, rely=2 / 11)
        serie_folio_btn.place(relx=5 / 24, rely=2 / 11)
        liquidacion_lbl.place(relx=8 / 24, rely=2 / 11)
        liquidacion_entry.place(relx=10 / 24, rely=2 / 11)
        facturas_lbl.place(relx=12 / 24, rely=2 / 11)
        facturas_serie.place(relx=13 / 24, rely=2 / 11)
        facturas_folio.place(relx=14 / 24, rely=2 / 11)
        fecha_lbl.place(relx=18 / 24, rely=2 / 11)
        fecha_entry.place(relx=19 / 24, rely=2 / 11)

        operador_n_lbl.place(relx=1 / 24, rely=3 / 11)
        operador_n_entry.place(relx=3 / 24, rely=3 / 11)
        operador_box.place(relx=4 / 24, rely=3 / 11)
        ruta_lbl.place(relx=7 / 24, rely=3 / 11)
        ruta_entry.place(relx=9 / 24, rely=3 / 11)
        unidad_lbl.place(relx=12 / 24, rely=3 / 11)
        unidad_entry.place(relx=13 / 24, rely=3 / 11)
        placas_lbl.place(relx=14 / 24, rely=3 / 11)
        placas.place(relx=15 / 24, rely=3 / 11)
        distancia_lbl.place(relx=17 / 24, rely=3 / 11)
        distancia_entry.place(relx=19 / 24, rely=3 / 11)

        naviera_n_lbl.place(relx=1 / 24, rely=4 / 11)
        naviera_n_entry.place(relx=3 / 24, rely=4 / 11)
        naviera_box.place(relx=4 / 24, rely=4 / 11)
        contenedor_lbl.place(relx=7 / 24, rely=4 / 11)
        contenedor_entry.place(relx=9 / 24, rely=4 / 11)
        tamano_lbl.place(relx=12 / 24, rely=4 / 11)
        tamano_box.place(relx=13 / 24, rely=4 / 11)
        servicio_lbl.place(relx=16 / 24, rely=4 / 11)
        servicio_box.place(relx=18 / 24, rely=4 / 11)

        cliente_n_lbl.place(relx=1 / 24, rely=5 / 11)
        cliente_entry.place(relx=3 / 24, rely=5 / 11)
        cliente_box.place(relx=4 / 24, rely=5 / 11)
        booking_lbl.place(relx=7 / 24, rely=5 / 11)
        booking_entry.place(relx=9 / 24, rely=5 / 11)
        sello_lbl.place(relx=12 / 24, rely=5 / 11)
        sello_entry.place(relx=13 / 24, rely=5 / 11)
        estatus_lbl.place(relx=16 / 24, rely=5 / 11)
        estatus_entry.place(relx=18 / 24, rely=5 / 11)

        notas_lbl.place(relx=1 / 24, rely=6 / 11)
        notas_entry.place(relx=3 / 24, rely=6 / 11)
        peso_lbl.place(relx=1 / 24, rely=7 / 11)
        peso_entry.place(relx=3 / 24, rely=7 / 11)
        origen_lbl.place(relx=7 / 24, rely=6 / 11)
        origen_txt.place(relx=8 / 24, rely=6 / 11)
        consignatario_lbl.place(relx=11 / 24, rely=6 / 11)
        consignatario_txt.place(relx=13 / 24, rely=6 / 11)
        destino_lbl.place(relx=16 / 24, rely=6 / 11)
        destino_txt.place(relx=18 / 24, rely=6 / 11)

        flete_entry.place(relx=1 / 24, rely=9 / 11)
        maniobra_entry.place(relx=3 / 24, rely=9 / 11)
        almacenaje_entry.place(relx=5 / 24, rely=9 / 11)
        ffalso_entry.place(relx=7 / 24, rely=9 / 11)
        reexpedicion_entry.place(relx=9 / 24, rely=9 / 11)
        difkm_entry.place(relx=11 / 24, rely=9 / 11)
        subtotal_entry.place(relx=13 / 24, rely=9 / 11)
        iva_entry.place(relx=15 / 24, rely=9 / 11)
        retencion_entry.place(relx=17 / 24, rely=9 / 11)
        total_entry.place(relx=19 / 24, rely=9 / 11)

        flete_lbl.place(relx=1 / 24, rely=9 / 12)
        maniobra_lbl.place(relx=3 / 24, rely=9 / 12)
        almacenaje_lbl.place(relx=5 / 24, rely=9 / 12)
        ffalso_lbl.place(relx=7 / 24, rely=9 / 12)
        reexpedicion_lbl.place(relx=9 / 24, rely=9 / 12)
        difkm_lbl.place(relx=11 / 24, rely=9 / 12)
        subtotal_lbl.place(relx=13 / 24, rely=9 / 12)
        iva_lbl.place(relx=15 / 24, rely=9 / 12)
        retencion_lbl.place(relx=17 / 24, rely=9 / 12)
        total_lbl.place(relx=19 / 24, rely=9 / 12)

        lista_btn = tk.Button(self, text='Lista de Ordenes')
        lista_btn.place(relx=1/50, rely=9/10)

        # DEFINICION DE BINDINGS PARA ENTRIES Y BOXES

        def focusout_operador_n(event):
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT  nombres, apellido1, apellido2
                        FROM Personal
                        WHERE n_empleado = %s"""

                c.execute(stmt, operador_n_entry.get())

                query = c.fetchone()

                operador_box.delete(0, tk.END)
                operador_box.insert(0, query[0] + ' ' + query[1] + ' ' + query[2])

            finally:
                c.close()

        def focusout_naviera_n(event):
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT  nombre
                        FROM Navieras
                        WHERE n_naviera = %s"""

                c.execute(stmt, naviera_n_entry.get())
                query = c.fetchone()
                naviera_box.delete(0, tk.END)
                naviera_box.insert(0, query[0])

            finally:
                c.close()

        def focusout_cliente_n(event):
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT  nombre
                        FROM Clientes
                        WHERE n_cliente = %s"""

                c.execute(stmt, cliente_entry.get())
                query = c.fetchone()
                cliente_box.delete(0, tk.END)
                cliente_box.insert(0, query[0])

            finally:
                c.close()

        def select_cliente(event):
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT  n_cliente
                        FROM Clientes
                        WHERE nombre = %s"""

                c.execute(stmt, cliente_box.get())
                query = c.fetchone()

                cliente_entry.delete(0, tk.END)
                cliente_entry.insert(0, query[0])

            finally:
                c.close()

        def select_naviera(event):
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT  n_naviera
                        FROM Navieras
                        WHERE nombre = %s"""

                c.execute(stmt, naviera_box.get())
                query = c.fetchone()

                naviera_n_entry.delete(0, tk.END)
                naviera_n_entry.insert(0, query[0])

            finally:
                c.close()

        def focusout_unidad(event):
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT  placas
                        FROM Unidades
                        WHERE n_economico = %s"""

                c.execute(stmt, unidad_entry.get())
                placas.configure(state='normal')
                placas.delete(0, tk.END)
                placas.insert(0, c.fetchone())
                placas.configure(state='readonly')

            finally:
                placas.configure(state='readonly')
                c.close()

        def focusout_flete(event):

            subtotal_entry.configure(state='normal')
            iva_entry.configure(state='normal')
            retencion_entry.configure(state='normal')
            total_entry.configure(state='normal')

            subtotal_entry.delete(0, tk.END)
            iva_entry.delete(0, tk.END)
            retencion_entry.delete(0, tk.END)
            total_entry.delete(0, tk.END)

            try:
                subtotal = (float(flete_entry.get()) + float(maniobra_entry.get()) + float(almacenaje_entry.get()) +
                            float(ffalso_entry.get()) + float(reexpedicion_entry.get()) + float(difkm_entry.get()))
                iva = subtotal * 0.16
                retencion = 0.04 * (float(ffalso_entry.get()) + float(flete_entry.get()) + float(reexpedicion_entry.get()) +
                                    float(difkm_entry.get()))
                total = subtotal + iva + retencion

                subtotal_entry.insert(0, round(subtotal, 2))
                iva_entry.insert(0, round(iva, 2))
                retencion_entry.insert(0, round(retencion, 2))
                total_entry.insert(0, total)

            except ValueError:
                pass

            finally:
                pass

            subtotal_entry.configure(state='readonly')
            iva_entry.configure(state='readonly')
            retencion_entry.configure(state='readonly')
            total_entry.configure(state='readonly')

        # ASIGNACION DE BINDINGS

        flete_entry.bind('<FocusOut>', focusout_flete)
        maniobra_entry.bind('<FocusOut>', focusout_flete)
        almacenaje_entry.bind('<FocusOut>', focusout_flete)
        ffalso_entry.bind('<FocusOut>', focusout_flete)
        reexpedicion_entry.bind('<FocusOut>', focusout_flete)
        difkm_entry.bind('<FocusOut>', focusout_flete)

        operador_n_entry.bind('<FocusOut>', focusout_operador_n)
        naviera_n_entry.bind('<FocusOut>', focusout_naviera_n)
        cliente_entry.bind('<FocusOut>', focusout_cliente_n)
        unidad_entry.bind('<FocusOut>', focusout_unidad)
        cliente_box.bind("<<ComboboxSelected>>", select_cliente)
        naviera_box.bind("<<ComboboxSelected>>", select_naviera)

        # FUNCION DE GENERAR PDF

        def pdf_gen():
            orden = Canvas('orden.pdf', pagesize=LETTER)

            orden.setFont('Helvetica-Bold', 18)
            orden.drawCentredString(305, 760, 'AUTOTRANSPORTES PANTACO S.A. DE C.V.')

            orden.setFont('Helvetica-Bold', 12)
            orden.drawCentredString(305, 740, 'R.F.C.: APA140923B23')

            orden.setFont('Helvetica', 6)
            orden.roundRect(5, 5, 603, 40, radius=3)
            orden.drawString(5, 26, '||1.1|9BB8EEEB-BD55-4FA7-BBF2-152D0D158408|2020-08-03T13:56:48|SAT970701NN3|Qw1KSFiN7OI/xaHK1soJZY9/n8WfT37u7EDXs563G4We64gRnx9kZ3t6fMN1gCQApcobPxEzbepdqz3Jk9flVFZdJp+uc6YTBI+z1nT/A')
            orden.drawString(5, 16, 'Yoo5KQ8Qk4Zmy0PpFkc2cpJzIm1dLRf3QWHEyg6GOuewOYpiuEN18FrLVf8U1iIpdZ7jDe8LeAYJU4IfuFBvbeLD1zmUdX0PIoyHaeJuZGdrBg024+J1f3T1l3MX4sQZXUnsok07oeoNOcu3jTB6aNCavMAuxUB5/DhiZNdI5S0Gac7')
            orden.drawString(5, 6, '7laT4dY9TKZPjo7voN4MSv5BC32VuV19If19OVy1K/y8sa0SzlDdyDModp4G3w==|00001000000504465028||')

            orden.setFont('Helvetica', 8)
            orden.drawString(5, 35, 'Cadena Original del complemento de certificación digital del SAT:')

            orden.setFillColor('#ffcc66')
            orden.roundRect(5, 95, 603, 12, radius=3, fill=1)
            orden.roundRect(5, 243, 603, 24, radius=3, fill=1)
            orden.roundRect(5, 443, 603, 24, radius=3, fill=1)
            orden.roundRect(5, 627, 603, 24, radius=3, fill=1)
            orden.roundRect(5, 651, 70, 12, radius=3, fill=1)
            orden.roundRect(457.25, 651, 76, 12, radius=3, fill=1)
            orden.roundRect(507, 762.75, 101, 25.25, radius=3, fill=1)
            orden.roundRect(507, 712.25, 101, 25.25, radius=3, fill=1)

            orden.setFillColor('#000000')

            orden.roundRect(5, 5, 603, 783, radius=3)

            orden.roundRect(5, 45, 201, 50, radius=3)
            orden.drawCentredString(103, 84, 'NOMBRE DEL OPERADOR')
            orden.drawCentredString(103, 65, '%s' % operador_box.get())

            orden.roundRect(206, 45, 201, 50, radius=3)
            orden.drawCentredString(305, 84, 'ECONÓMICO')
            orden.drawCentredString(305, 65, '%s' % unidad_entry.get())

            orden.roundRect(407, 45, 201, 50, radius=3)
            orden.drawCentredString(506, 84, 'PLACAS')
            orden.drawCentredString(506, 65, '%s' % placas.get())

            orden.roundRect(5, 5, 603, 90, radius=3)
            orden.drawCentredString(305, 97, 'ASIGNACIÓN DEL SERVICIO')

            orden.roundRect(5, 107, 603, 136, radius=3)

            orden.roundRect(5, 107, 295, 136, radius=3)
            orden.roundRect(5, 107, 295, 34, radius=3)
            orden.drawCentredString(150, 232, 'NOMBRE')
            orden.roundRect(5, 141, 295, 34, radius=3)
            orden.drawCentredString(150, 198, 'FRIMA')
            orden.roundRect(5, 175, 295, 34, radius=3)
            orden.drawCentredString(150, 164, 'FECHA Y HORA DE ENTRADA')
            orden.roundRect(5, 209, 295, 34, radius=3)
            orden.drawCentredString(150, 130, 'FECHA Y HORA DE SALIDA')

            orden.roundRect(300, 107, 175, 136, radius=3)
            orden.drawCentredString(387.5, 230, 'SELLO DE PLANTA')

            orden.roundRect(475, 107, 133, 136, radius=3)
            orden.drawImage('qr_code.jpeg', 476, 109, 130, 130)

            orden.drawCentredString(305, 254, 'ACUSE DE RECIBO DE MERCANCIA')

            orden.roundRect(5, 267, 603, 176, radius=3)

            orden.roundRect(5, 267, 470, 106, radius=3)
            orden.drawCentredString(240, 361, 'MERCANCIA INCRIPTADA SEGÚN PEDIMENTO SAT')
            orden.drawCentredString(240, 320, 'FLETE LIBRE A BORDO Y SIN MANIOBRAS')
            orden.drawCentredString(240, 279,
                                    'PESO MÁXIMO 19 TONELADAS + TARA SEGÚN NOM 012-SCT *EVITE PROBLEMAS CON SCT*')

            orden.roundRect(5, 373, 470, 70, radius=3)
            orden.drawString(8, 431, '%s' % contenedor_entry.get())
            orden.drawString(8, 419, '%s %s' % (tamano_box.get(), naviera_box.get()))
            orden.drawString(8, 407, 'Booking / BL: %s' % booking_entry.get())
            orden.drawString(8, 395, 'Sello: %s' % sello_entry.get())
            orden.drawString(8, 383, '%s' % notas_entry.get())

            orden.roundRect(475, 267, 133, 176, radius=3)
            orden.roundRect(475, 267, 75, 176, radius=3)
            orden.roundRect(550, 267, 58, 176, radius=3)

            orden.roundRect(475, 267, 133, 17.6, radius=3)
            orden.drawString(479, 272, 'TOTAL')
            orden.drawString(554, 272, '$ %s' % total_entry.get())

            orden.roundRect(475, 284.6, 133, 17.6, radius=3)
            orden.drawString(479, 289.6, 'RET 4%')
            orden.drawString(554, 289.6, '$ %s' % retencion_entry.get())

            orden.roundRect(475, 302.2, 133, 17.6, radius=3)
            orden.drawString(479, 307.2, 'I.V.A. %16')
            orden.drawString(554, 307.2, '$ %s' % iva_entry.get())

            orden.roundRect(475, 319.8, 133, 17.6, radius=3)
            orden.drawString(479, 324.8, 'SUBTOTAL')
            orden.drawString(554, 324.8, '$ %s' % subtotal_entry.get())

            orden.roundRect(475, 337.4, 133, 17.6, radius=3)
            orden.drawString(479, 342.4, 'DIF. KM.')
            orden.drawString(554, 342.4, '$ %s' % difkm_entry.get())

            orden.roundRect(475, 355, 133, 17.6, radius=3)
            orden.drawString(479, 360, 'REEXPEDICIÓN')
            orden.drawString(554, 360, '$ %s' % reexpedicion_entry.get())

            orden.roundRect(475, 372.6, 133, 17.6, radius=3)
            orden.drawString(479, 377.6, 'F. FALSO')
            orden.drawString(554, 377.6, '$ %s' % ffalso_entry.get())

            orden.roundRect(475, 390.2, 133, 17.6, radius=3)
            orden.drawString(479, 395.2, 'ALMACENAJE')
            orden.drawString(554, 395.2, '$ %s' % almacenaje_entry.get())

            orden.roundRect(475, 407.8, 133, 17.6, radius=3)
            orden.drawString(479, 412.8, 'MANIOBRA')
            orden.drawString(554, 412.8, '$ %s' % maniobra_entry.get())

            orden.roundRect(475, 425.4, 133, 17.6, radius=3)
            orden.drawString(479, 430.4, 'FLETE')
            orden.drawString(554, 430.4, '$ %s' % flete_entry.get())

            orden.drawCentredString(240, 452, 'DETALLES DE LA CARGA')

            i = 0
            for renglon in (origen_txt.get(1.0, 'end-1c')).split('\n', 100):
                orden.drawCentredString(82.875, 607 - i, '%s' % renglon)
                i = i + 10

            i = 0
            for renglon in (consignatario_txt.get(1.0, 'end-1c')).split('\n', 100):
                orden.drawCentredString(306.5, 607 - i, '%s' % renglon)
                i = i + 10

            i = 0
            for renglon in (destino_txt.get(1.0, 'end-1c')).split('\n', 100):
                orden.drawCentredString(532.625, 607 - i, '%s' % renglon)
                i = i + 10

            orden.roundRect(5, 467, 603, 160, radius=3)

            orden.roundRect(155.75, 467, 301.5, 160, radius=3)
            orden.roundRect(457.25, 467, 150.75, 160, radius=3)

            orden.drawCentredString(82.875, 634, ' ORIGEN')
            orden.drawCentredString(306.5, 634, ' CONSIGNATARIO')
            orden.drawCentredString(532.625, 634, 'DESTINO / AGENCIA ADUANAL')

            orden.drawString(25, 654, 'RUTA')
            orden.roundRect(75, 651, 533, 12, radius=3)
            orden.drawString(80, 654, '%s' % ruta_entry.get())

            orden.roundRect(457.25, 651, 150.75, 12, radius=3)

            orden.drawString(459, 654, 'TIPO DE SERVICIO')
            orden.roundRect(533.25, 651, 74.75, 12, radius=3)
            orden.drawCentredString(570.625, 654, '%s' % servicio_box.get())

            orden.setFont('Helvetica-Bold', 12)
            orden.roundRect(5, 663, 603, 24, radius=3)
            orden.drawCentredString(305, 670, '%s' % naviera_box.get())

            orden.setFont('Helvetica', 8)
            orden.roundRect(5, 687, 101, 101, radius=3)
            orden.drawImage('logo.jpg', 7, 689, width=98, height=98)

            orden.roundRect(106, 687, 401, 101, radius=3)

            orden.roundRect(507, 687, 101, 50.5, radius=3)
            orden.roundRect(507, 687, 101, 25.25, radius=3)
            orden.drawCentredString(557.5, 700, '%s' % fecha_entry.get())

            orden.drawCentredString(557.5, 725, 'FECHA')

            orden.roundRect(507, 737.5, 101, 25.25, radius=3)
            orden.drawCentredString(557.5, 750, '%s - %s' % (serie_entry.get(), folio_entry.get()))

            orden.drawCentredString(557.5, 775, 'FOLIO')

            orden.drawCentredString(305, 720, 'AV. GRANJAS #113 COL. JARDÍN AZPEITIA DEL. AZCAPOTZALCO CDMX,'
                                              ' CP. 02530 TEL. 55-2631-6615')

            orden.save()
            startfile('orden.pdf')

        # FUNCIONES SELECCIONAR GUARDAR Y CANCELAR

        def poblar_operador_box():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT nombres, apellido1, apellido2
                            FROM Personal
                            WHERE tipo = 'operador'
                            Order BY nombres ASC""")

                query = c.fetchall()

                operadores = []
                i = 0
                for operador in query:
                    operadores.append(query[i][0] + ' ' + query[i][1] + ' ' + query[i][2])
                    i += 1

                operador_box.config(values=operadores)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            except TypeError:
                pass

            finally:
                c.close

        def poblar_navieras_box():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT nombre
                            FROM Navieras
                            ORDER BY nombre ASC""")

                query = c.fetchall()

                navieras = []
                i = 0
                for naviera in query:
                    navieras.append(query[i][0])
                    i += 1

                naviera_box.config(values=navieras)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close

        def poblar_tamano_box():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT tipo
                            FROM Contenedores
                            ORDER BY tipo ASC""")

                query = c.fetchall()

                tipos = []
                i = 0

                for contenedor in query:
                    tipos.append(query[i][0])
                    i += 1

                tamano_box.config(values=tipos)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close

        def poblar_clientes_box():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT nombre
                            FROM Clientes
                            ORDER BY nombre ASC""")

                query = c.fetchall()

                clientes = []
                i = 0
                for cliente in query:
                    clientes.append(query[i][0])
                    i += 1

                cliente_box.config(values=clientes)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def insertar_siguiente():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()
                c.execute("""SELECT serie, folio
                            FROM Ordenes
                            ORDER BY folio DESC
                            LIMIT 1""")

                query = c.fetchone()

                serie_entry.insert(0, query[0])
                folio_entry.insert(0, query[1]+1)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def cancelar():

            subtotal_entry.configure(state='normal')
            iva_entry.configure(state='normal')
            retencion_entry.configure(state='normal')
            total_entry.configure(state='normal')
            serie_entry.delete(0, tk.END)
            folio_entry.delete(0, tk.END)
            liquidacion_entry.configure(state='normal')
            liquidacion_entry.delete(0, tk.END)
            liquidacion_entry.configure(state='readonly')
            facturas_serie.configure(state='normal')
            facturas_folio.configure(state='normal')
            facturas_serie.delete(0, tk.END)
            facturas_folio.delete(0, tk.END)
            facturas_serie.configure(state='readonly')
            facturas_folio.configure(state='readonly')
            fecha_entry.delete(0, tk.END)
            operador_n_entry.delete(0, tk.END)
            operador_box.delete(0, tk.END)
            unidad_entry.delete(0, tk.END)
            placas.configure(state='normal')
            placas.delete(0, tk.END)
            placas.configure(state='readonly')
            naviera_n_entry.delete(0, tk.END)
            naviera_box.delete(0, tk.END)
            cliente_entry.delete(0, tk.END)
            cliente_box.delete(0, tk.END)
            ruta_entry.delete(0, tk.END)
            contenedor_entry.delete(0, tk.END)
            servicio_box.delete(0, tk.END)
            booking_entry.delete(0, tk.END)
            sello_entry.delete(0, tk.END)
            distancia_entry.delete(0, tk.END)
            peso_entry.delete(0, tk.END)
            tamano_box.config(state='normal')
            tamano_box.delete(0, tk.END)
            tamano_box.config(state='readonly')
            origen_txt.delete(1.0, tk.END)
            consignatario_txt.delete(1.0, tk.END)
            destino_txt.delete(1.0, tk.END)
            notas_entry.delete(0, tk.END)
            flete_entry.delete(0, tk.END)
            maniobra_entry.delete(0, tk.END)
            almacenaje_entry.delete(0, tk.END)
            ffalso_entry.delete(0, tk.END)
            reexpedicion_entry.delete(0, tk.END)
            difkm_entry.delete(0, tk.END)
            subtotal_entry.delete(0, tk.END)
            iva_entry.delete(0, tk.END)
            retencion_entry.delete(0, tk.END)
            total_entry.delete(0, tk.END)
            fecha_entry.insert(0, date.today())
            subtotal_entry.configure(state='readonly')
            iva_entry.configure(state='readonly')
            retencion_entry.configure(state='readonly')
            total_entry.configure(state='readonly')

            insertar_siguiente()

        # TODO BUSCAR FOLIOS DE LIQUIDACIONES Y FACTURAS

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT fecha, n_empleado, ruta, n_economico, distancia, n_naviera, contenedor, tamano, 
                                    tipo_servicio, n_cliente, booking, sello, estatus, notas, peso, origen, 
                                    consignatario, destino, flete, maniobra, almacenaje, ffalso, reexp, difkm, subtotal, 
                                    iva, retencion, total
                        FROM Ordenes
                        WHERE serie= %s AND folio= %s"""
                c.execute(stmt, (serie_entry.get(), folio_entry.get()))
                query = c.fetchone()

                lista = []
                for item in query:
                    if item is None:
                        item = str('')
                    lista.append(item)

                subtotal_entry.configure(state='normal')
                iva_entry.configure(state='normal')
                retencion_entry.configure(state='normal')
                total_entry.configure(state='normal')

                fecha_entry.delete(0, tk.END)
                operador_n_entry.delete(0, tk.END)
                ruta_entry.delete(0, tk.END)
                unidad_entry.delete(0, tk.END)
                distancia_entry.delete(0, tk.END)
                naviera_n_entry.delete(0, tk.END)
                contenedor_entry.delete(0, tk.END)
                tamano_box.config(state='normal')
                tamano_box.delete(0, tk.END)
                servicio_box.delete(0, tk.END)
                cliente_entry.delete(0, tk.END)
                booking_entry.delete(0, tk.END)
                sello_entry.delete(0, tk.END)
                estatus_entry.delete(0, tk.END)
                notas_entry.delete(0, tk.END)
                peso_entry.delete(0, tk.END)
                origen_txt.delete(1.0, tk.END)
                consignatario_txt.delete(1.0, tk.END)
                destino_txt.delete(1.0, tk.END)
                flete_entry.delete(0, tk.END)
                maniobra_entry.delete(0, tk.END)
                almacenaje_entry.delete(0, tk.END)
                ffalso_entry.delete(0, tk.END)
                reexpedicion_entry.delete(0, tk.END)
                difkm_entry.delete(0, tk.END)
                subtotal_entry.delete(0, tk.END)
                iva_entry.delete(0, tk.END)
                retencion_entry.delete(0, tk.END)
                total_entry.delete(0, tk.END)

                fecha_entry.insert(0, lista[0])
                operador_n_entry.insert(0, lista[1])
                ruta_entry.insert(0, lista[2])
                unidad_entry.insert(0, lista[3])
                distancia_entry.insert(0, lista[4])
                naviera_n_entry.insert(0, lista[5])
                contenedor_entry.insert(0, lista[6])
                tamano_box.insert(0, lista[7])
                tamano_box.config(state='readonly')
                servicio_box.insert(0, lista[8])
                cliente_entry.insert(0, lista[9])
                booking_entry.insert(0, lista[10])
                sello_entry.insert(0, lista[11])
                estatus_entry.insert(0, lista[12])
                notas_entry.insert(0, lista[13])
                peso_entry.insert(0, lista[14])
                origen_txt.insert(1.0, lista[15])
                consignatario_txt.insert(1.0, lista[16])
                destino_txt.insert(1.0, lista[17])
                flete_entry.insert(0, lista[18])
                maniobra_entry.insert(0, lista[19])
                almacenaje_entry.insert(0, lista[20])
                ffalso_entry.insert(0, lista[21])
                reexpedicion_entry.insert(0, lista[22])
                difkm_entry.insert(0, lista[23])
                subtotal_entry.insert(0, lista[24])
                iva_entry.insert(0, lista[25])
                retencion_entry.insert(0, lista[26])
                total_entry.insert(0, lista[27])

                subtotal_entry.configure(state='readonly')
                iva_entry.configure(state='readonly')
                retencion_entry.configure(state='readonly')
                total_entry.configure(state='readonly')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT liquidacion
                        FROM Ordenes
                        WHERE serie = %s and folio = %s"""
                c.execute(stmt, (serie_entry.get(), folio_entry.get()))
                query = c.fetchone()
                liquidacion_entry.configure(state='normal')
                liquidacion_entry.delete(0, tk.END)
                if query[0] is not None:
                    liquidacion_entry.insert(0, query[0])

            finally:
                liquidacion_entry.configure(state='readonly')
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT factura_serie, factura_folio
                        FROM Ordenes
                        WHERE serie = %s and folio = %s"""
                c.execute(stmt, (serie_entry.get(), folio_entry.get()))

                query = c.fetchone()

                facturas_serie.configure(state='normal')
                facturas_folio.configure(state='normal')
                facturas_serie.delete(0, tk.END)
                facturas_folio.delete(0, tk.END)
                facturas_serie.insert(0, query[0])
                facturas_folio.insert(0, query[1])

            finally:
                facturas_serie.configure(state='readonly')
                facturas_folio.configure(state='readonly')
                c.close()

        def abrir_lista():

            ventana_lista = tk.Toplevel()
            ventana_lista.minsize(width=1000, height=600)
            ventana_lista.maxsize(width=1000, height=600)

            busqueda_frame = tk.Frame(ventana_lista)
            busqueda_frame.pack(pady=10)

            lista_frame = tk.Label(ventana_lista)
            lista_frame.pack()

            criterios_lbl = tk.Label(busqueda_frame, text='Criterio de Busqueda:')
            criterios_lbl.grid(column=0, row=0)

            criterios_busqueda_box = ttk.Combobox(busqueda_frame)
            criterios_busqueda_box.grid(column=1, row=0)

            buscar_lbl = tk.Label(busqueda_frame, text='Buscar:')
            buscar_lbl.grid(column=2, row=0, padx=(10, 0))

            buscar_entry = tk.Entry(busqueda_frame)
            buscar_entry.grid(column=3, row=0)

            scroll0 = tk.Scrollbar(ventana_lista, orient='horizontal')
            scroll0.pack(fill='x')

            lista_busqueda = ttk.Treeview(lista_frame, height=5, xscrollcommand=scroll0.set)
            lista_busqueda.pack()

            tabla_frame = tk.Frame(ventana_lista)
            tabla_frame.pack()

            scrollbar = tk.Scrollbar(ventana_lista, orient='horizontal')
            scrollbar.pack(side='bottom', fill='x')

            lista = ttk.Treeview(tabla_frame, height=15, xscrollcommand=scrollbar.set)
            lista.pack(padx=10, pady=10)

            scroll0.configure(command=lista_busqueda.xview)
            scrollbar.configure(command=lista.xview)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute('DESCRIBE Ordenes')
                query = c.fetchall()

                columnas = []
                for campo in query:
                    columnas.append(campo[0])

                criterios_busqueda_box.configure(values=columnas, state='readonly')

                lista_busqueda.configure(columns=columnas)
                lista_busqueda['show'] = 'headings'

                lista.configure(columns=columnas)
                lista['show'] = 'headings'

                for columna in columnas:
                    lista.heading(columna, text=columna)
                    lista.column(columna, minwidth=100, width=100, stretch='no')
                    lista_busqueda.heading(columna, text=columna)
                    lista_busqueda.column(columna, minwidth=100, width=100, stretch='no')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                            FROM Ordenes
                            ORDER BY folio DESC""")
                query = c.fetchall()

                for fila in query:
                    lista.insert("", 'end', values=fila)

            finally:
                c.close()

            def release_busqueda(event):
                try:
                    lista_busqueda.delete(*lista_busqueda.get_children())

                finally:
                    pass

                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    c.execute("SELECT * FROM Ordenes WHERE " + criterios_busqueda_box.get() + "= " + "'" +
                              buscar_entry.get() + "'" + "")

                    query = c.fetchall()

                    for renglon in query:
                        lista_busqueda.insert("", 'end', values=renglon)

                finally:
                    c.close()

            def click_header(event):

                n_columna = lista.identify_column(event.x).replace('#', '')

                if lista.identify('region', event.x, event.y) == 'heading':
                    try:
                        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                        c = db.cursor()

                        c.execute("SELECT * FROM Ordenes ORDER BY " + columnas[int(n_columna)-1] + " DESC")

                        query = c.fetchall()

                        lista.delete(*lista.get_children())

                        for renglon in query:
                            lista.insert("", 'end', values=renglon)

                    finally:
                        c.close()

            def pdf_busqueda():

                busqueda = Canvas('busqueda.pdf', pagesize=landscape(LEGAL))
                busqueda.setFont('Helvetica', 7)
                x = 8
                for columna in columnas:
                    busqueda.drawString(x, 600, columna)
                    x += 50

                x = 8
                y = 590
                for fila in lista_busqueda.get_children():
                    for columna in lista_busqueda.item(fila)['values']:
                        busqueda.drawString(x, y, str(columna))
                        x += 50
                    x = 8
                    y += -10

                busqueda.save()
                startfile('busqueda.pdf')

            pdf_btn2 = tk.Button(lista_frame, text='.PDF', image=pdf_icono, command=pdf_busqueda)
            pdf_btn2.pack(pady=5)
            buscar_entry.bind('<Return>', release_busqueda)
            lista.bind('<Button-1>', click_header)

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT serie, folio
                        FROM Ordenes 
                        WHERE serie= %s AND folio= %s"""

                c.execute(stmt, (serie_entry.get(), int(folio_entry.get())))
                query = c.fetchone()
                c.close()

                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                lista0 = [fecha_entry.get(), operador_n_entry.get(), ruta_entry.get(), unidad_entry.get(),
                         distancia_entry.get(), naviera_n_entry.get(), contenedor_entry.get(), tamano_box.get(),
                         servicio_box.get(), cliente_entry.get(), booking_entry.get(), sello_entry.get(),
                         estatus_entry.get(), notas_entry.get(), peso_entry.get(), origen_txt.get(1.0, tk.END),
                         consignatario_txt.get(1.0, tk.END), destino_txt.get(1.0, tk.END), flete_entry.get(),
                         maniobra_entry.get(), almacenaje_entry.get(), ffalso_entry.get(), reexpedicion_entry.get(),
                         difkm_entry.get(), subtotal_entry.get(), iva_entry.get(), retencion_entry.get(),
                         total_entry.get()]

                lista1 = []
                for entry in lista0:
                    if entry == '' or entry == '\n':
                        entry = None
                    lista1.append(entry)

                if query is not None and query[0] == serie_entry.get() and query[1] == int(folio_entry.get()):

                    mensaje = messagebox.askyesno('Orden Existe', 'La orden %s - %s ya existe. '
                                                                  '¿Desea guardar los cambios?'
                                                  % (serie_entry.get(), folio_entry.get()))
                    if mensaje is True:
                        try:

                            stmt = """UPDATE Ordenes
                                    SET fecha = %s,
                                        n_empleado = %s,
                                        ruta = %s,
                                        n_economico= %s,
                                        distancia = %s,
                                        n_naviera = %s,
                                        contenedor = %s,
                                        tamano = %s,
                                        tipo_servicio = %s,
                                        n_cliente = %s,
                                        booking = %s,
                                        sello = %s,
                                        estatus = %s,
                                        notas = %s,
                                        peso = %s,
                                        origen = %s,
                                        consignatario = %s,
                                        destino = %s,
                                        flete = %s,
                                        maniobra = %s,
                                        almacenaje = %s,
                                        ffalso = %s,
                                        reexp = %s,
                                        difkm = %s,
                                        subtotal = %s,
                                        iva = %s,
                                        retencion = %s,
                                        total = %s
                                    WHERE serie = %s AND folio= %s"""

                            c.execute(stmt, (lista1[0], lista1[1], lista1[2], lista1[3], lista1[4], lista1[5],
                                             lista1[6], lista1[7], lista1[8], lista1[9], lista1[10], lista1[11],
                                             lista1[12], lista1[13], lista1[14], lista1[15], lista1[16], lista1[17],
                                             lista1[18], lista1[19], lista1[20], lista1[21], lista1[22], lista1[23],
                                             lista1[24], lista1[25], lista1[26], lista1[27], serie_entry.get(),
                                             folio_entry.get()))
                            db.commit()
                            cancelar()

                        finally:
                            c.close()

                else:
                    mensaje = messagebox.askyesno('Orden Inexistente', 'La orden %s - %s no existe. '
                                                                           '¿Desea darla de alta?'
                                                      % (serie_entry.get(), folio_entry.get()))
                    if mensaje is True:
                        try:

                            stmt = """INSERT INTO Ordenes (serie, folio, fecha, n_empleado, ruta, n_economico, 
                                                            distancia, n_naviera, contenedor, tamano, tipo_servicio, 
                                                            n_cliente, booking, sello, estatus, notas, peso, origen, 
                                                            consignatario, destino, flete, maniobra, almacenaje, 
                                                            ffalso, reexp, difkm, subtotal, iva, retencion, total)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                %s,%s,%s,%s)"""

                            c.execute(stmt, (serie_entry.get(), folio_entry.get(), lista1[0], lista1[1], lista1[2],
                                             lista1[3], lista1[4], lista1[5], lista1[6], lista1[7], lista1[8], lista1[9]
                                             , lista1[10], lista1[11], lista1[12], lista1[13], lista1[14], lista1[15],
                                             lista1[16], lista1[17], lista1[18], lista1[19], lista1[20], lista1[21],
                                             lista1[22], lista1[23], lista1[24], lista1[25], lista1[26], lista1[27]))

                            db.commit()
                            cancelar()

                        finally:
                            c.close()

            finally:
                db.commit()
                c.close()

        # LLAMMAR FUNCIONES DE POBLAR COMBOBOXES

        insertar_siguiente()
        poblar_operador_box()
        poblar_navieras_box()
        poblar_clientes_box()
        poblar_tamano_box()

        lista_btn.configure(relief='flat', bg='white', bd=1, command=abrir_lista)
        serie_folio_btn.configure(relief='flat', bg='white', bd=1, command=seleccionar)

        pdf_btn = tk.Button(self, text='.PDF', image=pdf_icono, command=pdf_gen)
        pdf_btn.place(relx=8 / 16, rely=12 / 13, anchor='center')

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        serie_folio_btn.configure(command=seleccionar)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Navieras(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        titulo = tk.Label(self, text="Navieras", font='Segoe 12 bold')

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        naviera_n_lbl = tk.Label(self, text='No. de Naviera')
        naviera_n_entry = tk.Entry(self, width=4)
        naviera_lbl = tk.Label(self, text='Naviera')
        naviera_box = ttk.Combobox(self, width=17)

        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)

        rfc_lbl = tk.Label(self, text='R.F.C.')
        rfc_entry = tk.Entry(self)

        uso_cfdi_lbl = tk.Label(self, text='Uso de CFDI')
        uso_cfdi_box = ttk.Combobox(self)

        metodo_pago_lbl = tk.Label(self, text='Metodo de Pago')
        metodo_pago_box = ttk.Combobox(self)

        domicilio_lbl = tk.Label(self, text='Domicilio')
        domicilio_entry = tk.Text(self, height=5, width=25)

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        naviera_n_lbl.place(relx=4 / 24, rely=2 / 11)
        naviera_n_entry.place(relx=6 / 24, rely=2 / 11)
        naviera_lbl.place(relx=7 / 24, rely=2 / 11)
        naviera_box.place(relx=8 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=11 / 24, rely=2 / 11)

        rfc_lbl.place(relx=4 / 24, rely=3 / 11)
        rfc_entry.place(relx=6 / 24, rely=3 / 11)
        uso_cfdi_lbl.place(relx=9 / 24, rely=3 / 11)
        uso_cfdi_box.place(relx=11 / 24, rely=3 / 11)
        metodo_pago_lbl.place(relx=14 / 24, rely=3 / 11)
        metodo_pago_box.place(relx=16 / 24, rely=3 / 11)

        domicilio_lbl.place(relx=4 / 24, rely=4 / 11)
        domicilio_entry.place(relx=6 / 24, rely=4 / 11)

        lista_btn = tk.Button(self, text='Lista de Navieras')
        lista_btn.place(relx=1 / 50, rely=9 / 10)

        # FUNCIONES SELECCIONAR GUARDAR Y CANCELAR

        def abrir_lista():

            ventana_lista = tk.Toplevel()
            ventana_lista.minsize(width=1000, height=610)
            ventana_lista.maxsize(width=1000, height=610)

            busqueda_frame = tk.Frame(ventana_lista)
            busqueda_frame.pack(pady=10)

            lista_frame = tk.Label(ventana_lista)
            lista_frame.pack()

            criterios_lbl = tk.Label(busqueda_frame, text='Criterio de Busqueda:')
            criterios_lbl.grid(column=0, row=0)

            criterios_busqueda_box = ttk.Combobox(busqueda_frame)
            criterios_busqueda_box.grid(column=1, row=0)

            buscar_lbl = tk.Label(busqueda_frame, text='Buscar:')
            buscar_lbl.grid(column=2, row=0, padx=(10, 0))

            buscar_entry = tk.Entry(busqueda_frame)
            buscar_entry.grid(column=3, row=0)

            scroll0 = tk.Scrollbar(ventana_lista, orient='horizontal')
            scroll0.pack(fill='x')

            lista_busqueda = ttk.Treeview(lista_frame, height=5, xscrollcommand=scroll0.set)
            lista_busqueda.pack()

            tabla_frame = tk.Frame(ventana_lista)
            tabla_frame.pack()

            scrollbar = tk.Scrollbar(ventana_lista, orient='horizontal')
            scrollbar.pack(side='bottom', fill='x')

            lista = ttk.Treeview(tabla_frame, height=15, xscrollcommand=scrollbar.set)
            lista.pack(padx=10, pady=10)

            scroll0.configure(command=lista_busqueda.xview)
            scrollbar.configure(command=lista.xview)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute('DESCRIBE Navieras')
                query = c.fetchall()

                columnas = []
                for campo in query:
                    columnas.append(campo[0])

                criterios_busqueda_box.configure(values=columnas, state='readonly')

                lista_busqueda.configure(columns=columnas)
                lista_busqueda['show'] = 'headings'

                lista.configure(columns=columnas)
                lista['show'] = 'headings'

                for columna in columnas:
                    lista.heading(columna, text=columna)
                    lista.column(columna, minwidth=100, width=100, stretch='no')
                    lista_busqueda.heading(columna, text=columna)
                    lista_busqueda.column(columna, minwidth=100, width=100, stretch='no')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                            FROM Navieras
                            ORDER BY n_naviera DESC""")
                query = c.fetchall()

                for fila in query:
                    lista.insert("", 'end', values=fila)

            finally:
                c.close()

            def release_busqueda(event):
                try:
                    lista_busqueda.delete(*lista_busqueda.get_children())

                finally:
                    pass

                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    c.execute("SELECT * FROM Navieras WHERE " + criterios_busqueda_box.get() + "= " + "'" +
                              buscar_entry.get() + "'" + "")

                    query = c.fetchall()

                    for renglon in query:
                        lista_busqueda.insert("", 'end', values=renglon)

                finally:
                    c.close()

            def click_header(event):

                n_columna = lista.identify_column(event.x).replace('#', '')

                if lista.identify('region', event.x, event.y) == 'heading':
                    try:
                        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                        c = db.cursor()

                        c.execute("SELECT * FROM Navieras ORDER BY " + columnas[int(n_columna) - 1] + " DESC")

                        query = c.fetchall()

                        lista.delete(*lista.get_children())

                        for renglon in query:
                            lista.insert("", 'end', values=renglon)

                    finally:
                        c.close()

            def pdf_busqueda():

                busqueda = Canvas('busqueda.pdf', pagesize=LETTER)
                busqueda.setFont('Helvetica', 8)
                x = 8
                for columna in columnas:
                    busqueda.drawString(x, 760, columna)
                    x += 80

                x = 8
                y = 750
                for fila in lista_busqueda.get_children():
                    for columna in lista_busqueda.item(fila)['values']:
                        busqueda.drawString(x, y, str(columna))
                        x += 80
                    x = 8
                    y += -10

                busqueda.save()
                startfile('busqueda.pdf')

            global pdf_img
            pdf_icono = self.image2 = ImageTk.PhotoImage(pdf_img)
            pdf_btn = tk.Button(lista_frame, text='.PDF', image=pdf_icono, command=pdf_busqueda)
            pdf_btn.pack(pady=5)

            buscar_entry.bind('<Return>', release_busqueda)
            lista.bind('<Button-1>', click_header)

        def poblar_navieras_box():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT nombre
                            FROM Navieras
                            ORDER BY nombre ASC""")

                query = c.fetchall()

                naviera_box.config(values=query)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close

        def insertar_siguiente():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT n_naviera
                        FROM Navieras
                        ORDER BY n_naviera DESC
                        LIMIT 1""")

                naviera_n_entry.insert(0, c.fetchone()[0]+1)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()
                pass

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Navieras
                        WHERE n_naviera= %s"""

                c.execute(stmt, naviera_n_entry.get())

                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                naviera_box.delete(0, tk.END)
                rfc_entry.delete(0, tk.END)
                uso_cfdi_box.delete(0, tk.END)
                metodo_pago_box.delete(0, tk.END)
                domicilio_entry.delete(1.0, tk.END)

                naviera_box.insert(0, datos[1])
                rfc_entry.insert(0, datos[2])
                uso_cfdi_box.insert(0, datos[5])
                metodo_pago_box.insert(0, datos[4])
                domicilio_entry.insert(1.0, datos[3])

            finally:
                db.commit()
                c.close()

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT n_naviera 
                        FROM Navieras 
                        WHERE n_naviera = %s"""

                c.execute(stmt, naviera_n_entry.get())
                query = c.fetchone()

                if query is not None:
                    query = query[0]

                c.close()

                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                if query == int(naviera_n_entry.get()):

                    mensaje = messagebox.askyesno('Naviera Existe', 'El numero de naviera %s ya existe. '
                                                                    '¿Desea guardar los cambios?' % (naviera_n_entry.get()))
                    if mensaje is True:
                        try:
                            stmt = """UPDATE Navieras 
                                        SET nombre = %s, 
                                            rfc = %s, 
                                            domicilio = %s, 
                                            m_pago = %s, 
                                            uso_cfdi = %s
                                        WHERE n_naviera = %s """

                            c.execute(stmt, (naviera_box.get(), rfc_entry.get(), domicilio_entry.get(1.0, tk.END),
                                             metodo_pago_box.get(), uso_cfdi_box.get(), naviera_n_entry.get()))

                            naviera_n_entry.delete(0, tk.END)
                            naviera_box.delete(0, tk.END)
                            rfc_entry.delete(0, tk.END)
                            domicilio_entry.delete(1.0, tk.END)
                            metodo_pago_box.delete(0, tk.END)
                            uso_cfdi_box.delete(0, tk.END)

                            db.commit()

                            insertar_siguiente()

                        finally:
                            db.commit()
                            c.close()

                else:
                    mensaje = messagebox.askyesno('Naviera Inexistente', 'La naviera %s %s no existe.'
                                                                         ' ¿Desea darla de alta ?'
                                                  % (naviera_n_entry.get(), naviera_box.get()))

                    if mensaje is True:
                        try:

                            stmt = """INSERT INTO Navieras (n_naviera, nombre, rfc, domicilio, m_pago, uso_cfdi) 
                                    VALUES (%s, %s, %s, %s, %s, %s)"""
                            c.execute(stmt, (naviera_n_entry.get(), naviera_box.get(), rfc_entry.get(),
                                             domicilio_entry.get(1.0, tk.END), metodo_pago_box.get(),
                                             uso_cfdi_box.get()))

                            naviera_n_entry.delete(0, tk.END)
                            naviera_box.delete(0, tk.END)
                            rfc_entry.delete(0, tk.END)
                            domicilio_entry.delete(1.0, tk.END)
                            metodo_pago_box.delete(0, tk.END)
                            uso_cfdi_box.delete(0, tk.END)

                            db.commit()

                            insertar_siguiente()

                        finally:
                            db.commit()
                            c.close()

            except ValueError:
                messagebox.showerror('Error!', 'El No. de Naviera solo puede ser compuesto por caracteres numericos.')

            except TypeError:
                messagebox.showerror('Error!', 'El No. de Naviera solo puede ser compuesto por caracteres numericos.')

            finally:
                db.commit()
                c.close()

        def cancelar():
            naviera_n_entry.delete(0, tk.END)
            naviera_box.delete(0, tk.END)
            rfc_entry.delete(0, tk.END)
            uso_cfdi_box.delete(0, tk.END)
            metodo_pago_box.delete(0, tk.END)
            domicilio_entry.delete(1.0, tk.END)

            insertar_siguiente()

        poblar_navieras_box()
        insertar_siguiente()

        seleccionar_btn.config(command=seleccionar)
        lista_btn.configure(relief='flat', bg='white', bd=1, command=abrir_lista)

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Clientes(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        titulo = tk.Label(self, text="Clientes", font='Segoe 12 bold')

        cliente_n_lbl = tk.Label(self, text='No. de Cliente')
        cliente_n_entry = tk.Entry(self, width=4)
        cliente_lbl = tk.Label(self, text='Cliente')
        cliente_box = ttk.Combobox(self, width=17)

        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)

        rfc_lbl = tk.Label(self, text='R.F.C.')
        rfc_entry = tk.Entry(self)
        uso_cfdi_lbl = tk.Label(self, text='Uso de CFDI')
        uso_cfdi_box = ttk.Combobox(self)
        metodo_pago_lbl = tk.Label(self, text='Metodo de Pago')
        metodo_pago_box = ttk.Combobox(self)

        domicilio_lbl = tk.Label(self, text='Domicilio')
        domicilio_entry = tk.Text(self, height=5, width=25)

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        cliente_n_lbl.place(relx=4 / 24, rely=2 / 11)
        cliente_n_entry.place(relx=6 / 24, rely=2 / 11)
        cliente_lbl.place(relx=7 / 24, rely=2 / 11)
        cliente_box.place(relx=8 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=11 / 24, rely=2 / 11)

        rfc_lbl.place(relx=4 / 24, rely=3 / 11)
        rfc_entry.place(relx=6 / 24, rely=3 / 11)
        uso_cfdi_lbl.place(relx=9 / 24, rely=3 / 11)
        uso_cfdi_box.place(relx=11 / 24, rely=3 / 11)
        metodo_pago_lbl.place(relx=14 / 24, rely=3 / 11)
        metodo_pago_box.place(relx=16 / 24, rely=3 / 11)

        domicilio_lbl.place(relx=4 / 24, rely=4 / 11)
        domicilio_entry.place(relx=6 / 24, rely=4 / 11)

        lista_btn = tk.Button(self, text='Lista de Clientes')
        lista_btn.place(relx=1 / 50, rely=9 / 10)

        # FUNCIONES SELECCIONAR GUARDAR Y CANCELAR

        def abrir_lista():

            ventana_lista = tk.Toplevel()
            ventana_lista.minsize(width=1000, height=560)
            ventana_lista.maxsize(width=1000, height=560)

            busqueda_frame = tk.Frame(ventana_lista)
            busqueda_frame.pack(pady=10)

            lista_frame = tk.Label(ventana_lista)
            lista_frame.pack()

            criterios_lbl = tk.Label(busqueda_frame, text='Criterio de Busqueda:')
            criterios_lbl.grid(column=0, row=0)

            criterios_busqueda_box = ttk.Combobox(busqueda_frame)
            criterios_busqueda_box.grid(column=1, row=0)

            buscar_lbl = tk.Label(busqueda_frame, text='Buscar:')
            buscar_lbl.grid(column=2, row=0, padx=(10, 0))

            buscar_entry = tk.Entry(busqueda_frame)
            buscar_entry.grid(column=3, row=0)

            scroll0 = tk.Scrollbar(ventana_lista, orient='horizontal')
            scroll0.pack(fill='x')

            lista_busqueda = ttk.Treeview(lista_frame, height=5, xscrollcommand=scroll0.set)
            lista_busqueda.pack()

            tabla_frame = tk.Frame(ventana_lista)
            tabla_frame.pack()

            scrollbar = tk.Scrollbar(ventana_lista, orient='horizontal')
            scrollbar.pack(side='bottom', fill='x')

            lista = ttk.Treeview(tabla_frame, height=15, xscrollcommand=scrollbar.set)
            lista.pack(padx=10, pady=10)

            scroll0.configure(command=lista_busqueda.xview)
            scrollbar.configure(command=lista.xview)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute('DESCRIBE Clientes')
                query = c.fetchall()

                columnas = []
                for campo in query:
                    columnas.append(campo[0])

                criterios_busqueda_box.configure(values=columnas, state='readonly')

                lista_busqueda.configure(columns=columnas)
                lista_busqueda['show'] = 'headings'

                lista.configure(columns=columnas)
                lista['show'] = 'headings'

                for columna in columnas:
                    lista.heading(columna, text=columna)
                    lista.column(columna, minwidth=100, width=100, stretch='no')
                    lista_busqueda.heading(columna, text=columna)
                    lista_busqueda.column(columna, minwidth=100, width=100, stretch='no')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                            FROM Clientes
                            ORDER BY n_cliente DESC""")
                query = c.fetchall()

                for fila in query:
                    lista.insert("", 'end', values=fila)

            finally:
                c.close()

            def release_busqueda(event):
                try:
                    lista_busqueda.delete(*lista_busqueda.get_children())

                finally:
                    pass

                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    c.execute("SELECT * FROM Clientes WHERE " + criterios_busqueda_box.get() + "= " + "'" +
                              buscar_entry.get() + "'" + "")

                    query = c.fetchall()

                    for renglon in query:
                        lista_busqueda.insert("", 'end', values=renglon)

                finally:
                    c.close()

            def click_header(event):

                n_columna = lista.identify_column(event.x).replace('#', '')

                if lista.identify('region', event.x, event.y) == 'heading':
                    try:
                        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                        c = db.cursor()

                        c.execute("SELECT * FROM Clientes ORDER BY " + columnas[int(n_columna) - 1] + " DESC")

                        query = c.fetchall()

                        lista.delete(*lista.get_children())

                        for renglon in query:
                            lista.insert("", 'end', values=renglon)

                    finally:
                        c.close()

            def pdf_busqueda():

                busqueda = Canvas('busqueda.pdf', pagesize=LETTER)
                busqueda.setFont('Helvetica', 8)
                x = 8
                for columna in columnas:
                    busqueda.drawString(x, 760, columna)
                    x += 80

                x = 8
                y = 750
                for fila in lista_busqueda.get_children():
                    for columna in lista_busqueda.item(fila)['values']:
                        busqueda.drawString(x, y, str(columna))
                        x += 80
                    x = 8
                    y += -10

                busqueda.save()
                startfile('busqueda.pdf')

            global pdf_img
            pdf_icono = self.image2 = ImageTk.PhotoImage(pdf_img)
            pdf_btn = tk.Button(lista_frame, text='.PDF', image=pdf_icono, command=pdf_busqueda)
            pdf_btn.pack(pady=5)

            buscar_entry.bind('<Return>', release_busqueda)
            lista.bind('<Button-1>', click_header)

        def poblar_clientes_box():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT nombre
                            FROM Clientes
                            ORDER BY nombre ASC""")
                query = c.fetchall()

                clientes = []
                i = 0
                for cliente in query:
                    clientes.append(query[i][0])
                    i += 1

                cliente_box.config(values=clientes)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def insertar_siguiente():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT n_cliente
                        FROM Clientes
                        ORDER BY n_cliente DESC
                        LIMIT 1""")

                cliente_n_entry.insert(0, c.fetchone()[0]+1)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Clientes
                        WHERE n_cliente= %s"""

                c.execute(stmt, cliente_n_entry.get())

                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                cliente_box.delete(0, tk.END)
                rfc_entry.delete(0, tk.END)
                uso_cfdi_box.delete(0, tk.END)
                metodo_pago_box.delete(0, tk.END)
                domicilio_entry.delete(1.0, tk.END)

                cliente_box.insert(0, datos[1])
                rfc_entry.insert(0, datos[2])
                uso_cfdi_box.insert(0, datos[5])
                metodo_pago_box.insert(0, datos[4])
                domicilio_entry.insert(1.0, datos[3])

            finally:
                db.commit()
                c.close()

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT n_cliente 
                        FROM Clientes 
                        WHERE n_cliente = %s"""

                c.execute(stmt, cliente_n_entry.get())
                query = c.fetchone()

                if query is not None:
                    query = query[0]

                c.close()

                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                if query == int(cliente_n_entry.get()):

                    mensaje = messagebox.askyesno('Cliente Existe', 'El numero de cliente %s ya existe. '
                                                                    '¿Desea guardar los cambios?' % (cliente_n_entry.get()))
                    if mensaje is True:
                        try:
                            stmt = """UPDATE Clientes 
                                        SET nombre = %s, 
                                            rfc = %s, 
                                            domicilio = %s, 
                                            m_pago = %s, 
                                            uso_cfdi = %s
                                        WHERE n_cliente = %s """

                            c.execute(stmt, (cliente_box.get(), rfc_entry.get(), domicilio_entry.get(1.0, tk.END),
                                             metodo_pago_box.get(), uso_cfdi_box.get(), cliente_n_entry.get()))

                            db.commit()

                            cliente_n_entry.delete(0, tk.END)
                            cliente_box.delete(0, tk.END)
                            rfc_entry.delete(0, tk.END)
                            domicilio_entry.delete(1.0, tk.END)
                            metodo_pago_box.delete(0, tk.END)
                            uso_cfdi_box.delete(0, tk.END)

                            insertar_siguiente()

                        finally:
                            db.commit()
                            c.close()

                else:
                    mensaje = messagebox.askyesno('Cliente Inexistente', 'El cliente %s %s no existe.'
                                                                         ' ¿Desea darlo de alta ?'
                                                  % (cliente_n_entry.get(), cliente_box.get()))

                    if mensaje is True:
                        try:
                            stmt = """INSERT INTO Clientes (n_cliente, nombre, rfc, domicilio, m_pago, uso_cfdi) 
                                    VALUES (%s, %s, %s, %s, %s, %s)"""

                            c.execute(stmt, (cliente_n_entry.get(), cliente_box.get(), rfc_entry.get(),
                                             domicilio_entry.get(1.0, tk.END), metodo_pago_box.get(),
                                             uso_cfdi_box.get()))

                            cliente_n_entry.delete(0, tk.END)
                            cliente_box.delete(0, tk.END)
                            rfc_entry.delete(0, tk.END)
                            domicilio_entry.delete(1.0, tk.END)
                            metodo_pago_box.delete(0, tk.END)
                            uso_cfdi_box.delete(0, tk.END)

                            db.commit()

                            insertar_siguiente()

                        finally:
                            db.commit()
                            c.close()

            except ValueError:
                messagebox.showerror('Error!', 'El No. de Cliente solo puede ser compuesto por caracteres numericos.')

            except TypeError:
                messagebox.showerror('Error!', 'El No. de Cliente solo puede ser compuesto por caracteres numericos.')

            finally:
                db.commit()
                c.close()

        def cancelar():
            cliente_n_entry.delete(0, tk.END)
            cliente_box.delete(0, tk.END)
            rfc_entry.delete(0, tk.END)
            uso_cfdi_box.delete(0, tk.END)
            metodo_pago_box.delete(0, tk.END)
            domicilio_entry.delete(1.0, tk.END)
            insertar_siguiente()

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        lista_btn.configure(relief='flat', bg='white', bd=1, command=abrir_lista)
        seleccionar_btn.configure(command=seleccionar)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)

        poblar_clientes_box()
        insertar_siguiente()


class Unidades(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        titulo = tk.Label(self, text="Unidades", font='Segoe 12 bold')

        economico_n_lbl = tk.Label(self, text='Económico')
        economico_n_entry = tk.Entry(self, width=4)
        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)

        motor_n_lbl = tk.Label(self, text='No. de Motor')
        motor_n_entry = tk.Entry(self)
        placas_lbl = tk.Label(self, text='Placas')
        placas_entry = tk.Entry(self)
        modelo_lbl = tk.Label(self, text='Modelo')
        modelo_entry = tk.Entry(self)

        niv_lbl = tk.Label(self, text='N.I.V.')
        niv_entry = tk.Entry(self)
        descripcion_lbl = tk.Label(self, text='Descripción')
        descripcion_text = tk.Text(self, width=15, height=5)

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        economico_n_lbl.place(relx=4 / 24, rely=2 / 11)
        economico_n_entry.place(relx=6 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=7 / 24, rely=2 / 11)

        motor_n_lbl.place(relx=4 / 24, rely=3 / 11)
        motor_n_entry.place(relx=6 / 24, rely=3 / 11)
        placas_lbl.place(relx=9 / 24, rely=3 / 11)
        placas_entry.place(relx=11 / 24, rely=3 / 11)
        modelo_lbl.place(relx=14 / 24, rely=3 / 11)
        modelo_entry.place(relx=16 / 24, rely=3 / 11)

        niv_lbl.place(relx=4 / 24, rely=4 / 11)
        niv_entry.place(relx=6 / 24, rely=4 / 11)
        descripcion_lbl.place(relx=9 / 24, rely=4 / 11)
        descripcion_text.place(relx=11 / 24, rely=4 / 11)

        # FUNCIONES GUARDAR Y CANCELAR

        def abrir_lista():

            ventana_lista = tk.Toplevel()
            ventana_lista.minsize(width=1000, height=560)
            ventana_lista.maxsize(width=1000, height=560)

            busqueda_frame = tk.Frame(ventana_lista)
            busqueda_frame.pack(pady=10)

            lista_frame = tk.Label(ventana_lista)
            lista_frame.pack()

            criterios_lbl = tk.Label(busqueda_frame, text='Criterio de Búsqueda:')
            criterios_lbl.grid(column=0, row=0)

            criterios_busqueda_box = ttk.Combobox(busqueda_frame)
            criterios_busqueda_box.grid(column=1, row=0)

            buscar_lbl = tk.Label(busqueda_frame, text='Buscar:')
            buscar_lbl.grid(column=2, row=0, padx=(10, 0))

            buscar_entry = tk.Entry(busqueda_frame)
            buscar_entry.grid(column=3, row=0)

            scroll0 = tk.Scrollbar(ventana_lista, orient='horizontal')
            scroll0.pack(fill='x')

            lista_busqueda = ttk.Treeview(lista_frame, height=5, xscrollcommand=scroll0.set)
            lista_busqueda.pack()

            tabla_frame = tk.Frame(ventana_lista)
            tabla_frame.pack()

            scrollbar = tk.Scrollbar(ventana_lista, orient='horizontal')
            scrollbar.pack(side='bottom', fill='x')

            lista = ttk.Treeview(tabla_frame, height=15, xscrollcommand=scrollbar.set)
            lista.pack(padx=10, pady=10)

            scroll0.configure(command=lista_busqueda.xview)
            scrollbar.configure(command=lista.xview)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute('DESCRIBE Unidades')
                query = c.fetchall()

                columnas = []
                for campo in query:
                    columnas.append(campo[0])

                criterios_busqueda_box.configure(values=columnas, state='readonly')

                lista_busqueda.configure(columns=columnas)
                lista_busqueda['show'] = 'headings'

                lista.configure(columns=columnas)
                lista['show'] = 'headings'

                for columna in columnas:
                    lista.heading(columna, text=columna)
                    lista.column(columna, minwidth=100, width=100, stretch='no')
                    lista_busqueda.heading(columna, text=columna)
                    lista_busqueda.column(columna, minwidth=100, width=100, stretch='no')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                            FROM Unidades
                            ORDER BY n_economico DESC""")
                query = c.fetchall()

                for fila in query:
                    lista.insert("", 'end', values=fila)

            finally:
                c.close()

            def release_busqueda(event):
                try:
                    lista_busqueda.delete(*lista_busqueda.get_children())

                finally:
                    pass

                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    c.execute("SELECT * FROM Unidades WHERE " + criterios_busqueda_box.get() + "= " + "'" +
                              buscar_entry.get() + "'" + "")

                    query = c.fetchall()

                    for renglon in query:
                        lista_busqueda.insert("", 'end', values=renglon)

                finally:
                    c.close()

            def click_header(event):

                n_columna = lista.identify_column(event.x).replace('#', '')

                if lista.identify('region', event.x, event.y) == 'heading':
                    try:
                        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                        c = db.cursor()

                        c.execute("SELECT * FROM Unidades ORDER BY " + columnas[int(n_columna) - 1] + " DESC")

                        query = c.fetchall()

                        lista.delete(*lista.get_children())

                        for renglon in query:
                            lista.insert("", 'end', values=renglon)

                    finally:
                        c.close()

            def pdf_busqueda():

                busqueda = Canvas('busqueda.pdf', pagesize=LETTER)
                busqueda.setFont('Helvetica', 8)
                x = 8
                for columna in columnas:
                    busqueda.drawString(x, 760, columna)
                    x += 80

                x = 8
                y = 750
                for fila in lista_busqueda.get_children():
                    for columna in lista_busqueda.item(fila)['values']:
                        busqueda.drawString(x, y, str(columna))
                        x += 80
                    x = 8
                    y += -10

                busqueda.save()
                startfile('busqueda.pdf')

            global pdf_img
            pdf_icono = self.image2 = ImageTk.PhotoImage(pdf_img)
            pdf_btn = tk.Button(lista_frame, text='.PDF', image=pdf_icono, command=pdf_busqueda)
            pdf_btn.pack(pady=5)

            buscar_entry.bind('<Return>', release_busqueda)
            lista.bind('<Button-1>', click_header)

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Unidades
                        WHERE n_economico = %s"""

                c.execute(stmt, economico_n_entry.get())

                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                motor_n_entry.delete(0, tk.END)
                placas_entry.delete(0, tk.END)
                modelo_entry.delete(0, tk.END)
                niv_entry.delete(0, tk.END)
                descripcion_text.delete(1.0, tk.END)

                motor_n_entry.insert(0, datos[1])
                placas_entry.insert(0, datos[2])
                modelo_entry.insert(0, datos[3])
                niv_entry.insert(0, datos[4])
                descripcion_text.insert(1.0, datos[5])

            finally:
                db.commit()
                c.close()

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT n_economico
                        FROM Unidades 
                        WHERE n_economico = %s"""

                c.execute(stmt, economico_n_entry.get())
                query = c.fetchone()

                if query is not None:
                    query = query[0]

                c.close()

                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                if query == int(economico_n_entry.get()):

                    mensaje = messagebox.askyesno('Unidad Existe', 'El número de unidad %s ya existe. '
                                                                   '¿Desea guardar los cambios?'
                                                  % (economico_n_entry.get()))
                    if mensaje is True:
                        try:
                            stmt = """UPDATE Unidades 
                                        SET n_motor = %s, 
                                            placas = %s, 
                                            modelo = %s, 
                                            niv = %s, 
                                            descripcion = %s
                                        WHERE n_economico = %s """

                            c.execute(stmt, (motor_n_entry.get(), placas_entry.get(), modelo_entry.get(),
                                             niv_entry.get(), descripcion_text.get(1.0, tk.END),
                                             economico_n_entry.get()))

                            motor_n_entry.delete(0, tk.END)
                            placas_entry.delete(0, tk.END)
                            modelo_entry.delete(0, tk.END)
                            niv_entry.delete(0, tk.END)
                            descripcion_text.delete(1.0, tk.END)
                            economico_n_entry.delete(0, tk.END)

                        finally:
                            db.commit()
                            c.close()

                else:
                    mensaje = messagebox.askyesno('Unidad Inexistente', 'La unidad %s no existe. '
                                                                        '¿Desea darla de alta ?'
                                                  % economico_n_entry.get())

                    if mensaje is True:
                        try:

                            stmt = """INSERT INTO Unidades (n_economico, n_motor, placas, modelo, niv, descripcion) 
                                    VALUES (%s, %s, %s, %s, %s, %s)"""
                            c.execute(stmt, (economico_n_entry.get(), motor_n_entry.get(), placas_entry.get(),
                                             modelo_entry.get(), niv_entry.get(), descripcion_text.get(1.0, tk.END)))

                            motor_n_entry.delete(0, tk.END)
                            placas_entry.delete(0, tk.END)
                            modelo_entry.delete(0, tk.END)
                            niv_entry.delete(0, tk.END)
                            descripcion_text.delete(1.0, tk.END)
                            economico_n_entry.delete(0, tk.END)

                        finally:
                            db.commit()
                            c.close()

            except ValueError:
                messagebox.showerror('Error!', 'El No. de Unidad solo puede ser compuesto por caracteres numericos.')

            except TypeError:
                messagebox.showerror('Error!', 'El No. de Unidad solo puede ser compuesto por caracteres numericos.')

            finally:
                db.commit()
                c.close()

        def cancelar():
            economico_n_entry.delete(0, tk.END)
            motor_n_entry.delete(0, tk.END)
            placas_entry.delete(0, tk.END)
            modelo_entry.delete(0, tk.END)
            niv_entry.delete(0, tk.END)
            descripcion_text.delete(1.0, tk.END)

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        lista_btn = tk.Button(self, text='Lista de Unidades')
        lista_btn.place(relx=1 / 50, rely=9 / 10)
        lista_btn.configure(relief='flat', bg='white', bd=1, command=abrir_lista)
        seleccionar_btn.configure(command=seleccionar)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Personal(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        titulo = tk.Label(self, text='Personal', font='Segoe 12 bold')

        empleado_n_lbl = tk.Label(self, text='No. de Empleado')
        empleado_n_entry = tk.Entry(self, width=4)
        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)

        nombre_lbl = tk.Label(self, text='Nombre (s)')
        nombre_entry = tk.Entry(self)
        apellido1_lbl = tk.Label(self, text='Primer Apellido')
        apellido1_entry = tk.Entry(self)
        apellido2_lbl = tk.Label(self, text='Segundo Apellido')
        apellido2_entry = tk.Entry(self)

        rfc_lbl = tk.Label(self, text='R.F.C.')
        rfc_entry = tk.Entry(self)
        correo_lbl = tk.Label(self, text='Correo Electronico')
        correo_entry = tk.Entry(self)
        telefono_lbl = tk.Label(self, text='Tel. Emergencia')
        telefono_entry = tk.Entry(self)

        id_lbl = tk.Label(self, text='Identificacion')
        id_box = ttk.Combobox(self, width=17)
        id_n_lbl = tk.Label(self, text='No. Identificación')
        id_n_entry = tk.Entry(self)
        fecha_vencimiento_lbl = tk.Label(self, text='Vencimiento')
        fecha_vencimiento_entry = tk.Entry(self, width=10)

        fecha_vencimiento_entry.insert(0, '0000-00-00')

        imss_lbl = tk.Label(self, text='No. de I.M.S.S.')
        imss_entry = tk.Entry(self)
        fecha_alta_lbl = tk.Label(self, text='Fecha de Alta')
        fecha_alta_entry = tk.Entry(self, width=10)
        fecha_baja_lbl = tk.Label(self, text='Fecha de Baja')
        fecha_baja_entry = tk.Entry(self, width=10)

        fecha_alta_entry.insert(0, date.today())
        fecha_baja_entry.insert(0, '0000-00-00')

        tipo_empleado_lbl = tk.Label(self, text='Tipo de Empleado')
        tipo_empleado_entry = ttk.Combobox(self, width=17, values=('Operador', 'Patio', 'Oficina'), state='readonly')
        banco_lbl = tk.Label(self, text='Banco')
        banco_box = ttk.Combobox(self, width=17)
        cuenta_n_lbl = tk.Label(self, text='No. de Cuenta')
        cuenta_n_entry = tk.Entry(self)

        domicilio_lbl = tk.Label(self, text='Domicilio')
        domicilio_text = tk.Text(self, width=35, height=4)

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        empleado_n_lbl.place(relx=4 / 24, rely=2 / 11)
        empleado_n_entry.place(relx=6 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=7 / 24, rely=2 / 11)

        nombre_lbl.place(relx=4 / 24, rely=3 / 11)
        nombre_entry.place(relx=6 / 24, rely=3 / 11)
        apellido1_lbl.place(relx=9 / 24, rely=3 / 11)
        apellido1_entry.place(relx=11 / 24, rely=3 / 11)
        apellido2_lbl.place(relx=14 / 24, rely=3 / 11)
        apellido2_entry.place(relx=16 / 24, rely=3 / 11)

        rfc_lbl.place(relx=4 / 24, rely=4 / 11)
        rfc_entry.place(relx=6 / 24, rely=4 / 11)
        correo_lbl.place(relx=9 / 24, rely=4 / 11)
        correo_entry.place(relx=11 / 24, rely=4 / 11)
        telefono_lbl.place(relx=14 / 24, rely=4 / 11)
        telefono_entry.place(relx=16 / 24, rely=4 / 11)

        id_lbl.place(relx=4 / 24, rely=5 / 11)
        id_box.place(relx=6 / 24, rely=5 / 11)
        id_n_lbl.place(relx=9 / 24, rely=5 / 11)
        id_n_entry.place(relx=11 / 24, rely=5 / 11)
        fecha_vencimiento_lbl.place(relx=14 / 24, rely=5 / 11)
        fecha_vencimiento_entry.place(relx=16 / 24, rely=5 / 11)

        imss_lbl.place(relx=4 / 24, rely=6 / 11)
        imss_entry.place(relx=6 / 24, rely=6 / 11)
        fecha_alta_lbl.place(relx=9 / 24, rely=6 / 11)
        fecha_alta_entry.place(relx=11 / 24, rely=6 / 11)
        fecha_baja_lbl.place(relx=14 / 24, rely=6 / 11)
        fecha_baja_entry.place(relx=16 / 24, rely=6 / 11)

        tipo_empleado_lbl.place(relx=4 / 24, rely=7 / 11)
        tipo_empleado_entry.place(relx=6 / 24, rely=7 / 11)
        banco_lbl.place(relx=9 / 24, rely=7 / 11)
        banco_box.place(relx=11 / 24, rely=7 / 11)
        cuenta_n_lbl.place(relx=14 / 24, rely=7 / 11)
        cuenta_n_entry.place(relx=16 / 24, rely=7 / 11)

        domicilio_lbl.place(relx=4 / 24, rely=8 / 11)
        domicilio_text.place(relx=6 / 24, rely=8 / 11)

        # FUNCIONES SELECCIONAR GUARDAR Y CANCELAR

        def abrir_lista():

            ventana_lista = tk.Toplevel()
            ventana_lista.minsize(width=1000, height=560)
            ventana_lista.maxsize(width=1000, height=560)

            busqueda_frame = tk.Frame(ventana_lista)
            busqueda_frame.pack(pady=10)

            lista_frame = tk.Label(ventana_lista)
            lista_frame.pack()

            criterios_lbl = tk.Label(busqueda_frame, text='Criterio de Busqueda:')
            criterios_lbl.grid(column=0, row=0)

            criterios_busqueda_box = ttk.Combobox(busqueda_frame)
            criterios_busqueda_box.grid(column=1, row=0)

            buscar_lbl = tk.Label(busqueda_frame, text='Buscar:')
            buscar_lbl.grid(column=2, row=0, padx=(10, 0))

            buscar_entry = tk.Entry(busqueda_frame)
            buscar_entry.grid(column=3, row=0)

            scroll0 = tk.Scrollbar(ventana_lista, orient='horizontal')
            scroll0.pack(fill='x')

            lista_busqueda = ttk.Treeview(lista_frame, height=5, xscrollcommand=scroll0.set)
            lista_busqueda.pack()

            tabla_frame = tk.Frame(ventana_lista)
            tabla_frame.pack()

            scrollbar = tk.Scrollbar(ventana_lista, orient='horizontal')
            scrollbar.pack(side='bottom', fill='x')

            lista = ttk.Treeview(tabla_frame, height=15, xscrollcommand=scrollbar.set)
            lista.pack(padx=10, pady=10)

            scroll0.configure(command=lista_busqueda.xview)
            scrollbar.configure(command=lista.xview)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute('DESCRIBE Personal')
                query = c.fetchall()

                columnas = []
                for campo in query:
                    columnas.append(campo[0])

                criterios_busqueda_box.configure(values=columnas, state='readonly')

                lista_busqueda.configure(columns=columnas)
                lista_busqueda['show'] = 'headings'

                lista.configure(columns=columnas)
                lista['show'] = 'headings'

                for columna in columnas:
                    lista.heading(columna, text=columna)
                    lista.column(columna, minwidth=70, width=70, stretch='no')
                    lista_busqueda.heading(columna, text=columna)
                    lista_busqueda.column(columna, minwidth=70, width=70, stretch='no')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                            FROM Personal
                            ORDER BY n_empleado DESC""")
                query = c.fetchall()

                for fila in query:
                    lista.insert("", 'end', values=fila)

            finally:
                c.close()

            def release_busqueda(event):
                try:
                    lista_busqueda.delete(*lista_busqueda.get_children())

                finally:
                    pass

                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    c.execute("SELECT * FROM Personal WHERE " + criterios_busqueda_box.get() + "= " + "'" +
                              buscar_entry.get() + "'" + "")

                    query = c.fetchall()

                    for renglon in query:
                        lista_busqueda.insert("", 'end', values=renglon)

                finally:
                    c.close()

            def click_header(event):

                n_columna = lista.identify_column(event.x).replace('#', '')

                if lista.identify('region', event.x, event.y) == 'heading':
                    try:
                        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                        c = db.cursor()

                        c.execute("SELECT * FROM Personal ORDER BY " + columnas[int(n_columna) - 1] + " DESC")

                        query = c.fetchall()

                        lista.delete(*lista.get_children())

                        for renglon in query:
                            lista.insert("", 'end', values=renglon)

                    finally:
                        c.close()

            def pdf_busqueda():

                busqueda = Canvas('busqueda.pdf', pagesize=landscape(LEGAL))
                busqueda.setFont('Helvetica', 8)
                x = 8
                for columna in columnas:
                    busqueda.drawString(x, 600, columna)
                    x += 60

                x = 8
                y = 590
                for fila in lista_busqueda.get_children():
                    for columna in lista_busqueda.item(fila)['values']:
                        busqueda.drawString(x, y, str(columna))
                        x += 60
                    x = 8
                    y += -10

                busqueda.save()
                startfile('busqueda.pdf')

            global pdf_img
            pdf_icono = self.image2 = ImageTk.PhotoImage(pdf_img)
            pdf_btn = tk.Button(lista_frame, text='.PDF', image=pdf_icono, command=pdf_busqueda)
            pdf_btn.pack(pady=5)

            buscar_entry.bind('<Return>', release_busqueda)
            lista.bind('<Button-1>', click_header)

        def insertar_siguiente():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT n_empleado
                            FROM Personal
                            ORDER BY n_empleado DESC""")

                empleado_n_entry.insert(0, c.fetchone()[0]+1)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Personal
                        WHERE n_empleado= %s"""

                c.execute(stmt, empleado_n_entry.get())
                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                tipo_empleado_entry.config(state='normal')
                nombre_entry.delete(0, tk.END)
                apellido1_entry.delete(0, tk.END)
                apellido2_entry.delete(0, tk.END)
                rfc_entry.delete(0, tk.END)
                correo_entry.delete(0, tk.END)
                telefono_entry.delete(0, tk.END)
                id_box.delete(0, tk.END)
                id_n_entry.delete(0, tk.END)
                fecha_vencimiento_entry.delete(0, tk.END)
                imss_entry.delete(0, tk.END)
                fecha_alta_entry.delete(0, tk.END)
                fecha_baja_entry.delete(0, tk.END)
                tipo_empleado_entry.delete(0, tk.END)
                banco_box.delete(0, tk.END)
                cuenta_n_entry.delete(0, tk.END)
                domicilio_text.delete(1.0, tk.END)

                nombre_entry.insert(0, datos[1])
                apellido1_entry.insert(0, datos[2])
                apellido2_entry.insert(0, datos[3])
                rfc_entry.insert(0, datos[4])
                correo_entry.insert(0, datos[5])
                telefono_entry.insert(0, datos[6])
                id_box.insert(0, datos[7])
                id_n_entry.insert(0, datos[8])
                fecha_vencimiento_entry.insert(0, datos[9])
                imss_entry.insert(0, datos[10])
                fecha_alta_entry.insert(0, datos[11])
                fecha_baja_entry.insert(0, datos[12])
                tipo_empleado_entry.insert(0, datos[13])
                banco_box.insert(0, datos[14])
                cuenta_n_entry.insert(0, datos[15])
                domicilio_text.insert(1.0, datos[16])

                tipo_empleado_entry.config(state='readonly')

            finally:
                c.close()

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT n_empleado
                        FROM personal
                        WHERE n_empleado = %s"""

                c.execute(stmt, empleado_n_entry.get())
                query = c.fetchone()

                if query is not None:
                    query = query[0]

                if query == int(empleado_n_entry.get()):
                    mensaje = messagebox.askyesno('Empleado Existe', 'El numero de empleado %s ya existe. '
                                                                 '¿Desea guardar los cambios?' % empleado_n_entry.get())
                    if mensaje is True:
                        try:
                            stmt = """UPDATE Personal
                                    SET nombres = %s,
                                        apellido1 = %s,
                                        apellido2 = %s,
                                        rfc = %s,
                                        correo = %s,
                                        tel = %s,
                                        id = %s,
                                        n_id = %s,
                                        vencimiento_id = %s,
                                        imss = %s,
                                        alta = %s,
                                        baja = %s,
                                        tipo = %s,
                                        banco = %s,
                                        n_cuenta = %s,
                                        domicilio = %s
                                    WHERE n_empleado = %s"""

                            c.execute(stmt, (nombre_entry.get(), apellido1_entry.get(), apellido2_entry.get(),
                                             rfc_entry.get(), correo_entry.get(), telefono_entry.get(),
                                             id_box.get(), id_n_entry.get(), fecha_vencimiento_entry.get(),
                                             imss_entry.get(), fecha_alta_entry.get(), fecha_baja_entry.get(),
                                             tipo_empleado_entry.get(), banco_box.get(), cuenta_n_entry.get(),
                                             domicilio_text.get(1.0, tk.END), empleado_n_entry.get()))

                            empleado_n_entry.delete(0, tk.END)
                            nombre_entry.delete(0, tk.END)
                            apellido1_entry.delete(0, tk.END)
                            apellido2_entry.delete(0, tk.END)
                            rfc_entry.delete(0, tk.END)
                            correo_entry.delete(0, tk.END)
                            telefono_entry.delete(0, tk.END)
                            id_box.delete(0, tk.END)
                            id_n_entry.delete(0, tk.END)
                            fecha_vencimiento_entry.delete(0, tk.END)
                            imss_entry.delete(0, tk.END)
                            fecha_alta_entry.delete(0, tk.END)
                            fecha_baja_entry.delete(0, tk.END)
                            banco_box.delete(0, tk.END)
                            cuenta_n_entry.delete(0, tk.END)
                            domicilio_text.delete(1.0, tk.END)
                            tipo_empleado_entry.config(state='normal')
                            tipo_empleado_entry.delete(0, tk.END)
                            tipo_empleado_entry.config(state='normal')

                            fecha_vencimiento_entry.insert(0, "0000-00-00")
                            fecha_alta_entry.insert(0, date.today())
                            fecha_baja_entry.insert(0, '0000-00-00')

                            db.commit()

                            insertar_siguiente()

                        finally:
                            c.close()

                else:
                    mensaje = messagebox.askyesno('Empleado Inexistente', 'El empleado con numero %s no existe.'
                                                                          ' ¿Desea dar de alta ?'
                                                  % (empleado_n_entry.get()))
                    if mensaje is True:
                        try:
                            stmt = """INSERT INTO Personal(n_empleado, nombres, apellido1, apellido2, rfc, correo, tel,
                                                            id, n_id, vencimiento_id, imss, alta, baja, tipo, banco, 
                                                            n_cuenta, domicilio)
                                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

                            c.execute(stmt, (empleado_n_entry.get(), nombre_entry.get(), apellido1_entry.get(),
                                             apellido2_entry.get(), rfc_entry.get(), correo_entry.get(),
                                             telefono_entry.get(), id_box.get(), id_n_entry.get(),
                                             fecha_vencimiento_entry.get(), imss_entry.get(), fecha_alta_entry.get(),
                                             fecha_baja_entry.get(), tipo_empleado_entry.get(), banco_box.get(),
                                             cuenta_n_entry.get(), domicilio_text.get(1.0, tk.END)))

                            empleado_n_entry.delete(0, tk.END)
                            nombre_entry.delete(0, tk.END)
                            apellido1_entry.delete(0, tk.END)
                            apellido2_entry.delete(0, tk.END)
                            rfc_entry.delete(0, tk.END)
                            correo_entry.delete(0, tk.END)
                            telefono_entry.delete(0, tk.END)
                            id_box.delete(0, tk.END)
                            id_n_entry.delete(0, tk.END)
                            fecha_vencimiento_entry.delete(0, tk.END)
                            imss_entry.delete(0, tk.END)
                            fecha_alta_entry.delete(0, tk.END)
                            fecha_baja_entry.delete(0, tk.END)
                            banco_box.delete(0, tk.END)
                            cuenta_n_entry.delete(0, tk.END)
                            domicilio_text.delete(1.0, tk.END)
                            tipo_empleado_entry.config(state='normal')
                            tipo_empleado_entry.delete(0, tk.END)
                            tipo_empleado_entry.config(state='normal')

                            fecha_vencimiento_entry.insert(0, "0000-00-00")
                            fecha_alta_entry.insert(0, date.today())
                            fecha_baja_entry.insert(0, '0000-00-00')

                            db.commit()

                            insertar_siguiente()

                        finally:
                            c.close()

            except ValueError:
                messagebox.showerror('Error!', 'El No. de Empleado solo puede ser compuesto por caracteres numericos.')

            except TypeError:
                messagebox.showerror('Error!', 'El No. de Empleado solo puede ser compuesto por caracteres numericos.')

            finally:
                c.close()

        def cancelar():
            empleado_n_entry.delete(0, tk.END)
            nombre_entry.delete(0, tk.END)
            apellido1_entry.delete(0, tk.END)
            apellido2_entry.delete(0, tk.END)
            rfc_entry.delete(0, tk.END)
            correo_entry.delete(0, tk.END)
            telefono_entry.delete(0, tk.END)
            id_box.delete(0, tk.END)
            id_n_entry.delete(0, tk.END)
            fecha_vencimiento_entry.delete(0, tk.END)
            imss_entry.delete(0, tk.END)
            fecha_alta_entry.delete(0, tk.END)
            fecha_baja_entry.delete(0, tk.END)
            banco_box.delete(0, tk.END)
            cuenta_n_entry.delete(0, tk.END)
            domicilio_text.delete(1.0, tk.END)
            tipo_empleado_entry.config(state='normal')
            tipo_empleado_entry.delete(0, tk.END)
            tipo_empleado_entry.config(state='normal')

            fecha_vencimiento_entry.insert(0, "0000-00-00")
            fecha_alta_entry.insert(0, date.today())
            fecha_baja_entry.insert(0, '0000-00-00')

            insertar_siguiente()

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        insertar_siguiente()

        lista_btn = tk.Button(self, text='Lista de Personal')
        lista_btn.place(relx=1 / 50, rely=9 / 10)
        lista_btn.configure(relief='flat', bg='white', bd=1, command=abrir_lista)
        seleccionar_btn.config(command=seleccionar)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Facturas(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        titulo = tk.Label(self, text='Facturas', font='Segoe 12 bold')

        serie_lbl = tk.Label(self, text='Serie')
        serie_entry = tk.Entry(self, width=3)
        folio_lbl = tk.Label(self, text='Folio')
        folio_entry = tk.Entry(self, width=5)
        fecha_lbl = tk.Label(self, text='Fecha')
        fecha_entry = tk.Entry(self, width=10)
        fecha_entry.insert(0, date.today())

        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)

        receptor_lbl = tk.Label(self, text='Receptor')
        receptor_box = ttk.Combobox(self)
        total_lbl = tk.Label(self, text='Total')
        total_entry = tk.Entry(self, width=6)
        estatus_lbl = tk.Label(self, text='Estatus')
        estatus_box = ttk.Combobox(self, values=('Pendiente de pago', 'Pagada', 'Por pagar'))

        orden_lbl = tk.Label(self, text='Ordenenes Asociadas a la Factura')

        serie_orden_lbl = tk.Label(self, text='Serie')
        serie_orden_entry = tk.Entry(self, width=3)
        folio_orden_lbl = tk.Label(self, text='Folio')
        folio_orden_entry = tk.Entry(self, width=5)
        anadir_btn = tk.Button(self, text='Añadir Orden', font='Segoe 8 bold')
        anadir_btn.configure(relief='flat', bg='white', bd=1)

        ordenes_tree = ttk.Treeview(self, columns=('1', '2'), height=7)

        ordenes_tree.column('1', width=50)
        ordenes_tree.column('2', width=80)
        ordenes_tree['show'] = 'headings'

        serie_lbl.place(relx=4 / 24, rely=2 / 11)
        serie_entry.place(relx=5 / 24, rely=2 / 11)
        folio_lbl.place(relx=6 / 24, rely=2 / 11)
        folio_entry.place(relx=7 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=8 / 24, rely=2 / 11)
        fecha_lbl.place(relx=12 / 24, rely=2 / 11)
        fecha_entry.place(relx=13 / 24, rely=2 / 11)

        receptor_lbl.place(relx=4/24, rely=3 / 11)
        receptor_box.place(relx=5/24, rely=3 / 11)
        total_lbl.place(relx=9/24, rely=3 / 11)
        total_entry.place(relx=10/24, rely=3 / 11)
        estatus_lbl.place(relx=11/24, rely=3/11)
        estatus_box.place(relx=12/24, rely=3/11)

        orden_lbl.place(relx=4 / 24, rely=4 / 11)

        serie_orden_lbl.place(relx=4 / 24, rely=5 / 11)
        serie_orden_entry.place(relx=5 / 24, rely=5 / 11)
        folio_orden_lbl.place(relx=6 / 24, rely=5 / 11)
        folio_orden_entry.place(relx=7 / 24, rely=5 / 11)
        anadir_btn.place(relx=8 / 24, rely=5 / 11)

        ordenes_tree.place(relx=5 / 24, rely=6 / 11)
        ordenes_tree.heading('1', text='Serie')
        ordenes_tree.heading('2', text='Folio')

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        # TODO FUNCIONES DE FACTURAS

        def insertar_siguiente():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT serie, folio
                            FROM Facturas ORDER BY folio DESC""")
                query = c.fetchone()

                serie_entry.insert(0, query[0])
                folio_entry.insert(0, query[1]+1)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def anadir_orden():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT serie, folio
                        FROM Ordenes
                        WHERE serie = %s AND folio = %s"""

                c.execute(stmt, (serie_orden_entry.get(), folio_orden_entry.get()))

                query = c.fetchone()
                ordenes_tree.insert("", 'end', values=query)

                serie_orden_entry.delete(0, tk.END)
                folio_orden_entry.delete(0, tk.END)

            finally:
                c.close()

        def poblar_receptor():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT nombre
                        FROM Navieras""")

                query = c.fetchall()
                receptor = []

                i = 0
                for naviera in query:
                    receptor.append(naviera[0])
                    i += 1

                c.execute("""SELECT nombre
                            FROM Clientes""")

                query = c.fetchall()

                i = 0
                for cliente in query:
                    receptor.append(cliente[0])
                    i += 1

                receptor_box.configure(values=receptor)

            finally:
                c.close()

        def abrir_lista():

            ventana_lista = tk.Toplevel()
            ventana_lista.minsize(width=1000, height=560)
            ventana_lista.maxsize(width=1000, height=560)

            busqueda_frame = tk.Frame(ventana_lista)
            busqueda_frame.pack(pady=10)

            lista_frame = tk.Label(ventana_lista)
            lista_frame.pack()

            criterios_lbl = tk.Label(busqueda_frame, text='Criterio de Busqueda:')
            criterios_lbl.grid(column=0, row=0)

            criterios_busqueda_box = ttk.Combobox(busqueda_frame)
            criterios_busqueda_box.grid(column=1, row=0)

            buscar_lbl = tk.Label(busqueda_frame, text='Buscar:')
            buscar_lbl.grid(column=2, row=0, padx=(10, 0))

            buscar_entry = tk.Entry(busqueda_frame)
            buscar_entry.grid(column=3, row=0)

            scroll0 = tk.Scrollbar(ventana_lista, orient='horizontal')
            scroll0.pack(fill='x')

            lista_busqueda = ttk.Treeview(lista_frame, height=5, xscrollcommand=scroll0.set)
            lista_busqueda.pack()

            tabla_frame = tk.Frame(ventana_lista)
            tabla_frame.pack()

            scrollbar = tk.Scrollbar(ventana_lista, orient='horizontal')
            scrollbar.pack(side='bottom', fill='x')

            lista = ttk.Treeview(tabla_frame, height=15, xscrollcommand=scrollbar.set)
            lista.pack(padx=10, pady=10)

            scroll0.configure(command=lista_busqueda.xview)
            scrollbar.configure(command=lista.xview)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute('DESCRIBE Facturas')
                query = c.fetchall()

                columnas = []
                for campo in query:
                    columnas.append(campo[0])

                criterios_busqueda_box.configure(values=columnas, state='readonly')

                lista_busqueda.configure(columns=columnas)
                lista_busqueda['show'] = 'headings'

                lista.configure(columns=columnas)
                lista['show'] = 'headings'

                for columna in columnas:
                    lista.heading(columna, text=columna)
                    lista.column(columna, minwidth=100, width=100, stretch='no')
                    lista_busqueda.heading(columna, text=columna)
                    lista_busqueda.column(columna, minwidth=100, width=100, stretch='no')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                               FROM Facturas
                               ORDER BY folio DESC""")
                query = c.fetchall()

                for fila in query:
                    lista.insert("", 'end', values=fila)

            finally:
                c.close()

            def release_busqueda(event):
                try:
                    lista_busqueda.delete(*lista_busqueda.get_children())

                finally:
                    pass

                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    c.execute("SELECT * FROM Facturas WHERE " + criterios_busqueda_box.get() + "= " + "'" +
                              buscar_entry.get() + "'" + "")

                    query = c.fetchall()

                    for renglon in query:
                        lista_busqueda.insert("", 'end', values=renglon)

                finally:
                    c.close()

            def click_header(event):

                n_columna = lista.identify_column(event.x).replace('#', '')

                if lista.identify('region', event.x, event.y) == 'heading':
                    try:
                        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                        c = db.cursor()

                        c.execute("SELECT * FROM Facturas ORDER BY " + columnas[int(n_columna) - 1] + " DESC")

                        query = c.fetchall()

                        lista.delete(*lista.get_children())

                        for renglon in query:
                            lista.insert("", 'end', values=renglon)

                    finally:
                        c.close()

            def pdf_busqueda():

                busqueda = Canvas('busqueda.pdf', pagesize=LETTER)
                busqueda.setFont('Helvetica', 8)
                x = 8
                for columna in columnas:
                    busqueda.drawString(x, 760, columna)
                    x += 80

                x = 8
                y = 750
                for fila in lista_busqueda.get_children():
                    for columna in lista_busqueda.item(fila)['values']:
                        busqueda.drawString(x, y, str(columna))
                        x += 80
                    x = 8
                    y += -10

                busqueda.save()
                startfile('busqueda.pdf')

            global pdf_img
            pdf_icono = self.image2 = ImageTk.PhotoImage(pdf_img)
            pdf_btn = tk.Button(lista_frame, text='.PDF', image=pdf_icono, command=pdf_busqueda)
            pdf_btn.pack(pady=5)

            buscar_entry.bind('<Return>', release_busqueda)
            lista.bind('<Button-1>', click_header)

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT fecha, receptor, total, estatus
                        FROM Facturas
                        WHERE serie = %s AND folio = %s"""

                c.execute(stmt, (serie_entry.get(), folio_entry.get()))
                query = c.fetchone()

                fecha_entry.delete(0, tk.END)
                receptor_box.delete(0, tk.END)
                total_entry.delete(0, tk.END)
                estatus_box.delete(0, tk.END)

                fecha_entry.insert(0, query[0])
                receptor_box.insert(0, query[1])
                total_entry.insert(0, query[2])
                estatus_box.insert(0, query[3])

                stmt = """SELECT serie, folio
                        FROM Ordenes
                        WHERE factura_serie = %s AND factura_folio = %s"""

                c.execute(stmt, (serie_entry.get(), folio_entry.get()))
                query = c.fetchall()

                ordenes_tree.delete(*ordenes_tree.get_children())

                for orden in query:
                    ordenes_tree.insert("",'end', values=orden)

            finally:
                c.close()

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT serie, folio
                        FROM Facturas
                        WHERE serie = %s AND folio = %s"""

                c.execute(stmt, (serie_entry.get(), folio_entry.get()))

                query = c.fetchone()

                if query is None:
                    mensaje = messagebox.askyesno('Factura Inexistente', 'La Factura %s - %s no existe. ¿Desea darla'
                                                                             ' de alta?'
                                                  % (serie_entry.get(), folio_entry.get()))
                    if mensaje is True:
                        try:
                            stmt = """INSERT INTO Facturas (serie, folio, fecha, receptor, estatus, total)
                                    VALUES (%s,%s,%s,%s,%s,%s)"""

                            c.execute(stmt, (serie_entry.get(), folio_entry.get(), fecha_entry.get(),
                                             receptor_box.get(), estatus_box.get(), total_entry.get()))
                            
                            db.commit()

                            for fila in ordenes_tree.get_children():
                                try:
                                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                                    c = db.cursor()

                                    stmt = """SELECT factura_serie, factura_folio
                                           FROM Ordenes
                                           WHERE serie = %s AND folio = %s"""

                                    c.execute(stmt, (ordenes_tree.item(fila)['values'][0],
                                                     ordenes_tree.item(fila)['values'][1]))

                                    query = c.fetchone()

                                    if query[0] is None and query[1] is None:
                                        stmt = """UPDATE Ordenes
                                                SET factura_serie = %s,
                                                    factura_folio = %s
                                                WHERE serie = %s AND folio = %s"""

                                        c.execute(stmt, (serie_entry.get(), folio_entry.get(),
                                                         ordenes_tree.item(fila)['values'][0],
                                                         ordenes_tree.item(fila)['values'][1],))

                                        db.commit()

                                    if query[0] is not None and query[0] != ordenes_tree.item(fila)['values'][0] and \
                                            query[1] is not None and query[1] != int(ordenes_tree.item(fila)['values'][1]):

                                        mensaje = messagebox.askyesno('Orden Asiganda', 'La Orden %s - %s está asignada'
                                                    ' a la Factura %s - %s. ¿Desea reasignarla a la Factura %s - %s?'
                                                                      % (ordenes_tree.item(fila)['values'][0],
                                                                         ordenes_tree.item(fila)['values'][1],
                                                                         query[0], query[1], serie_entry.get(),
                                                                         folio_entry.get()))

                                        if mensaje is True:
                                            stmt = """UPDATE Ordenes
                                                    SET factura_serie = %s,
                                                        factura_folio = %s
                                                    WHERE serie = %s AND folio = %s"""

                                            c.execute(stmt, (serie_entry.get(), folio_entry.get(),
                                                             ordenes_tree.item(fila)['values'][0],
                                                             ordenes_tree.item(fila)['values'][1],))
                                            db.commit()

                                finally:
                                    c.close()

                            cancelar()

                        finally:
                            c.close()

                elif query[0] == serie_entry.get() and query[1] == int(folio_entry.get()):
                    mensaje = messagebox.askyesno('Factura Existente', 'La Factura %s - %s ya existe.¿Desea guardar los'
                                                                       ' cambios?' % (serie_entry.get(),
                                                                                      folio_entry.get()))
                    if mensaje is True:
                        try:
                            db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                            c = db.cursor()

                            for fila in ordenes_tree.get_children():
                                try:
                                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                                    c = db.cursor()

                                    stmt = """SELECT factura_serie, factura_folio
                                           FROM Ordenes
                                           WHERE serie = %s AND folio = %s"""

                                    c.execute(stmt, (ordenes_tree.item(fila)['values'][0],
                                                     ordenes_tree.item(fila)['values'][1]))

                                    query = c.fetchone()

                                    if query[0] is None and query[1] is None:
                                        stmt = """UPDATE Ordenes
                                                SET factura_serie = %s,
                                                    factura_folio = %s
                                                WHERE serie = %s AND folio = %s"""

                                        c.execute(stmt, (serie_entry.get(), folio_entry.get(),
                                                         ordenes_tree.item(fila)['values'][0],
                                                         ordenes_tree.item(fila)['values'][1],))

                                        db.commit()

                                    if query[0] is not None and query[0] != ordenes_tree.item(fila)['values'][0] and \
                                            query[1] is not None and query[1] != int(ordenes_tree.item(fila)['values'][1]):

                                        mensaje = messagebox.askyesno('Orden Asiganda', 'La Orden %s - %s está asignada'
                                                    ' a la Factura %s - %s. ¿Desea reasignarla a la Factura %s - %s?'
                                                                      % (ordenes_tree.item(fila)['values'][0],
                                                                         ordenes_tree.item(fila)['values'][1],
                                                                         query[0], query[1], serie_entry.get(),
                                                                         folio_entry.get()))

                                        if mensaje is True:
                                            stmt = """UPDATE Ordenes
                                                    SET factura_serie = %s,
                                                        factura_folio = %s
                                                    WHERE serie = %s AND folio = %s"""

                                            c.execute(stmt, (serie_entry.get(), folio_entry.get(),
                                                             ordenes_tree.item(fila)['values'][0],
                                                             ordenes_tree.item(fila)['values'][1],))
                                            db.commit()

                                finally:
                                    c.close()

                            cancelar()

                        finally:
                            c.close()
            finally:
                c.close()

        def cancelar():
            folio_entry.delete(0, tk.END)
            serie_entry.delete(0, tk.END)
            fecha_entry.delete(0, tk.END)
            fecha_entry.insert(0, date.today())
            serie_orden_entry.delete(0, tk.END)
            folio_orden_entry.delete(0, tk.END)
            ordenes_tree.delete(*ordenes_tree.get_children())
            receptor_box.delete(0, tk.END)
            total_entry.delete(0, tk.END)
            estatus_box.delete(0, tk.END)
            poblar_receptor()
            insertar_siguiente()

        poblar_receptor()
        insertar_siguiente()

        anadir_btn.configure(command=anadir_orden)
        seleccionar_btn.configure(command=seleccionar)

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        lista_btn = tk.Button(self, text='Lista de Facturas')
        lista_btn.place(relx=1 / 50, rely=9 / 10)
        lista_btn.configure(relief='flat', bg='white', bd=1, command=abrir_lista)

        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Liquidaciones(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        global pdf_img
        pdf_icono = self.image2 = ImageTk.PhotoImage(pdf_img)

        self.configure(bd=1, relief='raised')

        titulo = tk.Label(self, text='Liquidaciones', font='Segoe 12 bold')

        folio_lbl = tk.Label(self, text='Folio')
        folio_entry = tk.Entry(self, width=5)
        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)
        operador_n_lbl = tk.Label(self, text='No. de Operador')
        operador_n_entry = tk.Entry(self, width=4)
        operador_entry = tk.Entry(self, state='disabled')
        fecha_inicio_lbl = tk.Label(self, text='Fecha de Inicio')
        fecha_inicio_entry = tk.Entry(self, width=10)
        fecha_cierre_lbl = tk.Label(self, text='Fecha de Cierre')
        fecha_cierre_entry = tk.Entry(self, width=10)
        total_btn = tk.Button(self, text='Calcular Total', font='Segoe 8 bold')
        total_btn.configure(relief='flat', bg='white', bd=1)
        total_entry = tk.Entry(self, width=7, state='disabled')

        fecha_inicio_entry.insert(0, date.today())
        fecha_cierre_entry.insert(0, date.today())

        ordenes_lbl = tk.Label(self, text='Ordenes')
        anticipos_lbl = tk.Label(self, text='Anticipos')
        comprobacion_lbl = tk.Label(self, text='Comprobación')

        serie_orden_lbl = tk.Label(self, text='Serie')
        serie_orden_entry = tk.Entry(self, width=3)
        folio_orden_lbl = tk.Label(self, text='Folio')
        folio_orden_entry = tk.Entry(self, width=4)
        comision_lbl = tk.Label(self, text='Comisión')
        comision_entry = tk.Entry(self, width=6)
        anadir_orden_btn = tk.Button(self, text='Añadir Orden', font='Segoe 8 bold')
        anadir_orden_btn.configure(relief='flat', bg='white', bd=1)
        comp_concepto_box = ttk.Combobox(self, values=('Diesel', 'Cenas', 'T. Aire', 'Transporte', 'Otros'), width=10)
        comprobado_entry = tk.Entry(self, width=5)
        autorizado_entry = tk.Entry(self, width=5)
        anadir_comp_btn = tk.Button(self, text='Añadir', font='Segoe 8 bold')
        anadir_comp_btn.configure(relief='flat', bg='white', bd=1)

        serie_anticipo_lbl = tk.Label(self, text='Serie')
        serie_anticipo_entry = tk.Entry(self, width=3)
        folio_anticipo_lbl = tk.Label(self, text='Folio')
        folio_anticipo_entry = tk.Entry(self, width=4)
        anadir_anticipo_btn = tk.Button(self, text='Añadir Anticipo', font='Segoe 8 bold')
        anadir_anticipo_btn.configure(relief='flat', bg='white', bd=1)

        ordenes_tree = ttk.Treeview(self, columns=('1', '2', '3', '4', '5'), height=7)
        ordenes_tree['columns'] = ('1', '2', '3', '4', '5')

        ordenes_tree['show'] = 'headings'

        ordenes_tree.heading('1', text='Fecha')
        ordenes_tree.heading('2', text='Serie')
        ordenes_tree.heading('3', text='Folio')
        ordenes_tree.heading('4', text='Operador')
        ordenes_tree.heading('5', text='Comisión')

        ordenes_tree.column('1', width=70)
        ordenes_tree.column('2', width=70)
        ordenes_tree.column('3', width=70)
        ordenes_tree.column('4', width=70)
        ordenes_tree.column('5', width=70)

        anticipos_tree = ttk.Treeview(self, columns=('1', '2', '3', '4', '5', '6'), height=7)
        anticipos_tree['columns'] = ('1', '2', '3', '4', '5', '6')

        anticipos_tree['show'] = 'headings'

        anticipos_tree.heading('1', text='Fecha')
        anticipos_tree.heading('2', text='Serie')
        anticipos_tree.heading('3', text='Folio')
        anticipos_tree.heading('4', text='Operador')
        anticipos_tree.heading('5', text='Concepto')
        anticipos_tree.heading('6', text='Importe')

        anticipos_tree.column('1', width=75, minwidth=75, stretch='no')
        anticipos_tree.column('2', width=55, minwidth=65, stretch='no')
        anticipos_tree.column('3', width=55, minwidth=55, stretch='no')
        anticipos_tree.column('4', width=95, minwidth=75, stretch='no')
        anticipos_tree.column('5', width=70, minwidth=70, stretch='no')
        anticipos_tree.column('6', width=70, minwidth=70, stretch='no')

        comprobacion_tree = ttk.Treeview(self, columns=('1', '2', '3'), height=7)
        comprobacion_tree['columns'] = ('1', '2', '3')

        comprobacion_tree['show'] = 'headings'

        comprobacion_tree.heading('1', text='Concepto')
        comprobacion_tree.heading('2', text='Comprobado')
        comprobacion_tree.heading('3', text='Autorizado')

        comprobacion_tree.column('1', width=90)
        comprobacion_tree.column('2', width=90)
        comprobacion_tree.column('3', width=90)

        folio_lbl.place(relx=1 / 24, rely=2 / 11)
        folio_entry.place(relx=2 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=3 / 24, rely=2 / 11)
        operador_n_lbl.place(relx=5/24, rely=2/11)
        operador_n_entry.place(relx=7/24, rely=2/11)
        operador_entry.place(relx=8/24, rely=2/11)

        fecha_inicio_lbl.place(relx=11/24, rely=2/11)
        fecha_inicio_entry.place(relx=13/24, rely=2/11)
        fecha_cierre_lbl.place(relx=15/24, rely=2/11)
        fecha_cierre_entry.place(relx=17/24, rely=2/11)
        total_btn.place(relx=20/24, rely=2/11)
        total_entry.place(relx=22/24, rely=2/11)

        ordenes_lbl.place(relx=3/24, rely=3/11)
        anticipos_lbl.place(relx=12 / 24, rely=3 / 11)
        comprobacion_lbl.place(relx=20/24, rely=3/11)

        serie_orden_lbl.place(relx=1/50, rely=4/11)
        serie_orden_entry.place(relx=5/100, rely=4/11)
        folio_orden_lbl.place(relx=7/100, rely=4/11)
        folio_orden_entry.place(relx=10/100, rely=4/11)
        comision_lbl.place(relx=6/50, rely=4/11)
        comision_entry.place(relx=9/50, rely=4/11)
        anadir_orden_btn.place(relx=11/50, rely=4/11)
        serie_anticipo_lbl.place(relx=9 / 24, rely=4 / 11)
        serie_anticipo_entry.place(relx=10 / 24, rely=4 / 11)
        folio_anticipo_lbl.place(relx=11 / 24, rely=4 / 11)
        folio_anticipo_entry.place(relx=12 / 24, rely=4 / 11)
        anadir_anticipo_btn.place(relx=14 / 24, rely=4 / 11)
        comp_concepto_box.place(relx=38/50, rely=4/11)
        comprobado_entry.place(relx=42/50, rely=4/11)
        autorizado_entry.place(relx=44/50, rely=4/11)
        anadir_comp_btn.place(relx=46/50, rely=4/11)

        ordenes_tree.place(relx=1 / 50, rely=5/11)
        anticipos_tree.place(relx=18 / 50, rely=5 / 11)
        comprobacion_tree.place(relx=38 / 50, rely=5/11)

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        # TODO FUNCIONES SELECCIONAR GUARDAR Y CANCELAR

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Liquidaciones
                        WHERE folio =%s"""

                c.execute(stmt, folio_entry.get())
                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                operador_n_entry.delete(0, tk.END)
                fecha_inicio_entry.delete(0, tk.END)
                fecha_cierre_entry.delete(0, tk.END)
                operador_n_entry.insert(0, datos[3])
                fecha_inicio_entry.insert(0, datos[1])
                fecha_cierre_entry.insert(0, datos[2])
                total_entry.configure(state='normal')
                total_entry.delete(0, tk.END)
                total_entry.insert(0, datos[4])
                total_entry.configure(state='disabled')

                stmt = """SELECT fecha, serie, folio, n_empleado, comision
                        FROM Ordenes
                        WHERE liquidacion = %s"""

                c.execute(stmt, folio_entry.get())
                query = c.fetchall()

                ordenes_tree.delete(*ordenes_tree.get_children())

                for fila in query:
                    ordenes_tree.insert("", 'end', values=fila)

                stmt = """SELECT fecha, serie, folio, n_empleado, concepto, importe
                        FROM Anticipos
                        WHERE liquidacion = %s"""

                c.execute(stmt, folio_entry.get())
                query = c.fetchall()

                anticipos_tree.delete(*anticipos_tree.get_children())

                for fila in query:
                    anticipos_tree.insert("", 'end', values=fila)

                comprobacion_tree.delete(*comprobacion_tree.get_children())

            finally:
                c.close()

        def insertar_siguiente():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()
                c.execute("""SELECT folio
                            FROM Liquidaciones
                            ORDER BY folio DESC""")
                query = c.fetchone()
                folio_entry.insert(0, query[0]+1)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def operador_n_focusout(event):
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = ("""SELECT nombres, apellido1, apellido2
                            FROM Personal
                            WHERE n_empleado = %s""")
                c.execute(stmt, operador_n_entry.get())

                query = c.fetchone()

                operador_entry.configure(state='normal')
                operador_entry.delete(0, tk.END)
                operador_entry.insert(0, query[0] + ' ' + query[1] + ' ' + query[2])

            finally:
                operador_entry.configure(state='disabled')
                c.close()

        def calcular_total():
            comision = 0
            anticipos = 0
            comprobacion = 0

            for renglon in ordenes_tree.get_children():
                comision += float(ordenes_tree.item(renglon)['values'][-1])

            for renglon in anticipos_tree.get_children():
                anticipos += float(anticipos_tree.item(renglon)['values'][-1])

            for renglon in comprobacion_tree.get_children():
                comprobacion += float(comprobacion_tree.item(renglon)['values'][1])

            total = comision + (comprobacion - anticipos)

            total_entry.configure(state='normal')
            total_entry.delete(0, tk.END)
            total_entry.insert(0, total)
            total_entry.configure(state='readonly')

        def pdf_gen():
            comision = 0
            anticipos = 0
            comprobacion = 0

            for renglon in ordenes_tree.get_children():
                comision += float(ordenes_tree.item(renglon)['values'][-1])

            for renglon in anticipos_tree.get_children():
                anticipos += float(anticipos_tree.item(renglon)['values'][-1])

            for renglon in comprobacion_tree.get_children():
                comprobacion += float(comprobacion_tree.item(renglon)['values'][1])

            total = comision + comprobacion - anticipos

            # DIBUJAR PDF
            x = 15

            liquidacion = Canvas('liquidacion.pdf', pagesize=LETTER)
            liquidacion.setFont('Helvetica', 8)

            liquidacion.drawString(x, 760, 'Folio de Liquidación: ' + folio_entry.get())
            liquidacion.drawString(x, 745, 'Operador: ' + operador_entry.get())
            liquidacion.drawString(x, 730, 'Fecha de Inicio: ' + fecha_inicio_entry.get())
            liquidacion.drawString(x+150, 730, 'Fecha de Cierre: ' + fecha_cierre_entry.get())

            liquidacion.drawString(x, 700, 'Viajes:')

            i = 700
            for fila in ordenes_tree.get_children():
                i += -15
                liquidacion.drawString(x, i, str(ordenes_tree.item(fila)['values'][0]) + '   ' +
                                       str(ordenes_tree.item(fila)['values'][1]) + ' - ' +
                                       str(ordenes_tree.item(fila)['values'][2]) + '   $' +
                                       str(ordenes_tree.item(fila)['values'][4]))

            i += -20
            liquidacion.drawString(x, i, 'Total Viajes: $' + str(comision))

            i += -30
            liquidacion.drawString(x, i, 'Anticipos:')

            for fila in anticipos_tree.get_children():
                i += -15
                liquidacion.drawString(x, i, str(anticipos_tree.item(fila)['values'][0]) + '   ' +
                                       str(anticipos_tree.item(fila)['values'][1]) + ' - ' +
                                       str(anticipos_tree.item(fila)['values'][2]) + ' ' +
                                       str(anticipos_tree.item(fila)['values'][4]) + '   $' +
                                       str(anticipos_tree.item(fila)['values'][5]))
            i += -20
            liquidacion.drawString(x, i, 'Total Anticipos: $' + str(anticipos))

            i += -30
            liquidacion.drawString(x, i, 'Comprobación:')

            i += -15
            liquidacion.drawString(x, i, 'Concepto')
            liquidacion.drawString(x+75, i, 'Comprobado')
            liquidacion.drawString(x+125, i, 'Autorizado')

            for fila in comprobacion_tree.get_children():
                i += -15
                liquidacion.drawString(x, i, comprobacion_tree.item(fila)['values'][0])
                liquidacion.drawString(x+75, i, '$ ' + str(comprobacion_tree.item(fila)['values'][1]))
                liquidacion.drawString(x+125, i, '$ ' + str(comprobacion_tree.item(fila)['values'][2]))

            i += -20
            liquidacion.drawString(x, i, 'Total Comprobación : $' + str(comprobacion))

            i += -50
            liquidacion.drawString(x, i, 'Total a Pagar: $' + str(total))

            liquidacion.save()
            startfile('liquidacion.pdf')

        def abrir_lista():

            ventana_lista = tk.Toplevel()
            ventana_lista.minsize(width=1000, height=560)
            ventana_lista.maxsize(width=1000, height=560)

            busqueda_frame = tk.Frame(ventana_lista)
            busqueda_frame.pack(pady=10)

            lista_frame = tk.Label(ventana_lista)
            lista_frame.pack()

            criterios_lbl = tk.Label(busqueda_frame, text='Criterio de Busqueda:')
            criterios_lbl.grid(column=0, row=0)

            criterios_busqueda_box = ttk.Combobox(busqueda_frame)
            criterios_busqueda_box.grid(column=1, row=0)

            buscar_lbl = tk.Label(busqueda_frame, text='Buscar:')
            buscar_lbl.grid(column=2, row=0, padx=(10, 0))

            buscar_entry = tk.Entry(busqueda_frame)
            buscar_entry.grid(column=3, row=0)

            scroll0 = tk.Scrollbar(ventana_lista, orient='horizontal')
            scroll0.pack(fill='x')

            lista_busqueda = ttk.Treeview(lista_frame, height=5, xscrollcommand=scroll0.set)
            lista_busqueda.pack()

            tabla_frame = tk.Frame(ventana_lista)
            tabla_frame.pack()

            scrollbar = tk.Scrollbar(ventana_lista, orient='horizontal')
            scrollbar.pack(side='bottom', fill='x')

            lista = ttk.Treeview(tabla_frame, height=15, xscrollcommand=scrollbar.set)
            lista.pack(padx=10, pady=10)

            scroll0.configure(command=lista_busqueda.xview)
            scrollbar.configure(command=lista.xview)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute('DESCRIBE Liquidaciones')
                query = c.fetchall()

                columnas = []
                for campo in query:
                    columnas.append(campo[0])

                criterios_busqueda_box.configure(values=columnas, state='readonly')

                lista_busqueda.configure(columns=columnas)
                lista_busqueda['show'] = 'headings'

                lista.configure(columns=columnas)
                lista['show'] = 'headings'

                for columna in columnas:
                    lista.heading(columna, text=columna)
                    lista.column(columna, minwidth=100, width=100, stretch='no')
                    lista_busqueda.heading(columna, text=columna)
                    lista_busqueda.column(columna, minwidth=100, width=100, stretch='no')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                           FROM Liquidaciones
                           ORDER BY folio DESC""")
                query = c.fetchall()

                for fila in query:
                    lista.insert("", 'end', values=fila)

            finally:
                c.close()

            def release_busqueda(event):
                try:
                    lista_busqueda.delete(*lista_busqueda.get_children())

                finally:
                    pass

                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    c.execute("SELECT * FROM Liquidaciones WHERE " + criterios_busqueda_box.get() + "= " + "'" +
                              buscar_entry.get() + "'" + "")

                    query = c.fetchall()

                    for renglon in query:
                        lista_busqueda.insert("", 'end', values=renglon)

                finally:
                    c.close()

            def click_header(event):

                n_columna = lista.identify_column(event.x).replace('#', '')

                if lista.identify('region', event.x, event.y) == 'heading':
                    try:
                        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                        c = db.cursor()

                        c.execute("SELECT * FROM Liquidaciones ORDER BY " + columnas[int(n_columna) - 1] + " DESC")

                        query = c.fetchall()

                        lista.delete(*lista.get_children())

                        for renglon in query:
                            lista.insert("", 'end', values=renglon)

                    finally:
                        c.close()

            def pdf_busqueda():

                busqueda = Canvas('busqueda.pdf', pagesize=LETTER)
                busqueda.setFont('Helvetica', 8)
                x = 8
                for columna in columnas:
                    busqueda.drawString(x, 760, columna)
                    x += 80

                x = 8
                y = 750
                for fila in lista_busqueda.get_children():
                    for columna in lista_busqueda.item(fila)['values']:
                        busqueda.drawString(x, y, str(columna))
                        x += 80
                    x = 8
                    y += -10

                busqueda.save()
                startfile('busqueda.pdf')

            pdf_btn2 = tk.Button(lista_frame, text='.PDF', image=pdf_icono, command=pdf_busqueda)
            pdf_btn2.pack(pady=5)
            buscar_entry.bind('<Return>', release_busqueda)
            lista.bind('<Button-1>', click_header)

        def anadir_orden():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT fecha, serie, folio, n_empleado
                           FROM Ordenes
                           WHERE serie = %s AND folio = %s"""

                c.execute(stmt, (serie_orden_entry.get(), folio_orden_entry.get()))
                query = c.fetchone()

                ordenes_tree.insert("", 'end', values=(query[0], query[1], query[2], query[2], comision_entry.get()))

                serie_orden_entry.delete(0, tk.END)
                folio_orden_entry.delete(0, tk.END)
                comision_entry.delete(0, tk.END)

            finally:
                c.close()

        def anadir_anticipo():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT fecha, serie, folio, n_empleado, concepto, importe
                        FROM Anticipos
                        WHERE serie = %s AND folio = %s"""

                c.execute(stmt, (serie_anticipo_entry.get(), folio_anticipo_entry.get()))
                query = c.fetchone()

                #                  "",ULTMO RENGLON, values = (col1, col2,..., coln)
                anticipos_tree.insert("", 'end', values=query)

                serie_anticipo_entry.delete(0, tk.END)
                folio_anticipo_entry.delete(0, tk.END)

            finally:
                c.close

        def anadir_comp():

            comprobacion_tree.insert("", 'end', values=(comp_concepto_box.get(), comprobado_entry.get(),
                                                        autorizado_entry.get()))

            comp_concepto_box.delete(0, tk.END)
            comprobado_entry.delete(0, tk.END)
            autorizado_entry.delete(0, tk.END)

        # TODO EXCEPCIONES

        def guardar():
            lista = [folio_entry.get(), operador_n_entry.get(), fecha_inicio_entry.get(), fecha_cierre_entry.get(),
                     total_entry.get()]
            datos = []
            for dato in lista:
                if dato == '':
                    dato = None
                datos.append(dato)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT folio
                        FROM Liquidaciones
                        WHERE folio = %s"""

                c.execute(stmt, folio_entry.get())
                query = c.fetchone()

                c.close()

                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                if query is not None:
                    query = query[0]

                if query is None:
                    mensaje = messagebox.askyesno('Liquidación Inexistente', 'La Liquidación %s no existe. ¿Desea darla'
                                                                             ' de alta?' % folio_entry.get())
                    if mensaje is True:
                        try:
                            stmt = """INSERT INTO Liquidaciones (folio, fecha_inicio, fecha_cierre, n_empleado, importe)
                                                               VALUES (%s,%s,%s,%s,%s)"""
                            c.execute(stmt, (folio_entry.get(), fecha_inicio_entry.get(), fecha_cierre_entry.get(),
                                             datos[1], datos[-1]))

                            db.commit()
                            for fila in ordenes_tree.get_children():
                                try:
                                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                                    c = db.cursor()

                                    stmt = """SELECT liquidacion
                                           FROM Ordenes
                                           WHERE serie = %s AND folio = %s"""
                                    c.execute(stmt, (ordenes_tree.item(fila)['values'][1],
                                                     ordenes_tree.item(fila)['values'][2]))

                                    query = c.fetchone()

                                    if query[0] is not None and query[0] != int(folio_entry.get()):
                                        mensaje = messagebox.askyesno('Orden Asignada', 'La Orden %s - %s esta '
                                                'asignada a la liquidacion %s. ¿Desea reasignarla a la Liquidacion %s?'
                                                                      % (ordenes_tree.item(fila)['values'][1],
                                                                         ordenes_tree.item(fila)['values'][2], query[0],
                                                                         folio_entry.get()))

                                        if mensaje is True:
                                            stmt = """UPDATE Ordenes
                                                   SET liquidacion = %s,
                                                       comision = %s
                                                   WHERE serie = %s AND folio = %s"""

                                            c.execute(stmt, (folio_entry.get(), ordenes_tree.item(fila)['values'][4],
                                                             ordenes_tree.item(fila)['values'][1],
                                                             ordenes_tree.item(fila)['values'][2]))

                                            db.commit()
                                        else:
                                            pass
                                    else:
                                        stmt = """UPDATE Ordenes
                                               SET liquidacion = %s,
                                                   comision = %s
                                               WHERE serie = %s AND folio = %s"""

                                        c.execute(stmt, (folio_entry.get(), ordenes_tree.item(fila)[4]['values'],
                                                         ordenes_tree.item(fila)['values'][1],
                                                         ordenes_tree.item(fila)['values'][2]))

                                        db.commit()

                                finally:
                                    c.close()

                            for fila in anticipos_tree.get_children():
                                try:
                                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                                    c = db.cursor()

                                    stmt = """SELECT liquidacion
                                           FROM Anticipos
                                           WHERE serie = %s AND folio = %s"""
                                    c.execute(stmt, (anticipos_tree.item(fila)['values'][1],
                                                     anticipos_tree.item(fila)['values'][2]))

                                    query = c.fetchone()

                                    if query[0] is not None and query[0] != int(folio_entry.get()):
                                        mensaje = messagebox.askyesno('Anticipo Asignado', 'El Anticipo %s - %s esta '
                                               'asignado a la liquidacion %s. ¿Desea reasignarlo a la Liquidacion %s?'
                                                                      % (anticipos_tree.item(fila)['values'][1],
                                                                         anticipos_tree.item(fila)['values'][2],
                                                                         query[0],
                                                                         folio_entry.get()))

                                        if mensaje is True:
                                            stmt = """UPDATE Anticipos
                                                   SET liquidacion = %s
                                                   WHERE serie = %s AND folio = %s"""

                                            c.execute(stmt, (folio_entry.get(), anticipos_tree.item(fila)['values'][1],
                                                             anticipos_tree.item(fila)['values'][2]))

                                            db.commit()
                                    else:
                                        stmt = """UPDATE Anticipos
                                               SET liquidacion = %s
                                               WHERE serie = %s AND folio = %s"""

                                        c.execute(stmt, (folio_entry.get(), anticipos_tree.item(fila)['values'][1],
                                                         anticipos_tree.item(fila)['values'][2]))

                                        db.commit()

                                finally:
                                    c.close()

                            cancelar()

                        finally:
                            c.close()

                elif query == int(folio_entry.get()):
                    mensaje = messagebox.askyesno('Liquidacion Existe', 'La liquidacion %s ya existe. ¿Desea guardar '
                                                                        'los cambios?' % folio_entry.get())
                    if mensaje is True:
                        try:
                            stmt = """UPDATE Liquidaciones
                                    SET fecha_inicio = %s,
                                        fecha_cierre = %s,
                                        n_empleado = %s,
                                        importe = %s
                                    WHERE folio = %s"""
                            c.execute(stmt, (fecha_inicio_entry.get(), fecha_cierre_entry.get(), datos[1],
                                             datos[-1], datos[0]))

                            db.commit()

                            for fila in ordenes_tree.get_children():
                                try:
                                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                                    c = db.cursor()

                                    stmt = """SELECT liquidacion
                                            FROM Ordenes
                                            WHERE serie = %s AND folio = %s"""
                                    c.execute(stmt, (ordenes_tree.item(fila)['values'][1],
                                                     ordenes_tree.item(fila)['values'][2]))

                                    query = c.fetchone()
                                    print(query[0])

                                    if query[0] is not None and query[0] != int(folio_entry.get()):
                                        mensaje = messagebox.askyesno('Orden Asignada', 'La Orden %s - %s está '
                                                 'asignada a la liquidacion %s. ¿Desea reasignarla a la Liquidación %s?'
                                                  % (ordenes_tree.item(fila)['values'][1],
                                                     ordenes_tree.item(fila)['values'][2], query[0], folio_entry.get()))

                                        if mensaje is True:
                                            stmt = """UPDATE Ordenes
                                                    SET liquidacion = %s,
                                                        comision = %s
                                                    WHERE serie = %s AND folio = %s"""

                                            c.execute(stmt, (folio_entry.get(), ordenes_tree.item(fila)['values'][4],
                                                             ordenes_tree.item(fila)['values'][1],
                                                             ordenes_tree.item(fila)['values'][2]))

                                            db.commit()

                                    else:
                                        stmt = """UPDATE Ordenes
                                                SET liquidacion = %s,
                                                    comision = %s
                                                WHERE serie = %s AND folio = %s"""

                                        c.execute(stmt, (folio_entry.get(), ordenes_tree.item(fila)['values'][4],
                                                         ordenes_tree.item(fila)['values'][1],
                                                         ordenes_tree.item(fila)['values'][2]))

                                        db.commit()

                                finally:
                                    c.close()
                            for fila in anticipos_tree.get_children():
                                try:
                                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                                    c = db.cursor()

                                    stmt = """SELECT liquidacion
                                            FROM Anticipos
                                            WHERE serie = %s AND folio = %s"""
                                    c.execute(stmt, (anticipos_tree.item(fila)['values'][1],
                                                     anticipos_tree.item(fila)['values'][2]))

                                    query = c.fetchone()

                                    if query[0] is not None and query[0] != int(folio_entry.get()):
                                        mensaje = messagebox.askyesno('Anticipo Asignado', 'El Anticipo %s - %s esta '
                                                'asignado a la liquidacion %s. ¿Desea reasignarlo a la Liquidacion %s?'
                                                                  % (anticipos_tree.item(fila)['values'][1],
                                                                     anticipos_tree.item(fila)['values'][2], query[0],
                                                                     folio_entry.get()))

                                        if mensaje is True:
                                            stmt = """UPDATE Anticipos
                                                    SET liquidacion = %s
                                                    WHERE serie = %s AND folio = %s"""

                                            c.execute(stmt, (folio_entry.get(), anticipos_tree.item(fila)['values'][1],
                                                             anticipos_tree.item(fila)['values'][2]))

                                            db.commit()
                                        else:
                                            pass
                                    else:
                                        stmt = """UPDATE Anticipos
                                                SET liquidacion = %s
                                                WHERE serie = %s AND folio = %s"""

                                        c.execute(stmt, (folio_entry.get(), anticipos_tree.item(fila)['values'][1],
                                                         anticipos_tree.item(fila)['values'][2]))

                                        db.commit()
                                finally:
                                    c.close()

                            cancelar()
                        finally:
                            c.close()
            finally:
                c.close()

        def cancelar():
                folio_entry.delete(0, tk.END)
                fecha_inicio_entry.delete(0, tk.END)
                fecha_cierre_entry.delete(0, tk.END)
                serie_anticipo_entry.delete(0, tk.END)
                folio_anticipo_entry.delete(0, tk.END)
                comision_entry.delete(0, tk.END)
                serie_orden_entry.delete(0, tk.END)
                folio_orden_entry.delete(0, tk.END)
                comp_concepto_box.delete(0, tk.END)
                comprobado_entry.delete(0, tk.END)
                autorizado_entry.delete(0, tk.END)
                ordenes_tree.delete(*ordenes_tree.get_children())
                anticipos_tree.delete(*anticipos_tree.get_children())
                comprobacion_tree.delete(*comprobacion_tree.get_children())
                total_entry.configure(state='normal')
                total_entry.delete(0, tk.END)
                total_entry.configure(state='disabled')
                operador_n_entry.delete(0, tk.END)
                operador_entry.configure(state='normal')
                operador_entry.delete(0, tk.END)
                operador_entry.configure(state='readonly')
                fecha_inicio_entry.insert(0, date.today())
                fecha_cierre_entry.insert(0, date.today())

                insertar_siguiente()

        insertar_siguiente()

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        operador_n_entry.bind('<FocusOut>', operador_n_focusout)

        lista_btn = tk.Button(self, text='Lista de Liquidaciones')
        lista_btn.place(relx=1 / 50, rely=9 / 10)
        lista_btn.configure(relief='flat', bg='white', bd=1, command=abrir_lista)

        pdf_btn = tk.Button(self, text='.PDF', image=pdf_icono, command=pdf_gen)
        pdf_btn.place(relx=8 / 16, rely=12 / 13, anchor='center')

        seleccionar_btn.configure(command=seleccionar)
        total_btn.configure(command=calcular_total)
        anadir_orden_btn.configure(command=anadir_orden)
        anadir_anticipo_btn.configure(command=anadir_anticipo)
        anadir_comp_btn.configure(command=anadir_comp)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Anticipos(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        global pdf_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)
        pdf_icono = self.image2 = ImageTk.PhotoImage(pdf_img)

        titulo = tk.Label(self, text='Anticipos', font='Segoe 12 bold')

        serie_lbl = tk.Label(self, text='Serie')
        serie_entry = tk.Entry(self, width=3)
        folio_lbl = tk.Label(self, text='Folio')
        folio_entry = tk.Entry(self, width=5)
        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)

        fecha_lbl = tk.Label(self, text='Fecha')
        fecha_entry = tk.Entry(self, width=10)

        fecha_entry.insert(0, date.today())

        operador_n_lbl = tk.Label(self, text='No. de Operador')
        operador_n_entry = tk.Entry(self, width=3)
        operador_box = ttk.Combobox(self, width=17)
        unidad_lbl = tk.Label(self, text='Unidad')
        unidad_entry = tk.Entry(self, width=3)

        concepto_lbl = tk.Label(self, text='Concepto')
        concepto_txt = tk.Text(self, width=25, height=3)

        importe_lbl = tk.Label(self, text='Importe')
        importe_entry = tk.Entry(self, width=9)

        imprimir_lbl = tk.Label(self, text='Imprimir')

        fecha_inicio_lbl = tk.Label(self, text='Fecha de Inicio')
        fecha_inicio_entry = tk.Entry(self, width=10)
        fecha_cierre_lbl = tk.Label(self, text='Fecha de Cierre')
        fecha_cierre_entry = tk.Entry(self, width=10)

        pdf_btn = tk.Button(self, image=pdf_icono)

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        serie_lbl.place(relx=7/24, rely=2/11)
        serie_entry.place(relx=8/24, rely = 2/11)
        folio_lbl.place(relx=9 / 24, rely=2 / 11)
        folio_entry.place(relx=10 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=11 / 24, rely=2 / 11)
        fecha_lbl.place(relx=14 / 24, rely=2 / 11)
        fecha_entry.place(relx=15 / 24, rely=2 / 11)

        operador_n_lbl.place(relx=7 / 24, rely=3 / 11)
        operador_n_entry.place(relx=9 / 24, rely=3 / 11)
        operador_box.place(relx=10 / 24, rely=3 / 11)
        unidad_lbl.place(relx=14 / 24, rely=3 / 11)
        unidad_entry.place(relx=15 / 24, rely=3 / 11)

        concepto_lbl.place(relx=7 / 24, rely=4 / 11)
        concepto_txt.place(relx=9 / 24, rely=4 / 11)

        importe_lbl.place(relx=10 / 24, rely=6 / 11)
        importe_entry.place(relx=11 / 24, rely=6 / 11)

        imprimir_lbl.place(relx=11/24, rely=7/11)

        fecha_inicio_lbl.place(relx=7/24, rely=8/11)
        fecha_inicio_entry.place(relx=9/24, rely=8/11)
        fecha_cierre_lbl.place(relx=11/24, rely=8/11)
        fecha_cierre_entry.place(relx=13/24, rely=8/11)

        pdf_btn.place(relx=11/24, rely=9/11)

        # FUNCIONES DE BOTONES

        def pdf_gen():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Anticipos
                        WHERE fecha BETWEEN %s and %s"""

                c.execute(stmt, (fecha_inicio_entry.get(), fecha_cierre_entry.get()))
                query = c.fetchall()

                anticipos = Canvas('anticipos.pdf', pagesize=LETTER)

                x = 0
                y = 592.5
                for anticipo in query:

                    c.execute("""SELECT nombres, apellido1, apellido2
                                FROM PERSONAL
                                WHERE n_empleado = %s""", anticipo[4])

                    nombre = c.fetchone()

                    anticipos.roundRect(x, y, 305, 197.5, radius=3)
                    anticipos.drawString(x+5, y+180, str(anticipo[0]) + ' - ' + str(anticipo[1]))
                    anticipos.drawString(x+240, y+180, str(anticipo[2]))
                    anticipos.drawCentredString(x+305/2, y+140, nombre[0] + ' ' + nombre[1] + ' ' + nombre[2])
                    anticipos.drawCentredString(x+305/2, y+120, anticipo[6])
                    anticipos.drawString(x+240, y+20, '$' + ' ' + str(anticipo[7]))

                    x += 305
                    if x == 610:
                        y += -197.5
                        x = 0

                    if y < 0:
                        anticipos.showPage()
                        x = 0
                        y = 592.5

                anticipos.save()
                startfile('anticipos.pdf')

            finally:
                c.close()

        def abrir_lista():

            ventana_lista = tk.Toplevel()
            ventana_lista.minsize(width=1000, height=560)
            ventana_lista.maxsize(width=1000, height=560)

            busqueda_frame = tk.Frame(ventana_lista)
            busqueda_frame.pack(pady=10)

            lista_frame = tk.Label(ventana_lista)
            lista_frame.pack()

            criterios_lbl = tk.Label(busqueda_frame, text='Criterio de Busqueda:')
            criterios_lbl.grid(column=0, row=0)

            criterios_busqueda_box = ttk.Combobox(busqueda_frame)
            criterios_busqueda_box.grid(column=1, row=0)

            buscar_lbl = tk.Label(busqueda_frame, text='Buscar:')
            buscar_lbl.grid(column=2, row=0, padx=(10, 0))

            buscar_entry = tk.Entry(busqueda_frame)
            buscar_entry.grid(column=3, row=0)

            scroll0 = tk.Scrollbar(ventana_lista, orient='horizontal')
            scroll0.pack(fill='x')

            lista_busqueda = ttk.Treeview(lista_frame, height=5, xscrollcommand=scroll0.set)
            lista_busqueda.pack()

            tabla_frame = tk.Frame(ventana_lista)
            tabla_frame.pack()

            scrollbar = tk.Scrollbar(ventana_lista, orient='horizontal')
            scrollbar.pack(side='bottom', fill='x')

            lista = ttk.Treeview(tabla_frame, height=15, xscrollcommand=scrollbar.set)
            lista.pack(padx=10, pady=10)

            scroll0.configure(command=lista_busqueda.xview)
            scrollbar.configure(command=lista.xview)

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute('DESCRIBE Anticipos')
                query = c.fetchall()

                columnas = []
                for campo in query:
                    columnas.append(campo[0])

                criterios_busqueda_box.configure(values=columnas, state='readonly')

                lista_busqueda.configure(columns=columnas)
                lista_busqueda['show'] = 'headings'

                lista.configure(columns=columnas)
                lista['show'] = 'headings'

                for columna in columnas:
                    lista.heading(columna, text=columna)
                    lista.column(columna, minwidth=100, width=100, stretch='no')
                    lista_busqueda.heading(columna, text=columna)
                    lista_busqueda.column(columna, minwidth=100, width=100, stretch='no')

            finally:
                c.close()

            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                          FROM Anticipos
                          ORDER BY folio DESC""")
                query = c.fetchall()

                for fila in query:
                    lista.insert("", 'end', values=fila)

            finally:
                c.close()

            def release_busqueda(event):
                try:
                    lista_busqueda.delete(*lista_busqueda.get_children())

                finally:
                    pass

                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    c.execute("SELECT * FROM Anticipos WHERE " + criterios_busqueda_box.get() + "= " + "'" +
                              buscar_entry.get() + "'" + "")

                    query = c.fetchall()

                    for renglon in query:
                        lista_busqueda.insert("", 'end', values=renglon)

                finally:
                    c.close()

            def click_header(event):
                n_columna = lista.identify_column(event.x).replace('#', '')

                if lista.identify('region', event.x, event.y) == 'heading':
                    try:

                        db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                        c = db.cursor()

                        c.execute("SELECT * FROM Anticipos ORDER BY " + columnas[int(n_columna) - 1] + " DESC")

                        query = c.fetchall()

                        lista.delete(*lista.get_children())

                        for renglon in query:
                            lista.insert("", 'end', values=renglon)

                    finally:
                        c.close()

            def pdf_busqueda():

                busqueda = Canvas('busqueda.pdf', pagesize=LETTER)
                busqueda.setFont('Helvetica', 8)
                x = 8
                for columna in columnas:
                    busqueda.drawString(x, 760, columna)
                    x += 80

                x = 8
                y = 750
                for fila in lista_busqueda.get_children():
                    for columna in lista_busqueda.item(fila)['values']:
                        busqueda.drawString(x, y, str(columna))
                        x += 80
                    x = 8
                    y += -10

                busqueda.save()
                startfile('busqueda.pdf')

            pdf_btn2 = tk.Button(lista_frame, text='.PDF', image=pdf_icono, command=pdf_busqueda)
            pdf_btn2.pack(pady=5)

            buscar_entry.bind('<Return>', release_busqueda)
            lista.bind('<Button-1>', click_header)

        def poblar_operador_box():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT nombres, apellido1, apellido2
                            FROM Personal
                            ORDER BY nombres ASC""")

                query = c.fetchall()

                empleados = []
                i = 0
                for empleado in query:
                    empleados.append(query[i][0] + ' ' + query[i][1] + ' ' + query[i][2])
                    i += 1

                operador_box.configure(values=empleados)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close

        def insertar_siguiente():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT serie, folio 
                            FROM Anticipos
                            ORDER BY folio DESC""")

                query = c.fetchone()
                serie_entry.insert(0, query[0])
                folio_entry.insert(0, query[1]+1)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = ("""SELECT fecha, n_empleado, n_economico, concepto, importe
                            FROM Anticipos
                            WHERE serie = %s AND folio = %s""")

                c.execute(stmt, (serie_entry.get(), folio_entry.get()))

                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                fecha_entry.delete(0, tk.END)
                operador_n_entry.delete(0, tk.END)
                operador_box.delete(0, tk.END)
                unidad_entry.delete(0, tk.END)
                concepto_txt.delete(1.0, tk.END)
                importe_entry.delete(0, tk.END)

                fecha_entry.insert(0, datos[0])
                operador_n_entry.insert(0, datos[1])

                unidad_entry.insert(0, datos[2])
                concepto_txt.insert(1.0, datos[3])
                importe_entry.insert(0, datos[4])

                stmt = ("""SELECT nombres, apellido1, apellido2
                            FROM Personal
                            WHERE n_empleado = %s""")

                c.execute(stmt, operador_n_entry.get())

                query = c.fetchone()

                operador_box.insert(0, (query[0] + ' ' + query[1]) + ' ' + query[2])

            finally:
                c.close()

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT serie, folio
                        FROM Anticipos
                        WHERE serie =%s AND folio = %s"""

                c.execute(stmt, (serie_entry.get(), folio_entry.get()))
                query = c.fetchone()

                c.close()

                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                if query is not None and query[0] == serie_entry.get() and query[1] == int(folio_entry.get()):

                    mensaje = messagebox.askyesno('Anticipo Existe', 'El  anticipo %s %s ya existe. '
                                                                     '¿Desea guardar los cambios?'
                                                  % (serie_entry.get(), folio_entry.get()))

                    if mensaje is True:
                        try:
                            stmt = """UPDATE Anticipos 
                                        SET fecha = %s, 
                                            n_empleado = %s, 
                                            n_economico = %s, 
                                            concepto = %s, 
                                            importe = %s
                                        WHERE serie = %s AND folio =%s """

                            c.execute(stmt, (fecha_entry.get(), operador_n_entry.get(), unidad_entry.get(),
                                             concepto_txt.get(1.0, 'end-1c'), importe_entry.get(), serie_entry.get(),
                                      folio_entry.get()))

                            db.commit()

                            serie_entry.delete(0, tk.END)
                            folio_entry.delete(0, tk.END)
                            fecha_entry.delete(0, tk.END)
                            operador_n_entry.delete(0, tk.END)
                            operador_box.delete(0, tk.END)
                            unidad_entry.delete(0, tk.END)
                            concepto_txt.delete(1.0, tk.END)
                            importe_entry.delete(0, tk.END)
                            fecha_entry.insert(0, date.today())

                            insertar_siguiente()

                        finally:
                            db.commit()
                            c.close()

                else:
                    mensaje = messagebox.askyesno('Anticipo Inexistente', 'El anticipo %s %s no existe. '
                                                                          '¿Desea darlo de alta ?' % (serie_entry.get(), folio_entry.get()))

                    if mensaje is True:
                        try:
                            stmt = """INSERT INTO Anticipos (serie, folio, fecha, n_empleado, n_economico, concepto, importe) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""

                            c.execute(stmt, (serie_entry.get(), folio_entry.get(), fecha_entry.get(),
                                             operador_n_entry.get(), unidad_entry.get(),
                                             concepto_txt.get(1.0, 'end-1c'), importe_entry.get()))

                            serie_entry.delete(0, tk.END)
                            folio_entry.delete(0, tk.END)
                            fecha_entry.delete(0, tk.END)
                            operador_n_entry.delete(0, tk.END)
                            unidad_entry.delete(0, tk.END)
                            concepto_txt.delete(1.0, tk.END)
                            importe_entry.delete(0, tk.END)

                            fecha_entry.insert(0, date.today())

                            db.commit()

                            insertar_siguiente()

                        finally:
                            db.commit()
                            c.close()

            # except ValueError:
            #     messagebox.showerror('Error!', 'El folio solo puede ser compuesto por caracteres numéricos.')
            #
            # except TypeError:
            #     messagebox.showerror('Error!', 'El folio solo puede ser compuesto por caracteres numéricos.')

            finally:
                db.commit()
                c.close()

        def focusout_operador_n(event):
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT nombres, apellido1, apellido2
                            FROM Personal
                            WHERE n_empleado = %s"""
                c.execute(stmt, operador_n_entry.get())

                query = c.fetchone()
                operador_box.delete(0, tk.END)
                operador_box.insert(0, query[0] + ' ' + query[1] + ' ' + query[2])

            finally:
                c.close()

        def cancelar():
            serie_entry.delete(0, tk.END)
            folio_entry.delete(0, tk.END)
            fecha_entry.delete(0, tk.END)
            fecha_entry.insert(0, date.today())
            operador_n_entry.delete(0, tk.END)
            operador_box.delete(0, tk.END)
            unidad_entry.delete(0, tk.END)
            concepto_txt.delete(1.0, tk.END)
            importe_entry.delete(0, tk.END)

            insertar_siguiente()

        pdf_btn.config(command=pdf_gen)
        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        insertar_siguiente()
        poblar_operador_box()
        operador_n_entry.bind('<FocusOut>', focusout_operador_n)

        lista_btn = tk.Button(self, text='Lista de Anticipos')
        lista_btn.place(relx=1 / 50, rely=9 / 10)
        lista_btn.configure(relief='flat', bg='white', bd=1, command=abrir_lista)

        seleccionar_btn.config(command=seleccionar)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Contenedores(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        titulo = tk.Label(self, text='Contenedores', font='Segoe 12 bold')

        tamano_cont_lbl = tk.Label(self, text='Tamaño')
        tamano_cont_entry = ttk.Combobox(self)
        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)

        ancho_lbl = tk.Label(self, text='Ancho')
        ancho_entry = tk.Entry(self, width=5)

        largo_lbl = tk.Label(self, text='Largo')
        largo_entry = tk.Entry(self, width=5)

        alto_lbl = tk.Label(self, text='Alto')
        alto_entry = tk.Entry(self, width=5)
        peso_lbl = tk.Label(self, text='Peso')
        peso_entry = tk.Entry(self, width=5)

        metros1_lbl = tk.Label(self, text='m')
        metros2_lbl = tk.Label(self, text='m')
        metros3_lbl = tk.Label(self, text='m')
        ton_lbl = tk.Label(self, text='ton')

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        tamano_cont_lbl.place(relx=4 / 24, rely=2 / 11)
        tamano_cont_entry.place(relx=6 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=9/24, rely=2/11)

        ancho_lbl.place(relx=4 / 24, rely=3 / 11)
        ancho_entry.place(relx=6 / 24, rely=3 / 11)
        metros1_lbl.place(relx=7 / 24, rely=3 / 11)

        largo_lbl.place(relx=4 / 24, rely=4 / 11)
        largo_entry.place(relx=6 / 24, rely=4 / 11)
        metros2_lbl.place(relx=7 / 24, rely=4 / 11)

        alto_lbl.place(relx=4 / 24, rely=5 / 11)
        alto_entry.place(relx=6 / 24, rely=5 / 11)
        metros3_lbl.place(relx=7 / 24, rely=5 / 11)

        peso_lbl.place(relx=4/24, rely=6/11)
        peso_entry.place(relx=6 / 24, rely=6 / 11)
        ton_lbl.place(relx=7 / 24, rely=6 / 11)

        # FUNCIONES GUARDAR Y CANCELAR

        def poblar_tamano_box():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT tipo
                            FROM Contenedores""")

                query = c.fetchall()

                contenedores = []
                i = 0

                for tipo in query:
                    contenedores.append(query[i][0])
                    i += 1

                tamano_cont_entry.config(values=contenedores)

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                db.commit()
                c.close()

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT ancho, largo, alto, peso
                        FROM Contenedores
                        WHERE tipo = %s """

                c.execute(stmt, tamano_cont_entry.get())

                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                ancho_entry.delete(0, tk.END)
                largo_entry.delete(0, tk.END)
                alto_entry.delete(0, tk.END)
                peso_entry.delete(0, tk.END)

                ancho_entry.insert(0, datos[0])
                largo_entry.insert(0, datos[1])
                alto_entry.insert(0, datos[2])
                peso_entry.insert(0, datos[3])

            finally:
                db.commit()
                c.close()

        def guardar():
            if tamano_cont_entry.get() != '':
                try:
                    db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                    c = db.cursor()

                    lista = [ancho_entry.get(), largo_entry.get(), alto_entry.get(), peso_entry.get()]
                    datos = []

                    for elemento in lista:
                        if elemento == '':
                            elemento = None
                        datos.append(elemento)

                    stmt = """SELECT tipo 
                               FROM Contenedores 
                               WHERE tipo = %s"""

                    c.execute(stmt, tamano_cont_entry.get())
                    query = c.fetchone()

                    if query is not None:
                        query = query[0]

                    if query == tamano_cont_entry.get():

                        mensaje = messagebox.askyesno('Tipo de Contenedor Existente', 'El tipo de contenedor %s ya existe.'
                                                      ' ¿Desea guardar los cambios?' % tamano_cont_entry.get())

                        if mensaje is True:
                            try:
                                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                                c = db.cursor()

                                stmt = """UPDATE Contenedores
                                        SET ancho = %s,
                                            largo = %s,
                                            alto = %s,
                                            peso = %s
                                        WHERE tipo = %s"""

                                c.execute(stmt, (datos[0], datos[1], datos[2], datos[3], tamano_cont_entry.get()))

                                ancho_entry.delete(0, tk.END)
                                largo_entry.delete(0, tk.END)
                                alto_entry.delete(0, tk.END)
                                peso_entry.delete(0, tk.END)
                                tamano_cont_entry.delete(0, tk.END)

                            finally:
                                db.commit()
                                c.close()

                    else:
                        mensaje = messagebox.askyesno('Tipo Inexistente', ' El tipo de contenedor %s no existe. '
                                                      '¿Desea darlo de alta?' % tamano_cont_entry.get())

                        if mensaje is True:
                            try:
                                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                                c = db.cursor()

                                stmt = """INSERT INTO Contenedores (tipo, ancho, largo, alto, peso)
                                        VALUES (%s,%s,%s,%s,%s)"""

                                c.execute(stmt, (tamano_cont_entry.get(), datos[0], datos[1], datos[2], datos[3]))

                                ancho_entry.delete(0, tk.END)
                                largo_entry.delete(0, tk.END)
                                alto_entry.delete(0, tk.END)
                                peso_entry.delete(0, tk.END)
                                tamano_cont_entry.delete(0, tk.END)

                                db.commit()

                                poblar_tamano_box()

                            finally:
                                db.commit()
                                c.close()

                finally:
                    db.commit()
                    c.close()
            else:
                messagebox.showerror('Tamaño de Contenedor', 'El campo Tamaño de Contenedor no puede ser vacio')

        def cancelar():
            tamano_cont_entry.delete(0, tk.END)
            ancho_entry.delete(0, tk.END)
            largo_entry.delete(0, tk.END)
            alto_entry.delete(0, tk.END)
            peso_entry.delete(0, tk.END)

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        poblar_tamano_box()

        seleccionar_btn.configure(command=seleccionar)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Ciudades(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        titulo = tk.Label(self, text='Ciudades', font='Segoe 12 bold')

        clave_lbl = tk.Label(self, text='Clave de Ciudad')
        clave_entry = tk.Entry(self, width=6)

        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)

        nombre_lbl = tk.Label(self, text='Nombre de Cd.')
        nombre_entry = tk.Entry(self)

        estados = ['Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Coahulia de Zaragoza',
                   'Colima', 'Chiapas', 'Chihuahua', 'Ciudad de México', 'Durango', 'Guanajuato', 'Guerrero', 'Hidalgo',
                   'Jalisco', 'México', 'Michoacán de Ocampo', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla',
                   'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco', 'Tamaulipas',
                   'Tlaxcala', 'Veracruz de Ignacio de la Llvae', 'Yucatán', 'Zacatecas']

        estado_lbl = tk.Label(self, text='Estado')
        estado_box = ttk.Combobox(self, values=estados, state='readonly')

        ciudades_tree = ttk.Treeview(self, columns=('1', '2', '3'))
        ciudades_tree.heading('1', text='Clave')
        ciudades_tree.heading('2', text='Nombre')
        ciudades_tree.heading('3', text='Estado')
        ciudades_tree.column('1', width=65)
        ciudades_tree['show'] = 'headings'

        clave_lbl.place(relx=4 / 24, rely=2 / 11)
        clave_entry.place(relx=6 / 24, rely=2 / 11)
        seleccionar_btn.place(relx=7/24, rely=2/11)

        nombre_lbl.place(relx=4 / 24, rely=3 / 11)
        nombre_entry.place(relx=6 / 24, rely=3 / 11)

        estado_lbl.place(relx=4 / 24, rely=4 / 11)
        estado_box.place(relx=6 / 24, rely=4 / 11)

        ciudades_tree.place(relx=12/24, rely=2/11)

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        # FUNCIONES ALTA Y CANCELAR

        def poblar_ciudades_tree():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Ciudades
                        ORDER BY clave ASC"""

                c.execute(stmt)

                query = c.fetchall()

                ciudades_tree.delete(*ciudades_tree.get_children())

                i = 0
                for ciudad in query:
                    ciudades_tree.insert("", 'end', values=(ciudad[0], ciudad[1], ciudad[2]))
                    i += 1

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Ciudades
                        WHERE CLAVE = %s"""

                c.execute(stmt, clave_entry.get())

                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                nombre_entry.insert(0, datos[1])
                estado_box.configure(state='normal')
                estado_box.insert(0, datos[2])
                estado_box.configure(state='readonly')

            finally:
                c.close()

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT clave
                        FROM Ciudades
                        WHERE CLAVE = %s"""

                c.execute(stmt, clave_entry.get())

                query = c.fetchone()

                if query is not None and query[0] == clave_entry.get():

                    mensaje = messagebox.askyesno('Clave Existente', 'La clave de ciudad %s ya existe, '
                                                                 '¿Desea guradar los cambios?' % clave_entry.get())

                    if mensaje is True:
                        try:
                            stmt = """UPDATE Ciudades
                                    SET nombre = %s,
                                        estado = %s
                                    WHERE clave = %s"""

                            c.execute(stmt, (nombre_entry.get(), estado_box.get(), clave_entry.get()))

                            db.commit()

                            clave_entry.delete(0, tk.END)
                            nombre_entry.delete(0, tk.END)
                            estado_box.configure(state='normal')
                            estado_box.delete(0, tk.END)
                            estado_box.configure(state='readonly')

                            poblar_ciudades_tree()

                        finally:
                            c.close()

                else:
                    mensaje = messagebox.askyesno('Clave Inexistente', 'La clave de ciudad %s no existe, '
                                                                       '¿Desea darla de alta?' % clave_entry.get())
                    if mensaje is True:
                        try:
                            stmt = """INSERT INTO Ciudades (clave, nombre, estado)
                                    VALUES (%s,%s,%s)"""

                            c.execute(stmt, (clave_entry.get(), nombre_entry.get(), estado_box.get()))

                            db.commit()

                            clave_entry.delete(0, tk.END)
                            nombre_entry.delete(0, tk.END)
                            estado_box.configure(state='normal')
                            estado_box.delete(0, tk.END)
                            estado_box.configure(state='readonly')

                            poblar_ciudades_tree()

                        finally:
                            c.close()

            finally:
                c.close()

        def cancelar():
            clave_entry.delete(0, tk.END)
            nombre_entry.delete(0, tk.END)
            estado_box.configure(state='normal')
            estado_box.delete(0, tk.END)
            estado_box.configure(state='readonly')

        poblar_ciudades_tree()

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        seleccionar_btn.configure(command=seleccionar)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class Manteniemiento(Marco):
    def __init__(self, *args, **kwargs):
        Marco.__init__(self, *args, **kwargs)

        global guardar_img
        global cancelar_img
        guardar_icono = self.image0 = ImageTk.PhotoImage(guardar_img)
        cancelar_icono = self.image1 = ImageTk.PhotoImage(cancelar_img)

        titulo = tk.Label(self, text='Mantenimiento', font='Segoe 12 bold')

        id_lbl = tk.Label(self, text='I.D.')
        id_entry = tk.Entry(self, width=4)
        seleccionar_btn = tk.Button(self, text='Seleccionar', font='Segoe 8 bold')
        seleccionar_btn.configure(relief='flat', bg='white', bd=1)
        unidad_lbl = tk.Label(self, text='Unidad')
        unidad_entry = tk.Entry(self, width=3)

        ubicacion_lbl = tk.Label(self, text='Ubicacion')
        ubicacion_entry = tk.Entry(self)

        fecha_inicio_lbl = tk.Label(self, text='Fecha de Inicio')
        fecha_inicio_entry = tk.Entry(self, width=10)
        fecha_cierre_lbl = tk.Label(self, text='Fecha de Cierre')
        fecha_cierre_entry = tk.Entry(self, width=10)

        descripcion_lbl = tk.Label(self, text='Descripcion')
        descripcion_txt = tk.Text(self, width=25, height=6)

        costo_lbl = tk.Label(self, text='Costo')
        costo_entry = tk.Entry(self, width=8)

        mantenimiento_tree = ttk.Treeview(self, columns=('0', '1', '2', '3', '4', '5', '6'))
        mantenimiento_tree.heading('0', text='ID')
        mantenimiento_tree.heading('1', text='Unidad')
        mantenimiento_tree.heading('2', text='Ubicacion')
        mantenimiento_tree.heading('3', text='Inicio')
        mantenimiento_tree.heading('4', text='Cierre')
        mantenimiento_tree.heading('5', text='Descripcion')
        mantenimiento_tree.heading('6', text='Costo')
        mantenimiento_tree['show'] = 'headings'

        mantenimiento_tree.column('0', width=20)
        mantenimiento_tree.column('1', width=60)
        mantenimiento_tree.column('2', width=100)
        mantenimiento_tree.column('3', width=75)
        mantenimiento_tree.column('4', width=75)
        mantenimiento_tree.column('6', width=100)

        titulo.place(relx=1 / 2, rely=1 / 11, anchor='center')

        id_lbl.place(relx=3/24, rely=2/11)
        id_entry.place(relx=5/24, rely=2/11)
        seleccionar_btn.place(relx=6/24, rely=2/11)

        unidad_lbl.place(relx=8 / 24, rely=2 / 11)
        unidad_entry.place(relx=9 / 24, rely=2 / 11)

        ubicacion_lbl.place(relx=3 / 24, rely=3 / 11)
        ubicacion_entry.place(relx=5 / 24, rely=3 / 11)

        fecha_inicio_lbl.place(relx=3 / 24, rely=4 / 11)
        fecha_inicio_entry.place(relx=5 / 24, rely=4 / 11)
        fecha_cierre_lbl.place(relx=7 / 24, rely=4 / 11)
        fecha_cierre_entry.place(relx=9 / 24, rely=4 / 11)

        fecha_inicio_entry.insert(0, date.today())
        fecha_cierre_entry.insert(0, '0000-00-00')

        descripcion_lbl.place(relx=3 / 24, rely=5 / 11)
        descripcion_txt.place(relx=5 / 24, rely=5 / 11)

        costo_lbl.place(relx=3 / 24, rely=8 / 11)
        costo_entry.place(relx=5 / 24, rely=8 / 11)

        mantenimiento_tree.place(relx=11/24, rely=3/11)

        # FUNCIONES SELECCIONAR GUARDAR Y CANCELAR

        def poblar_mantenimientotree():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                c.execute("""SELECT *
                            FROM Mantenimiento
                            ORDER BY fecha_inicio DESC""")

                query = c.fetchall()

                for orden in query:
                    mantenimiento_tree.insert("", 'end', values=(orden[0], orden[1], orden[2], orden[3], orden[4],
                                                                 orden[5], orden[6]))

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def insertar_siguiente():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()
                c.execute("""SELECT id
                        FROM Mantenimiento
                        ORDER BY id DESC
                        LIMIT 1""")

                id_entry.delete(0, tk.END)
                id_entry.insert(0, c.fetchone()[0]+1)

                c.close()

            except pymysql.err.ProgrammingError:
                pass

            except TypeError:
                pass

            finally:
                c.close()

        def seleccionar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT *
                        FROM Mantenimiento
                        WHERE id = %s"""

                c.execute(stmt, id_entry.get())

                query = c.fetchone()

                datos = []
                for dato in query:
                    if dato is None:
                        dato = ''
                    datos.append(dato)

                unidad_entry.delete(0, tk.END)
                ubicacion_entry.delete(0, tk.END)
                fecha_inicio_entry.delete(0, tk.END)
                fecha_cierre_entry.delete(0, tk.END)
                descripcion_txt.delete(1.0, tk.END)
                costo_entry.delete(0, tk.END)

                unidad_entry.insert(0, datos[1])
                ubicacion_entry.insert(0, datos[2])
                fecha_inicio_entry.insert(0, datos[3])
                fecha_cierre_entry.insert(0, datos[4])
                descripcion_txt.insert(1.0, datos[5])
                costo_entry.insert(0, datos[6])

            finally:
                c.close()

        def guardar():
            try:
                db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                c = db.cursor()

                stmt = """SELECT id
                        FROM Mantenimiento
                        WHERE id = %s"""
                c.execute(stmt, id_entry.get())

                query = c.fetchone()

                if query is not None:
                    query = query[0]

                c.close()

                if query == int(id_entry.get()):

                    mensaje = messagebox.askyesno('Orden Existente', 'La orden de mantenimiento %s ya existe. '
                                                                    '¿Desea guardar los cambios?' % id_entry.get())

                    if mensaje is True:
                        try:
                            db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                            c = db.cursor()

                            stmt = """UPDATE Mantenimiento
                                    SET n_economico = %s,
                                        ubicacion = %s,
                                        fecha_inicio = %s,
                                        fecha_cierre = %s,
                                        descripcion = %s,
                                        costo = %s
                                    WHERE id = %s"""

                            c.execute(stmt, (unidad_entry.get(), ubicacion_entry.get(), fecha_inicio_entry.get(),
                                             fecha_cierre_entry.get(), descripcion_txt.get(1.0, tk.END),
                                             costo_entry.get(), id_entry.get()))
                            db.commit()

                            unidad_entry.delete(0, tk.END)
                            ubicacion_entry.delete(0, tk.END)
                            fecha_inicio_entry.delete(0, tk.END)
                            fecha_cierre_entry.delete(0, tk.END)
                            descripcion_txt.delete(1.0, tk.END)
                            costo_entry.delete(0, tk.END)
                            mantenimiento_tree.delete(*mantenimiento_tree.get_children())

                            insertar_siguiente()
                            fecha_inicio_entry.insert(0, date.today())
                            fecha_cierre_entry.insert(0, '0000-00-00')
                            poblar_mantenimientotree()

                        finally:
                            c.close()

                else:
                    mensaje = messagebox.askyesno('Orden Inexistente', 'La orden de mantenimiento %s no existe. '
                                                                       '¿Desea darla de alta?' % id_entry.get())
                    if mensaje is True:
                        try:
                            db = pymysql.connect(host=host, user=user, passwd=passw, database=database)
                            c = db.cursor()

                            stmt = """INSERT INTO Mantenimiento (id, n_economico, ubicacion, fecha_inicio, fecha_cierre,
                                                                descripcion, costo)
                                        VALUES (%s,%s,%s,%s,%s,%s,%s)"""

                            c.execute(stmt, (id_entry.get(), unidad_entry.get(), ubicacion_entry.get(),
                                             fecha_inicio_entry.get(), fecha_cierre_entry.get(),
                                             descripcion_txt.get(1.0, tk.END), costo_entry.get()))

                            db.commit()

                            unidad_entry.delete(0, tk.END)
                            ubicacion_entry.delete(0, tk.END)
                            fecha_inicio_entry.delete(0, tk.END)
                            fecha_cierre_entry.delete(0, tk.END)
                            descripcion_txt.delete(1.0, tk.END)
                            costo_entry.delete(0, tk.END)
                            mantenimiento_tree.delete(*mantenimiento_tree.get_children())

                            insertar_siguiente()
                            fecha_inicio_entry.insert(0, date.today())
                            fecha_cierre_entry.insert(0, '0000-00-00')
                            poblar_mantenimientotree()

                        finally:
                            c.close()

            finally:
                c.close()

        def cancelar():
            unidad_entry.delete(0, tk.END)
            ubicacion_entry.delete(0, tk.END)
            fecha_inicio_entry.delete(0, tk.END)
            fecha_inicio_entry.insert(0, date.today())
            fecha_cierre_entry.delete(0, tk.END)
            fecha_cierre_entry.insert(0, '0000-00-00')
            descripcion_txt.delete(1.0, tk.END)
            costo_entry.delete(0, tk.END)

        guardar_btn = tk.Button(self, text=' Guardar', relief='flat', bg='white', image=guardar_icono, compound='left',
                                command=guardar)
        cancelar_btn = tk.Button(self, text=' Cancelar', relief='flat', bg='white', image=cancelar_icono,
                                 compound='left', command=cancelar)

        insertar_siguiente()
        poblar_mantenimientotree()
        seleccionar_btn.config(command=seleccionar)
        guardar_btn.place(relx=13 / 16, rely=9 / 10)
        cancelar_btn.place(relx=14 / 16, rely=9 / 10)


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        default_font = tk.font.nametofont('TkDefaultFont')
        default_font.configure(family='Segoe')

        # ICONOS PARA LOS BOTONES

        inicio_img = Image.open('inicio.png')
        inicio_icono = self.image0 = ImageTk.PhotoImage(inicio_img)
        ordenes_img = Image.open('ordenes.png')
        ordenes_icono = self.image1 = ImageTk.PhotoImage(ordenes_img)
        navieras_img = Image.open('navieras.png')
        navieras_icono = self.image2 = ImageTk.PhotoImage(navieras_img)
        clientes_img = Image.open('clientes.png')
        clientes_icono = self.image3 = ImageTk.PhotoImage(clientes_img)
        unidades_img = Image.open('unidades.png')
        unidades_icono = self.image4 = ImageTk.PhotoImage(unidades_img)
        personal_img = Image.open('personal.png')
        personal_icono = self.image5 = ImageTk.PhotoImage(personal_img)
        facturas_img = Image.open('facturas.png')
        facturas_icono = self.image6 = ImageTk.PhotoImage(facturas_img)
        liquidaciones_img = Image.open('liquidaciones.png')
        liquidaciones_icono = self.image7 = ImageTk.PhotoImage(liquidaciones_img)
        anticipos_img = Image.open('anticipos.png')
        anticipos_icono = self.image8 = ImageTk.PhotoImage(anticipos_img)
        contenedores_img = Image.open('contenedroes.png')
        contenedores_icono = self.image9 = ImageTk.PhotoImage(contenedores_img)
        ciudades_img = Image.open('ciudades.png')
        ciudades_icono = self.image10 = ImageTk.PhotoImage(ciudades_img)
        mantenimiento_img = Image.open('mantenimiento.png')
        mantenimiento_icono = self.image11 = ImageTk.PhotoImage(mantenimiento_img)
        salir_img = Image.open('salir.png')
        salir_icono = self.image12 = ImageTk.PhotoImage(salir_img)

        ordenesl_img = Image.open('ordenesl.png')
        ordenesl_icono = self.image13 = ImageTk.PhotoImage(ordenesl_img)
        navierasl_img = Image.open('navierasl.png')
        navierasl_icono = self.image14 = ImageTk.PhotoImage(navierasl_img)
        clientesl_img = Image.open('clientesl.png')
        clientesl_icono = self.image15 = ImageTk.PhotoImage(clientesl_img)
        unidadesl_img = Image.open('unidadesl.png')
        unidadesl_icono = self.image16 = ImageTk.PhotoImage(unidadesl_img)
        personall_img = Image.open('personall.png')
        personall_icono = self.image17 = ImageTk.PhotoImage(personall_img)
        facturasl_img = Image.open('facturasl.png')
        facturasl_icono = self.image18 = ImageTk.PhotoImage(facturasl_img)
        liquidacionesl_img = Image.open('liquidacionesl.png')
        liquidacionesl_icono = self.image19 = ImageTk.PhotoImage(liquidacionesl_img)
        anticiposl_img = Image.open('anticiposl.png')
        anticiposl_icono = self.image20 = ImageTk.PhotoImage(anticiposl_img)
        contenedoresl_img = Image.open('contenedroesl.png')
        contenedoresl_icono = self.image21 = ImageTk.PhotoImage(contenedoresl_img)
        ciudadesl_img = Image.open('ciudadesl.png')
        ciudadesl_icono = self.image22 = ImageTk.PhotoImage(ciudadesl_img)
        mantenimientol_img = Image.open('mantenimientol.png')
        mantenimientol_icono = self.image23 = ImageTk.PhotoImage(mantenimientol_img)
        salirl_img = Image.open('salirl.png')
        salirl_icono = self.image24 = ImageTk.PhotoImage(salirl_img)

        ordenes = Ordenes(self)
        navieras = Navieras(self)
        clientes = Clientes(self)
        unidades = Unidades(self)
        personal = Personal(self)
        facturas = Facturas(self)
        liquidaciones = Liquidaciones(self)
        anticipos = Anticipos(self)
        contenedores = Contenedores(self)
        ciudades = Ciudades(self)
        mantenimiento = Manteniemiento(self)

        self.grid_columnconfigure(0, minsize=150, weight=1)
        self.grid_columnconfigure(1, weight=200)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # MARCOS DE INICIO

        inicio_marco = tk.Frame(self)
        inicio_marco.grid(column=1, row=0, rowspan=2, sticky='nsew')

        i = 0
        while i < 4:
            inicio_marco.grid_columnconfigure(i, weight=1)
            i += 1

        i = 0
        n = 10
        while i < 6:
            inicio_marco.grid_rowconfigure(i, weight=n)
            n = n + (pow(-1, i))*(-9)
            i += 1

        # MARCO DE CATALOGOS

        catalogos_marco = tk.Frame(self, bg='white')
        catalogos_marco.grid(column=0, row=0, rowspan=2, sticky='nsew')

        catalogos_marco.grid_columnconfigure(0, weight=1)

        i = 0
        while i < 14:
            catalogos_marco.rowconfigure(i, weight=1)
            i += 1

        # MARCO PRINCIPAL

        principal_marco = tk.Frame(self)
        principal_marco.grid(column=1, row=0, sticky='nsew')

        principal_marco1 = tk.Frame(self)
        principal_marco1.grid(column=1, row=1, sticky='nsew')

        # COLOCAR MARCOS EN EL MARCO PRINCIPAL DE LA VENTANA

        ordenes.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        navieras.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        clientes.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        unidades.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        personal.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        facturas.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        liquidaciones.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        anticipos.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        contenedores.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        ciudades.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
        mantenimiento.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)

        # DEFINIR Y ASIGNAR FUNCIONES A LOS BOTONES

        def mostrar_marco(marco):
            global contador_btn
            if contador_btn % 2 == 0:
                inicio_marco.lower()
                marco.place(in_=principal_marco, x=0, y=0, relwidth=1, relheight=1)
                marco.lift()

            else:
                inicio_marco.lower()
                marco.place(in_=principal_marco1, x=0, y=0, relwidth=1, relheight=1)
                marco.lift()

            contador_btn += 1

        ordenes_mostrar = partial(mostrar_marco, ordenes)
        navieras_mostrar = partial(mostrar_marco, navieras)
        clientes_mostrar = partial(mostrar_marco, clientes)
        unidades_mostrar = partial(mostrar_marco, unidades)
        personal_mostrar = partial(mostrar_marco, personal)
        facturas_mostrar = partial(mostrar_marco, facturas)
        liquidaciones_mostrar = partial(mostrar_marco, liquidaciones)
        anticipos_mostrar = partial(mostrar_marco, anticipos)
        contenedores_mostrar = partial(mostrar_marco, contenedores)
        ciudades_mostrar = partial(mostrar_marco, ciudades)
        mantenimiento_mostrar = partial(mostrar_marco, mantenimiento)

        # DEFINIR Y COLOCAR BOTONES DEL MARCO DE INICIO

        ordenes_btn_inicio = tk.Button(inicio_marco, command=ordenes_mostrar, image=ordenesl_icono)
        ordenes_btn_inicio.grid(column=0, row=0, sticky='nsew')
        ordenes_inicio = tk.Label(inicio_marco, text='Ordenes de Servicio')
        ordenes_inicio.grid(column=0, row=1, sticky='nsew')

        navieras_btn_inicio = tk.Button(inicio_marco, command=navieras_mostrar, image=navierasl_icono)
        navieras_btn_inicio.grid(column=1, row=0, sticky='nsew')
        navieras_inicio = tk.Label(inicio_marco, text='Navieras')
        navieras_inicio.grid(column=1, row=1, sticky='nsew')

        clientes_btn_inicio = tk.Button(inicio_marco, command=clientes_mostrar, image=clientesl_icono)
        clientes_btn_inicio.grid(column=2, row=0, sticky='nsew')
        clientes_inicio = tk.Label(inicio_marco, text='Clientes')
        clientes_inicio.grid(column=2, row=1, sticky='nsew')

        unidades_btn_inicio = tk.Button(inicio_marco, command=unidades_mostrar, image=unidadesl_icono)
        unidades_btn_inicio.grid(column=3, row=0, sticky='nsew')
        unidades_inicio = tk.Label(inicio_marco, text='Unidades')
        unidades_inicio.grid(column=3, row=1, sticky='nsew')

        personal_btn_inicio = tk.Button(inicio_marco, command=personal_mostrar, image=personall_icono)
        personal_btn_inicio.grid(column=0, row=2, sticky='nsew')
        personal_inicio = tk.Label(inicio_marco, text='Personal')
        personal_inicio.grid(column=0, row=3, sticky='nsew')

        facturas_btn_inicio = tk.Button(inicio_marco, command=facturas_mostrar, image=facturasl_icono)
        facturas_btn_inicio.grid(column=1, row=2, sticky='nsew')
        facturas_inicio = tk.Label(inicio_marco, text='Facturas')
        facturas_inicio.grid(column=1, row=3, sticky='nsew')

        liquidaciones_btn_inicio = tk.Button(inicio_marco, command=liquidaciones_mostrar, image=liquidacionesl_icono)
        liquidaciones_btn_inicio.grid(column=2, row=2, sticky='nsew')
        liquidaciones_inicio = tk.Label(inicio_marco, text='Liquidaciones')
        liquidaciones_inicio.grid(column=2, row=3, sticky='nsew')

        anticipos_btn_inicio = tk.Button(inicio_marco, command=anticipos_mostrar, image=anticiposl_icono)
        anticipos_btn_inicio.grid(column=3, row=2, sticky='nsew')
        anticipos_inicio = tk.Label(inicio_marco, text='Anticipos')
        anticipos_inicio.grid(column=3, row=3, sticky='nsew')

        contenedores_btn_inicio = tk.Button(inicio_marco, command=contenedores_mostrar, image=contenedoresl_icono)
        contenedores_btn_inicio.grid(column=0, row=4, sticky='nsew')
        contenedores_inicio = tk.Label(inicio_marco, text='Contenedores')
        contenedores_inicio.grid(column=0, row=5, sticky='nsew')

        ciudades_btn_inicio = tk.Button(inicio_marco, command=ciudades_mostrar, image=ciudadesl_icono)
        ciudades_btn_inicio.grid(column=1, row=4, sticky='nsew')
        ciudades_inicio = tk.Label(inicio_marco, text='Ciudades')
        ciudades_inicio.grid(column=1, row=5, sticky='nsew')

        mantenimiento_btn_inicio = tk.Button(inicio_marco, command=mantenimiento_mostrar, image=mantenimientol_icono)
        mantenimiento_btn_inicio.grid(column=2, row=4, sticky='nsew')
        mantenimiento_inicio = tk.Label(inicio_marco, text='Mantenimiento')
        mantenimiento_inicio.grid(column=2, row=5, sticky='nsew')

        salir_btn_inicio = tk.Button(inicio_marco, command=sys.exit, image=salirl_icono)
        salir_btn_inicio.grid(column=3, row=4, sticky='nsew')
        salir_inicio = tk.Label(inicio_marco, text='Salir')
        salir_inicio.grid(column=3, row=5, sticky='nsew')

        # BARRA DE CATALOGOS

        catalogos_lbl = tk.Label(catalogos_marco, text='Catálogos')
        catalogos_lbl.configure(relief='flat', bg='white', bd=0, font='Segoe 12 bold')
        catalogos_lbl.grid(row=0, sticky='nsew')

        inicio_btn = tk.Button(catalogos_marco, text='  Inicio', command=inicio_marco.lift, image=inicio_icono)
        ordenes_btn = tk.Button(catalogos_marco, text='  Ordenes de Servicio', command=ordenes_mostrar,
                                image=ordenes_icono,)
        navieras_btn = tk.Button(catalogos_marco, text='  Navieras', command=navieras_mostrar, image=navieras_icono)
        clientes_btn = tk.Button(catalogos_marco, text='  Clientes', command=clientes_mostrar, image=clientes_icono)
        unidades_btn = tk.Button(catalogos_marco, text='  Unidades', command=unidades_mostrar, image=unidades_icono)
        personal_btn = tk.Button(catalogos_marco, text='  Personal', command=personal_mostrar, image=personal_icono)
        facturas_btn = tk.Button(catalogos_marco, text='  Facturas', command=facturas_mostrar, image=facturas_icono)
        liquidaciones_btn = tk.Button(catalogos_marco, text='  Liquidaciones', command=liquidaciones_mostrar,
                                      image=liquidaciones_icono)
        anticipos_btn = tk.Button(catalogos_marco, text='  Anticipos', command=anticipos_mostrar, image=anticipos_icono)
        contenedores_btn = tk.Button(catalogos_marco, text='  Contenedores', comman=contenedores_mostrar,
                                     image=contenedores_icono)
        ciudades_btn = tk.Button(catalogos_marco, text='  Ciudades', command=ciudades_mostrar,  image=ciudades_icono)
        mantenimiento_btn = tk.Button(catalogos_marco, text='  Mantenimiento', command=mantenimiento_mostrar,
                                      image=mantenimiento_icono)
        salir_btn = tk.Button(catalogos_marco, text='  Salir', command=sys.exit, image=salir_icono)
        lista_botones_catalogos = [inicio_btn, ordenes_btn, navieras_btn, clientes_btn, unidades_btn, personal_btn,
                                   facturas_btn, liquidaciones_btn, anticipos_btn, contenedores_btn, ciudades_btn,
                                   mantenimiento_btn, salir_btn]

        # BINDINGS PARA  BOTONES DE LA BARRA DE CATALOGOS

        def hover_boton(event):
            event.widget.configure(bg='ghostwhite')

        def leave_boton(event):
            event.widget.configure(bg='white')

        # COLOCAR CONFIGURAR Y BIND DE BARRA DE CATALOGOS

        i = 1
        for boton in lista_botones_catalogos:
            boton.configure(relief='flat', bg='white', bd=0, compound='left', anchor='w')
            boton.grid(row=i, sticky='nsew')
            boton.bind('<Enter>', hover_boton)
            boton.bind('<Leave>', leave_boton)
            i += 1

        inicio_marco.lift()


if __name__ == "__main__":

    root = tk.Tk()
    logo_img = Image.open('logo.jpg')
    icono = ImageTk.PhotoImage(logo_img)
    root.minsize(1420, 880)
    root.title('Autotransportes Pantaco, S.A. de C.V.')
    root.iconphoto(True, icono)
    
    ventana_login()

    # crear_tablas()
    # main = MainView(root)
    # main.pack(side="top", fill="both", expand=True)

    root.lift()
    root.mainloop()
