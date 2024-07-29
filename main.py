import tkinter as tk
from tkinter import messagebox, Listbox, Scrollbar, END
import mysql.connector as db
from mysql.connector import Error

class ClienteFormulario:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.frame.config(bd=2, relief="sunken")

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

        self.agregar_telefono_button = tk.Button(self.frame, text="Agregar Teléfono", command=self.add_telefono_entry)
        self.agregar_telefono_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.submit_button = tk.Button(self.frame, text="Guardar cliente a la lista", command=self.guardar_cliente)
        self.submit_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.transaccion = tk.Button(self.frame, text="Confirmar transacción", command=self.confirmar_transaccion)
        self.transaccion.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        self.rollback = tk.Button(self.frame, text="Rollback", command=self.rollback_transaccion)
        self.rollback.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        self.lista_db = Listbox(parent, width=50)
        self.lista_db.pack(side=tk.RIGHT, padx=10, pady=10)

        self.scrollbar_db = Scrollbar(parent)
        self.scrollbar_db.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_db.config(yscrollcommand=self.scrollbar_db.set)
        self.scrollbar_db.config(command=self.lista_db.yview)

        self.lista_temp = Listbox(parent, width=50)
        self.lista_temp.pack(side=tk.RIGHT, padx=10, pady=10)

        self.scrollbar_temp = Scrollbar(parent)
        self.scrollbar_temp.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_temp.config(yscrollcommand=self.scrollbar_temp.set)
        self.scrollbar_temp.config(command=self.lista_temp.yview)

        self.clientes_temp = []  # Lista temporal para almacenar los clientes
        self.connection = None  # Conexión a la base de datos
        self.conectar_base_datos()
        self.cargar_clientes()  # Cargar clientes desde la base de datos al iniciar

    def conectar_base_datos(self):
        try:
            # Conexión a la base de datos
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
                self.connection.autocommit = False  # Desactivar autocommit para manejar transacciones
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

            # Limpiar la lista antes de cargar nuevos datos
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

    def guardar_cliente(self):
        nombre = self.nombre_entry.get()
        apellido = self.apellido_entry.get()
        direccion = self.direccion_entry.get()
        telefonos = [entry.get() for entry in self.telefono_entries if entry.get()]

        if not nombre or not apellido or not direccion or not telefonos:
            messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.")
            return

        # Agregar el cliente a la lista temporal
        cliente_datos = {
            'nombre': nombre,
            'apellido': apellido,
            'direccion': direccion,
            'telefonos': telefonos
        }
        self.clientes_temp.append(cliente_datos)

        # Agregar el cliente a la lista temporal de la interfaz para mostrar
        cliente_display = f"Nombre: {nombre}, Apellido: {apellido}, Dirección: {direccion}, Teléfonos: {', '.join(telefonos)}"
        self.lista_temp.insert(END, cliente_display)

        # Limpiar los campos
        self.limpiar_campos()

    def limpiar_campos(self):
        self.nombre_entry.delete(0, END)
        self.apellido_entry.delete(0, END)
        self.direccion_entry.delete(0, END)
        for entry in self.telefono_entries:
            entry.delete(0, END)

    def confirmar_transaccion(self):
        if not self.clientes_temp:
            messagebox.showwarning("Advertencia", "No hay clientes para guardar.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")  # Establecer nivel de aislamiento

            cursor.execute("START TRANSACTION")

            for cliente in self.clientes_temp:
                nombre = cliente['nombre']
                apellido = cliente['apellido']
                direccion = cliente['direccion']
                telefonos = cliente['telefonos']

                # Guardar el cliente en la base de datos
                query_cliente = "INSERT INTO clientes (Nombre, Apellido, Direccion) VALUES (%s, %s, %s)"
                cursor.execute(query_cliente, (nombre, apellido, direccion))
                cliente_id = cursor.lastrowid  # Obtener el ID del cliente insertado

                # Guardar los teléfonos en la base de datos
                for telefono in telefonos:
                    query_telefono = "INSERT INTO telefonos (Numero, clientes_idCliente) VALUES (%s, %s)"
                    cursor.execute(query_telefono, (telefono, cliente_id))

            cursor.execute("COMMIT")
            messagebox.showinfo("Éxito", "Clientes y teléfonos guardados en la base de datos.")
            self.cargar_clientes()  # Recargar la lista de clientes desde la base de datos
            self.lista_temp.delete(0, END)  # Limpiar la lista temporal de clientes
            self.clientes_temp = []  # Limpiar la lista temporal
        except db.IntegrityError as e:
            messagebox.showerror("Error de Integridad", f"Error al guardar los clientes: {e}. Posiblemente un número de teléfono duplicado.")
            cursor.execute("ROLLBACK")  # Hacer rollback si hay un error
        except Error as e:
            messagebox.showerror("Error", f"Error al guardar los clientes: {e}")
            cursor.execute("ROLLBACK")  # Hacer rollback si hay un error
        finally:
            cursor.close()

    def rollback_transaccion(self):
        # Limpiar la lista temporal y los campos de entrada
        self.lista_temp.delete(0, END)
        self.clientes_temp = []  # Limpiar la lista temporal
        self.limpiar_campos()  # Limpiar los campos de entrada
        messagebox.showinfo("Rollback", "Transacción revertida. Se han limpiado los datos temporalmente.")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gestión de Clientes")
    app = ClienteFormulario(root)
    root.mainloop()