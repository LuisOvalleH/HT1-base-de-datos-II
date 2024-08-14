import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, END
import mysql.connector as db
from mysql.connector import Error

class ClienteFormulario:
    def __init__(self, parent, title):
        self.parent = parent
        self.parent.title(title)
        self.frame = tk.Frame(parent)
        self.frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.frame.config(bd=2, relief="sunken")

        # Campos del formulario
        self.nombre_label = tk.Label(self.frame, text="Nombre")
        self.nombre_label.grid(row=0, column=0, padx=10, pady=10)
        self.nombre_entry = tk.Entry(self.frame)
        self.nombre_entry.grid(row=0, column=1, padx=10, pady=10)

        self.apellido_label = tk.Label(self.frame, text="Apellido")
        self.apellido_label.grid(row=1, column=0, padx=10, pady=10)
        self.apellido_entry = tk.Entry(self.frame)
        self.apellido_entry.grid(row=1, column=1, padx=10, pady=10)

        self.direccion_label = tk.Label(self.frame, text="Dirección")
        self.direccion_label.grid(row=2, column=0, padx=10, pady=10)
        self.direccion_entry = tk.Entry(self.frame)
        self.direccion_entry.grid(row=2, column=1, padx=10, pady=10)

        self.telefono_label = tk.Label(self.frame, text="Teléfono")
        self.telefono_label.grid(row=3, column=0, padx=10, pady=10)
        self.telefono_frame = tk.Frame(self.frame)
        self.telefono_frame.grid(row=3, column=1, padx=10, pady=10)

        self.telefono_entries = []
        self.add_telefono_entry()

        # Botones
        self.agregar_telefono_button = tk.Button(self.frame, text="Agregar Teléfono", command=self.add_telefono_entry)
        self.agregar_telefono_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.iniciar_transaccion = tk.Button(self.frame, text="Iniciar transacción", command=self.iniciar_transaccion)
        self.iniciar_transaccion.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.guardar_button = tk.Button(self.frame, text="Guardar cliente", command=self.guardar_cliente)
        self.guardar_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        self.confirmar_transaccion = tk.Button(self.frame, text="Confirmar transacción", command=self.confirmar_transaccion)
        self.confirmar_transaccion.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        self.rollback_transaccion = tk.Button(self.frame, text="Rollback", command=self.rollback_transaccion)
        self.rollback_transaccion.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        # Niveles de lectura
        self.nivel_lectura = tk.StringVar(value="READ COMMITTED")
        self.lectura_comprometida_button = tk.Button(self.frame, text="Lectura No comprometida", command=lambda: self.set_nivel_lectura("READ UNCOMMITTED"))
        self.lectura_comprometida_button.grid(row=9, column=0, padx=10, pady=10)

        self.lectura_no_comprometida_button = tk.Button(self.frame, text="Lectura Comprometida", command=lambda: self.set_nivel_lectura("READ COMMITTED"))
        self.lectura_no_comprometida_button.grid(row=9, column=1, padx=10, pady=10)

        self.lectura_repetible_button = tk.Button(self.frame, text="Lectura Repetible", command=lambda: self.set_nivel_lectura("REPEATABLE READ"))
        self.lectura_repetible_button.grid(row=9, column=2, padx=10, pady=10)

        self.lectura_no_repetible_button = tk.Button(self.frame, text="Lectura No Repetible", command=lambda: self.set_nivel_lectura("SERIALIZABLE"))
        self.lectura_no_repetible_button.grid(row=9, column=3, padx=10, pady=10)

        # Botón de consulta
        self.consultar_button = tk.Button(self.frame, text="Consultar Datos", command=self.consultar_datos)
        self.consultar_button.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

        # Lista para mostrar datos
        self.lista_db = Listbox(parent, width=50)
        self.lista_db.pack(side=tk.RIGHT, padx=10, pady=10)

        self.scrollbar_db = Scrollbar(parent)
        self.scrollbar_db.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_db.config(yscrollcommand=self.scrollbar_db.set)
        self.scrollbar_db.config(command=self.lista_db.yview)

        # Variables
        self.connection = None
        self.transaccion_iniciada = False
        self.conectar_base_datos()
        self.cargar_clientes()

    def set_nivel_lectura(self, nivel):
        self.nivel_lectura.set(nivel)
        messagebox.showinfo("Nivel de Lectura", f"Nivel de lectura establecido a: {nivel}")

    def conectar_base_datos(self):
        try:
            self.connection = db.connect(
                host='127.0.0.1',
                database='db2',
                user='root',
                password='ovalle82',
                port="3307"
            )
            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print(f"Conectado al servidor MySQL versión {db_Info}")
                self.connection.autocommit = False  # Asegurarse de que el autocommit esté desactivado
        except Error as e:
            print(f"Error al conectarse a MySQL: {e}")
            messagebox.showerror("Error de conexión", "No se pudo conectar a la base de datos.")

    def cargar_clientes(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT c.Nombre, c.Apellido, c.Direccion, GROUP_CONCAT(t.Numero SEPARATOR ', ') AS Telefonos "
                           "FROM clientes c LEFT JOIN telefonos t ON c.idCliente = t.clientes_idCliente "
                           "GROUP BY c.idCliente")
            rows = cursor.fetchall()

            self.lista_db.delete(0, END)

            for row in rows:
                cliente_datos = f"Nombre: {row[0]}, Apellido: {row[1]}, Dirección: {row[2]}, Teléfonos: {row[3]}"
                self.lista_db.insert(END, cliente_datos)
        except Error as e:
            messagebox.showerror("Error", f"Error al cargar los clientes: {e}")
        finally:
            cursor.close()

    def add_telefono_entry(self):
        telefono_entry = tk.Entry(self.telefono_frame)
        telefono_entry.pack(pady=2)
        self.telefono_entries.append(telefono_entry)

    def iniciar_transaccion(self):
        if self.transaccion_iniciada:
            messagebox.showwarning("Advertencia", "Ya hay una transacción en curso.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("START TRANSACTION")
            self.transaccion_iniciada = True
            messagebox.showinfo("Transacción", "Transacción iniciada.")
        except Error as e:
            messagebox.showerror("Error", f"No se pudo iniciar la transacción: {e}")
        finally:
            cursor.close()

    def guardar_cliente(self):
        if not self.transaccion_iniciada:
            messagebox.showwarning("Advertencia", "Debes iniciar una transacción antes de guardar clientes.")
            return

        nombre = self.nombre_entry.get()
        apellido = self.apellido_entry.get()
        direccion = self.direccion_entry.get()
        telefonos = [entry.get() for entry in self.telefono_entries if entry.get()]

        if not nombre or not apellido or not direccion or not telefonos:
            messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.")
            return

        try:
            cursor = self.connection.cursor()
            # Guardar en la base de datos
            query_cliente = "INSERT INTO clientes (Nombre, Apellido, Direccion) VALUES (%s, %s, %s)"
            cursor.execute(query_cliente, (nombre, apellido, direccion))
            cliente_id = cursor.lastrowid  # Obtener el último ID generado

            for telefono in telefonos:
                query_telefono = "INSERT INTO telefonos (Numero, clientes_idCliente) VALUES (%s, %s)"
                cursor.execute(query_telefono, (telefono, cliente_id))

            self.limpiar_campos()
            messagebox.showinfo("Cliente guardado", f"Cliente {nombre} {apellido} guardado temporalmente.")
        except db.IntegrityError as e:
            messagebox.showerror("Error", f"Error al guardar el cliente: {e}")
            self.connection.rollback()  # Hacer rollback en caso de error
        finally:
            cursor.close()

    def confirmar_transaccion(self):
        if not self.transaccion_iniciada:
            messagebox.showwarning("Advertencia", "No hay ninguna transacción iniciada.")
            return

        try:
            self.connection.commit()
            self.transaccion_iniciada = False
            messagebox.showinfo("Transacción", "Transacción confirmada.")
            self.cargar_clientes()  # Recargar la lista de clientes
        except Error as e:
            messagebox.showerror("Error", f"No se pudo confirmar la transacción: {e}")

    def rollback_transaccion(self):
        if not self.transaccion_iniciada:
            messagebox.showwarning("Advertencia", "No hay ninguna transacción iniciada.")
            return

        try:
            self.connection.rollback()
            self.transaccion_iniciada = False
            messagebox.showinfo("Transacción", "Transacción revertida.")
        except Error as e:
            messagebox.showerror("Error", f"No se pudo revertir la transacción: {e}")

    def consultar_datos(self):
        try:
            cursor = self.connection.cursor()

            # Establecer el nivel de lectura antes de la consulta
            cursor.execute(f"SET SESSION TRANSACTION ISOLATION LEVEL {self.nivel_lectura.get()}")

            # Realizar la consulta de clientes
            cursor.execute(
                "SELECT c.Nombre, c.Apellido, c.Direccion, GROUP_CONCAT(t.Numero SEPARATOR ', ') AS Telefonos "
                "FROM clientes c LEFT JOIN telefonos t ON c.idCliente = t.clientes_idCliente "
                "GROUP BY c.idCliente"
            )

            rows = cursor.fetchall()

            # Limpiar la lista anterior
            self.lista_db.delete(0, END)

            # Mostrar los resultados
            for row in rows:
                cliente_datos = f"Nombre: {row[0]}, Apellido: {row[1]}, Dirección: {row[2]}, Teléfonos: {row[3]}"
                self.lista_db.insert(END, cliente_datos)

        except Error as e:
            messagebox.showerror("Error", f"Error al consultar los datos: {e}")
        finally:
            cursor.close()

    def limpiar_campos(self):
        self.nombre_entry.delete(0, END)
        self.apellido_entry.delete(0, END)
        self.direccion_entry.delete(0, END)
        for entry in self.telefono_entries:
            entry.delete(0, END)

# Crear las ventanas principales
root1 = tk.Tk()
app1 = ClienteFormulario(root1, "Gestión de Clientes - Ventana 1")

root2 = tk.Toplevel()
app2 = ClienteFormulario(root2, "Gestión de Clientes - Ventana 2")

root1.mainloop()