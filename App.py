# --Libraries--
import customtkinter
import customtkinter as ctk
import tkinter as tk
import mysql.connector 
from tkinter import IntVar
from PIL import Image, ImageTk
from utils import *
from tkinter import messagebox
from customtkinter import CTkCheckBox
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from fpdf import FPDF
import uuid


class RootFrame(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana de la app
        self.title('Sistema de Ventas')
        self.geometry('645x600')
        self.resizable(False, False)

        # Configuración del frame principal dentro del root 'lienzo'
        self.login_frame = customtkinter.CTkFrame(self, border_color='#2c2d2e', border_width=5)
        self.login_frame.pack(pady=20, padx=20, fill='both', expand=True)

        # Frame sellsystem
        self.sellsystem_frame = SellSystemFrame(self, self.login_frame, border_color='#2c2d2e', border_width=5)

        # Frame inventorysystem
        self.inventorysystem_frame = InventorySystemFrame(self, self.login_frame, self.sellsystem_frame, border_color='#2c2d2e', border_width=5)

        # Cargar y mostrar la imagen corporativa
        image_path = 'src/img/logo.png'
        image = Image.open(image_path)
        ctk_image = customtkinter.CTkImage(image, size=(200, 200))
        self.image_label = customtkinter.CTkLabel(self.login_frame, image=ctk_image, text='')
        self.image_label.pack(pady=10)

        # Título 'Iniciar Sesión', encima de los entry's
        self.login_label = customtkinter.CTkLabel(self.login_frame, text='¡Bienvenido de vuelta!', text_color='#f5f9fa', font=("Roboto", 25, 'bold', 'underline'))
        self.login_label.place(x=166, y=18)

        # Título 'Email', por encima del entry para ingresar email, usando el metodo .place para moverlo de lugar
        self.email_label = customtkinter.CTkLabel(self.login_frame, text='Email', text_color='#f5f9fa', font=("Roboto", 16))
        self.email_label.place(x=110, y=160)

        # Entry para ingresar el email, el cual ya tiene que estar registrado en el sistema, y tiene que encajar con el que se ingrese aquí
        self.loginemail_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text='Ingrese su email', width=350)
        self.loginemail_entry.place(x=110, y=200)

        # Bloque de código que hace exactamente lo mismo de arriba, solo que esta vez ingresando la contraseña
        self.password_label = customtkinter.CTkLabel(self.login_frame, text='Contraseña', text_color='#f5f9fa', font=("Roboto", 16))
        self.password_label.place(x=110, y=280)

        self.loginpass_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text='Ingrese su contraseña', width=350, show='*')
        self.loginpass_entry.place(x=110, y=320)

        self.loginerror_label = customtkinter.CTkLabel(self.login_frame, text='La cuenta que ingreso no existe. Ingrese de nuevo por favor', text_color='#f0291a', font=("Roboto", 16))

        # Button para enviar los datos puestos en los anteriores entry's, para despues con un command realizar toma de decisiones sobre si se ingresa o no al sistema con los datos puestos
        self.loginsys_button = customtkinter.CTkButton(self.login_frame, command=lambda: login_check(self, self.loginemail_entry.get(), self.loginpass_entry.get(), ), width=100, height=30, text='Iniciar Sesión', fg_color='#000000')
        self.loginsys_button.pack(side='bottom', pady=50)

class SellSystemFrame(customtkinter.CTkFrame):
    def __init__(self, root, login_frame, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.login_frame = login_frame

        self.selected_items = []  
        self.quantity_entries = [] 
        self.selected_item_vars = []  

        self.content_frame = customtkinter.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True)

        self.sidebar_frame = customtkinter.CTkFrame(self.content_frame, bg_color="#2c2d2e", width=150)
        self.sidebar_frame.pack(side="left", fill="y")

        self.sidebar_buttons = []
        self.sidebar_buttons.append(customtkinter.CTkButton(self.sidebar_frame, text="Cerrar Sesión", width=15,
                                                             command=self.logout))

        for button in self.sidebar_buttons:
            button.pack(pady=10)

        self.blank_frame = customtkinter.CTkFrame(self.content_frame)
        self.blank_frame.pack(side="left", fill="both", expand=True)

        self.inventory_frame = customtkinter.CTkFrame(self.blank_frame)
        self.inventory_frame.pack(side="left", fill="both", expand=True)

        self.show_inventory_table()

        self.bottom_bar_frame = customtkinter.CTkFrame(self)
        self.bottom_bar_frame.pack(side="bottom", fill="x")

        self.add_to_cart_button = customtkinter.CTkButton(self.bottom_bar_frame, text="Añadir Productos al Carrito",
                                                          width=25, command=self.show_purchase_interface)
        self.add_to_cart_button.pack(pady=10)

        self.selected_items_window = None  
        self.selected_items_frame = None  

        self.disable_interface()

    def disable_interface(self):
        for widget in self.inventory_frame.winfo_children():
            widget.configure(state="disabled")

        self.add_to_cart_button.configure(state="disabled")

    def enable_interface(self):
        for widget in self.inventory_frame.winfo_children():
            widget.configure(state="normal")

        self.add_to_cart_button.configure(state="normal")

    def show(self):
        self.pack(side="left", fill="both", expand=True)

    def hide(self):
        self.pack_forget()

    def logout(self):
        self.pack_forget()
        self.login_frame.pack(pady=20, padx=20, fill='both', expand=True)
        self.root.resizable(False, False)
        self.root.loginemail_entry.delete(0, 'end')
        self.root.loginpass_entry.delete(0, 'end')

    def show_inventory_table(self):
        for child in self.inventory_frame.winfo_children():
            child.destroy()

        try:
            cnx = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="bdbazar"
            )

            cursor = cnx.cursor()

            query = "SELECT idProducto, nombreProducto, cantidadProducto, valorUnitario FROM producto"
            cursor.execute(query)
            items = cursor.fetchall()

            column_names = ['ID', 'Nombre', 'Cantidad', 'Valor Unitario', 'Seleccionar']
            for col_index, column_name in enumerate(column_names):
                header_label = customtkinter.CTkLabel(self.inventory_frame, text=column_name,
                                                    font=("Arial", 18, "bold"), width=90)
                header_label.grid(row=0, column=col_index, sticky="nsew")

            for row_index, item in enumerate(items):
                for col_index, value in enumerate(item):
                    if col_index == 3: 
                        value = f"${value}"
                    value_label = customtkinter.CTkLabel(self.inventory_frame, text=value,
                                                        font=("Arial", 14), width=90)
                    value_label.grid(row=row_index + 1, column=col_index, sticky="nsew")
                select_var = tk.IntVar()
                select_checkbox = customtkinter.CTkCheckBox(self.inventory_frame, variable=select_var, width=90, text='')
                select_checkbox.grid(row=row_index + 1, column=len(item), sticky="nsew")
                select_var.set(0)

                select_var.trace_add('write', lambda *args, var=select_var, item=item: self.update_selected_items(var, item))

            cursor.close()
            cnx.close()

        except mysql.connector.Error as e:
            messagebox.showerror("Error", str(e))

    def update_selected_items(self, var, item):
        if var.get() == 1: 
            self.selected_items.append(item)
        else:
            self.selected_items.remove(item)

    def show_purchase_interface(self):
        if not self.selected_items:
            messagebox.showinfo("No hay items seleccionados")
            return

    def show_purchase_interface(self):
        if not self.selected_items:
            messagebox.showinfo("No hay items seleccionados")
            return

        self.selected_items_window = customtkinter.CTkToplevel(self.root)
        self.selected_items_window.title("Interfaz de Venta")
        self.selected_items_window.geometry("700x700")

        self.selected_items_frame = customtkinter.CTkFrame(self.selected_items_window)
        self.selected_items_frame.pack(pady=20)

        product_label = customtkinter.CTkLabel(self.selected_items_frame, text="Producto")
        product_label.grid(row=0, column=0, padx=10)

        quantity_label = customtkinter.CTkLabel(self.selected_items_frame, text="Cantidad")
        quantity_label.grid(row=0, column=1, padx=10)

        self.quantity_entries = [] 

        for i, item in enumerate(self.selected_items):
            product_name_label = customtkinter.CTkLabel(self.selected_items_frame, text=item[1])
            product_name_label.grid(row=i + 1, column=0, padx=10)

            quantity_entry = customtkinter.CTkEntry(self.selected_items_frame)
            quantity_entry.grid(row=i + 1, column=1, padx=10)

            self.quantity_entries.append(quantity_entry)  

        row_offset = len(self.selected_items) + 2

        customer_name_label = customtkinter.CTkLabel(self.selected_items_frame, text="Nombre del Cliente:")
        customer_name_label.grid(row=row_offset, column=0, pady=10)

        self.customer_name_entry = customtkinter.CTkEntry(self.selected_items_frame)
        self.customer_name_entry.grid(row=row_offset, column=1, pady=5)

        company_name_label = customtkinter.CTkLabel(self.selected_items_frame, text="Razón Social:")
        company_name_label.grid(row=row_offset + 1, column=0, pady=10)

        self.company_name_entry = customtkinter.CTkEntry(self.selected_items_frame)
        self.company_name_entry.grid(row=row_offset + 1, column=1, pady=5)

        line_of_business_label = customtkinter.CTkLabel(self.selected_items_frame, text="Giro Cliente:")
        line_of_business_label.grid(row=row_offset + 2, column=0, pady=10)

        self.line_of_business_entry = customtkinter.CTkEntry(self.selected_items_frame)
        self.line_of_business_entry.grid(row=row_offset + 2, column=1, pady=5)

        rut_label = customtkinter.CTkLabel(self.selected_items_frame, text="RUT:")
        rut_label.grid(row=row_offset + 3, column=0, pady=10)

        self.rut_entry = customtkinter.CTkEntry(self.selected_items_frame)
        self.rut_entry.grid(row=row_offset + 3, column=1, pady=5)

        address_label = customtkinter.CTkLabel(self.selected_items_frame, text="Dirección:")
        address_label.grid(row=row_offset + 4, column=0, pady=10)

        self.address_entry = customtkinter.CTkEntry(self.selected_items_frame)
        self.address_entry.grid(row=row_offset + 4, column=1, pady=5)

        self.ticket_checkbox_var = tk.IntVar()
        ticket_checkbox = customtkinter.CTkCheckBox(self.selected_items_frame, text="¿Desea generar boleta?",
                                                    variable=self.ticket_checkbox_var)
        ticket_checkbox.grid(row=row_offset + 5, columnspan=2, pady=10)

        confirm_button = customtkinter.CTkButton(self.selected_items_frame, text="Confirmar", width=10,
                                            command=lambda: self.confirm_purchase(self.rut_entry.get(),
                                                                                    self.company_name_entry.get(),
                                                                                    self.address_entry.get(),
                                                                                    self.line_of_business_entry.get()))
        confirm_button.grid(row=row_offset + 6, column=0, padx=5, pady=10)

        cancel_button = customtkinter.CTkButton(self.selected_items_frame, text="Cancelar", width=10,
                                                command=self.cancel_purchase)
        cancel_button.grid(row=row_offset + 6, column=1, padx=5, pady=10)
    
    def confirm_purchase(self, rut, company_name, address, line_of_business):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="bdbazar"
            )
            cursor = connection.cursor()

            insert_query = "INSERT INTO cliente (rut, razonSocialCliente, direccionCliente, giroCliente) " \
                        "VALUES (%s, %s, %s, %s)"
            values = (rut, company_name, address, line_of_business)

            cursor.execute(insert_query, values)

            connection.commit()

            cursor.close()
            connection.close()

            messagebox.showinfo("Proceso Completado!")

            customer_name = self.customer_name_entry.get()
            products = [item[1] for item in self.selected_items]
            quantities = [entry.get() for entry in self.quantity_entries]

            for idx, var in enumerate(self.selected_item_vars):
                if var.get() == 1:
                    products.append(self.inventory_items[idx])
                    quantities.append(self.quantity_entries[idx].get())

            if not products:
                messagebox.showinfo("No Products Selected", "Please select at least one product.")
                return
            
            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", "B", 16)

            pdf.image("src/img/Icono Temporal.png", x=170, y=10, w=30)

            pdf.set_xy(10, 50)

            pdf.cell(0, 10, f"Customer Name: {customer_name}", ln=True)
            pdf.cell(0, 10, f"RUT: {rut}", ln=True)
            pdf.cell(0, 10, f"Company Name: {company_name}", ln=True)
            pdf.cell(0, 10, f"Address: {address}", ln=True)
            pdf.cell(0, 10, f"Line of Business: {line_of_business}", ln=True)

            pdf.set_xy(10, 100)

            pdf.cell(0, 10, "Product Details:", ln=True)

            net_value = 0.0
            vat = 0.0

            for product, quantity in zip(products, quantities):
                pdf.cell(0, 10, f"Product: {product}", ln=True)
                pdf.cell(0, 10, f"Quantity: {quantity}", ln=True)

                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="bdbazar"
                )
                cursor = connection.cursor()
                cursor.execute("SELECT valorUnitario FROM producto WHERE nombreProducto = %s", (product,))
                result = cursor.fetchone()
                if result is not None:
                    price = result[0]
                else:
                    price = 0

                total_price = price * int(quantity)

                net_value += total_price

                product_vat = total_price * 0.19

                vat += product_vat

                cursor.close()
                connection.close()

            total = net_value + vat

            pdf.cell(0, 10, f"Net Value: {net_value}", ln=True)
            pdf.cell(0, 10, f"VAT: {vat}", ln=True)
            pdf.cell(0, 10, f"Total: {total}", ln=True)

            ticket_id = str(uuid.uuid4())

            ticket_name = f"ticket_{ticket_id}.pdf"

            pdf_path = os.path.join("src", "img", "boletas", ticket_name)
            pdf.output(pdf_path)

            os.startfile(pdf_path)

            self.rut_entry.delete(0, "end")
            self.company_name_entry.delete(0, "end")
            self.address_entry.delete(0, "end")
            self.line_of_business_entry.delete(0, "end")
            self.selected_items = []
            self.selected_items_window.destroy()

        except mysql.connector.Error as error:
            messagebox.showerror("Database Error", str(error))

    def cancel_purchase(self):
        self.selected_items.clear()
        self.selected_items_window.destroy()

    
class ConfirmationDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, confirm_callback):
        super().__init__(parent)
        self.title(title)

        message_label = ctk.CTkLabel(self, text=message)
        message_label.pack(padx=10, pady=10)

        confirm_button = ctk.CTkButton(self, text="Confirmar", command=confirm_callback)
        confirm_button.pack(side="left", padx=10, pady=10)

        cancel_button = ctk.CTkButton(self, text="Cancelar", command=self.destroy)
        cancel_button.pack(side="left", padx=10, pady=10)

class InventorySystemFrame(customtkinter.CTkFrame):
    def __init__(self, root, login_frame, sellsystem_frame, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.root = root
        self.login_frame = login_frame
        self.sellsystem_frame = sellsystem_frame  

        self.content_frame = customtkinter.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True)

        self.sidebar_frame = customtkinter.CTkFrame(self.content_frame, bg_color="#2c2d2e", width=150)
        self.sidebar_frame.pack(side="left", fill="y")

        self.sidebar_buttons = []
        self.sidebar_buttons.append(customtkinter.CTkButton(self.sidebar_frame, text="Informe de Ventas", width=15))
        self.sidebar_buttons.append(customtkinter.CTkButton(self.sidebar_frame, text="Apertura de Día", width=15, command=self.opening_day))
        self.sidebar_buttons.append(customtkinter.CTkButton(self.sidebar_frame, text="Cierre de Día", width=15, command=self.closing_day))
        self.sidebar_buttons.append(customtkinter.CTkButton(self.sidebar_frame, text="Cerrar Sesión", width=15, command=self.logout))

        for button in self.sidebar_buttons:
            button.pack(pady=10)

        self.blank_frame = customtkinter.CTkFrame(self.content_frame)
        self.blank_frame.pack(side="left", fill="both", expand=True)

        self.inventory_frame = customtkinter.CTkFrame(self.blank_frame)
        self.inventory_frame.pack(side="left", fill="both", expand=True)

        self.bottom_bar_frame = customtkinter.CTkFrame(self)
        self.bottom_bar_frame.pack(side="bottom", fill="x")

        self.add_to_cart_button = customtkinter.CTkButton(self.bottom_bar_frame, text="Añadir Productos", width=15, command=self.open_add_product)
        self.add_to_cart_button.pack(pady=10)

        # Create the table frame
        self.table_frame = customtkinter.CTkFrame(self.inventory_frame)
        self.table_frame.pack(fill='both', expand=True)
        self.show_inventory_table()

        self.hide()

    def show_inventory_table(self):
        for child in self.table_frame.winfo_children():
            if isinstance(child, (customtkinter.CTkLabel, customtkinter.CTkButton)) and child.grid_info()["row"] > 0:
                child.destroy()

        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bdbazar"
        )
        cursor = cnx.cursor()
        query = "SELECT * FROM producto"
        cursor.execute(query)
        items = cursor.fetchall()

        column_names = ['ID', 'Nombre', 'Cantidad', 'Valor Unitario', 'Acciones']
        for col_index, column_name in enumerate(column_names):
            header_label = customtkinter.CTkLabel(self.table_frame, text=column_name, font=("Arial", 18, "bold"), width=90)
            header_label.grid(row=0, column=col_index, sticky="nsew")

        for row_index, item in enumerate(items):
            item_id = item[0]
            item_name = item[1]
            item_quantity = item[2]
            item_unit_value = item[3]

            item_id_label = customtkinter.CTkLabel(self.table_frame, text=item_id, font=("Arial", 12), width=80)
            item_id_label.grid(row=row_index + 1, column=0, sticky="nsew")

            item_name_label = customtkinter.CTkLabel(self.table_frame, text=item_name, font=("Arial", 12), width=80)
            item_name_label.grid(row=row_index + 1, column=1, sticky="nsew")

            item_quantity_label = customtkinter.CTkLabel(self.table_frame, text=item_quantity, font=("Arial", 12), width=80)
            item_quantity_label.grid(row=row_index + 1, column=2, sticky="nsew")

            item_unit_value_label = customtkinter.CTkLabel(self.table_frame, text=item_unit_value, font=("Arial", 12), width=80)
            item_unit_value_label.grid(row=row_index + 1, column=3, sticky="nsew")

            edit_button = customtkinter.CTkButton(self.table_frame, text="Editar", font=("Arial", 10), width=10,
                                                  command=lambda prod=item: self.open_edit_product(prod))
            edit_button.grid(row=row_index + 1, column=4, sticky="nsew")

            delete_button = customtkinter.CTkButton(self.table_frame, text="Eliminar", font=("Arial", 10), width=10, command=lambda prod=item: self.confirm_delete_product(prod))
            delete_button.grid(row=row_index + 1, column=5, sticky="nsew")

        for i in range(self.table_frame.grid_size()[1]):
            self.table_frame.columnconfigure(i, weight=1)

    def opening_day(self):
        messagebox.showinfo("Apertura de Día", "El sistema de ventas ha sido habilitado.")
        self.sellsystem_frame.enable_interface()

    def closing_day(self):
        messagebox.showinfo("Cierre de Día", "El sistema de ventas ha sido deshabilitado.")
        self.sellsystem_frame.disable_interface()

    def open_edit_product(self, product):

        edit_window = customtkinter.CTkToplevel(self.root)
        edit_window.title("Editar Producto")
        edit_window.geometry("300x200")


        name_label = customtkinter.CTkLabel(edit_window, text="Nombre:")
        name_label.pack()
        name_entry = customtkinter.CTkEntry(edit_window)
        name_entry.pack()

        quantity_label = customtkinter.CTkLabel(edit_window, text="Cantidad:")
        quantity_label.pack()
        quantity_entry = customtkinter.CTkEntry(edit_window)
        quantity_entry.pack()

        value_label = customtkinter.CTkLabel(edit_window, text="Valor Unitario:")
        value_label.pack()
        value_entry = customtkinter.CTkEntry(edit_window)
        value_entry.pack()


        name_entry.insert(0, product[1])
        quantity_entry.insert(0, product[2])
        value_entry.insert(0, product[3])


        update_button = customtkinter.CTkButton(edit_window, text="Update",
                                                command=lambda: self.update_product(product, name_entry.get(), quantity_entry.get(), value_entry.get()))
        update_button.pack()

        edit_window.mainloop()

    def update_product(self, product, name, quantity, value):
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bdbazar"
        )
        cursor = cnx.cursor()
        update_query = "UPDATE producto SET nombreProducto=%s, cantidadProducto=%s, valorUnitario=%s WHERE idProducto=%s"
        data = (name, quantity, value, product[0])
        cursor.execute(update_query, data)
        cnx.commit()

        # Show a success message
        messagebox.showinfo("Producto Actualizado")

        # Refresh the inventory table
        self.show_inventory_table()

    def confirm_delete_product(self, product):
        confirm_dialog = ConfirmationDialog(
            self,
            title="Confirmar Eliminación",
            message="¿Seguro que quieres eliminar este producto?",
            confirm_callback=lambda: self.perform_delete_product(product),
        )
        confirm_dialog.grab_set()

    def perform_delete_product(self, product):
        if isinstance(product, tuple) and len(product) >= 1:
            product_id = product[0]

            try:
                cnx = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="bdbazar"
                )
            except Exception as e:
                messagebox.showerror(f"Error: {e}")
                return

            cursor = cnx.cursor()

            delete_query = "DELETE FROM producto WHERE idProducto = %s"
            data = (product_id,)

            try:
                cursor.execute(delete_query, data)
                cnx.commit()

                messagebox.showinfo("Producto Removido!")

                cursor.close()
                cnx.close()

                self.show_inventory_table()
            except Exception as e:

                messagebox.showerror(f"Error: {e}")


    def open_add_product(self):

        add_window = customtkinter.CTkTopLevel(self)
        add_window.geometry("300x200")

        name_label = customtkinter.CTkLabel(add_window, text="Nombre:")
        name_label.pack()
        name_entry = customtkinter.CTkEntry(add_window)
        name_entry.pack()

        quantity_label = customtkinter.CTkLabel(add_window, text="Cantidad:")
        quantity_label.pack()
        quantity_entry = customtkinter.CTkEntry(add_window)
        quantity_entry.pack()

        value_label = customtkinter.CTkLabel(add_window, text="Valor Unitario:")
        value_label.pack()
        value_entry = customtkinter.CTkEntry(add_window)
        value_entry.pack()

        add_button = customtkinter.CTkButton(add_window, text="Add",
                                             command=lambda: self.add_product(name_entry.get(), quantity_entry.get(), value_entry.get()))
        add_button.pack()

        add_window.mainloop()
    
    def open_add_product(self):
        product_window = customtkinter.CTkToplevel(self.root)
        product_window.title("Add Product")
        product_window.geometry("400x300")

        name_label = customtkinter.CTkLabel(product_window, text="Product Name:")
        name_label.pack()
        name_entry = customtkinter.CTkEntry(product_window)
        name_entry.pack()

        quantity_label = customtkinter.CTkLabel(product_window, text="Quantity:")
        quantity_label.pack()
        quantity_entry = customtkinter.CTkEntry(product_window)
        quantity_entry.pack()

        unit_value_label = customtkinter.CTkLabel(product_window, text="Unit Value:")
        unit_value_label.pack()
        unit_value_entry = customtkinter.CTkEntry(product_window)
        unit_value_entry.pack()

        add_button = customtkinter.CTkButton(product_window, text="Add", width=15,
                                             command=lambda: self.add_product(name_entry.get(),
                                                                              quantity_entry.get(),
                                                                              unit_value_entry.get(),
                                                                              product_window))
        add_button.pack(pady=10)
    
    def add_product(self, name_entry, quantity, unit_value, product_window):
            if not name_entry or not quantity or not unit_value:
                messagebox.showerror("Error")
                return

            try:
                quantity = int(quantity)
                unit_value = float(unit_value)
            except ValueError:
                messagebox.showerror("Error")
                return

            try:
                cnx = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="bdbazar"
                )
            except Exception as e:
                messagebox.showerror(f"Error: {e}")
                return

            cursor = cnx.cursor()

            insert_query = "INSERT INTO producto (nombreProducto, cantidadProducto, valorUnitario) VALUES (%s, %s, %s)"
            product_data = (name_entry, quantity, unit_value)

            try:
                cursor.execute(insert_query, product_data)

                cnx.commit()

                messagebox.showinfo("Producto Añadido.")

                product_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Fallo: {e}")

            cursor.close()
            cnx.close()

    def show(self):
        self.pack(side="left", fill="both", expand=True)
        self.show_inventory_table()  

    def hide(self):
        self.pack_forget()

    def logout(self):
        self.pack_forget()
        self.login_frame.pack(pady=20, padx=20, fill='both', expand=True)
        self.root.resizable(False, False)
        self.root.loginemail_entry.delete(0, 'end')
        self.root.loginpass_entry.delete(0, 'end')


        
# Código mantenedor de la app
if __name__ == "__main__":
    root = RootFrame()
    root.mainloop()