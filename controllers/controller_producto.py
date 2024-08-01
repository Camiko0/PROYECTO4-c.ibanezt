from flask import render_template
from models.models_bd import Producto
import utils.funciones
import utils.validar_login
from models.enum_roles import Roles_Enum
from flask_login import login_required
    
#Obtener todos los productos
def get_producto_all() -> str:
    productos = Producto.query.all()
    productos = calcular_calorias(productos)
    return render_template('productos.html', productos=productos, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           mostrar_calorias=utils.validar_login.is_login())

#Obtener un producto por id
@utils.validar_login.validar_rol(Roles_Enum.CLIENTE)
@login_required
def get_producto_by_id(id_producto) -> str:
    productos = Producto.query.get(id_producto)
    #Validar la consulta realizada
    if productos is not None:
        product_list = [productos]
    else:
        product_list = []
    productos = calcular_calorias(product_list)
    return render_template('productos.html', productos=product_list, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           id_producto=id_producto, mostrar_calorias=utils.validar_login.is_login())

#Obtener un producto por id con calorias
@utils.validar_login.validar_rol(Roles_Enum.CLIENTE)
@login_required
def get_producto_by_id_calorias(id_producto) -> str:
    productos = Producto.query.get(id_producto)
    #Validar la consulta realizada
    if productos is not None:
        product_list = [productos]
    else:
        product_list = []
    productos = calcular_calorias(product_list)
    product_list = calcular_calorias(product_list)
    return render_template('productos.html', productos=product_list, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           id_producto=id_producto, mostrar_calorias=True)

#Obtener un producto por nombre
@utils.validar_login.validar_rol(Roles_Enum.EMPLEADO)
@login_required
def get_producto_by_name(nombre_producto) -> str:
    productos = Producto.query.filter_by(nombre=nombre_producto)
    #Validar la consulta realizada
    if productos.count() > 0:
        product_list = productos.all()
    else:
        product_list = []
    product_list = calcular_calorias(product_list)
    return render_template('productos.html', productos=product_list, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           nombre_producto=nombre_producto, mostrar_calorias=utils.validar_login.is_login())

#Obtener la rentabilidad de un producto por id
@utils.validar_login.validar_rol(Roles_Enum.ADMIN)
@login_required
def get_rentabilidad_producto_by_id(id_producto):
    productos = Producto.query.get(id_producto)
    response = calcular_costo_rentabilidad(productos)
    product_list = response[0]
    rentabilidad = response[1]
    return render_template('productos.html', productos=product_list, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           id_producto=id_producto, rentabilidad=rentabilidad, mostrar_calorias=utils.validar_login.is_login())

#Obtener el costo de un producto por id
@utils.validar_login.validar_rol(Roles_Enum.EMPLEADO)
@login_required
def get_costo_producto_by_id(id_producto):
    productos = Producto.query.get(id_producto)
    response = calcular_costo_rentabilidad(productos)
    product_list = response[0]
    costo = response[2]
    return render_template('productos.html', productos=product_list, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           id_producto=id_producto, costo=costo, mostrar_calorias=utils.validar_login.is_login())

def calcular_costo_rentabilidad(productos):
    #Validar la consulta realizada
    if productos is not None:
        product_list = [productos]
        lista_ingredientes = []
        #Calcular la rentabilidad
        for producto in product_list:
            for ingrediente in producto.ingredientes:
                lista_ingredientes.append({"nombre": ingrediente.nombre, "precio": ingrediente.precio})
            # Calcular costo
            costo = utils.funciones.producto_calcular_costo(lista_ingredientes)
            # Calcular rentabilidad
            rentabilidad = utils.funciones.producto_calcular_rentabilidad(producto.precio_publico, lista_ingredientes)
            product_list = calcular_calorias(product_list)
    else:
        product_list = []
        rentabilidad = 0
        costo = 0
    return product_list, rentabilidad, costo

#Obtener las calorias de un listado de productos (Se llama método calcular_calorias() que llama a funciones.producto_contar_calorias)
def calcular_calorias(productos: list) -> list:
    for producto in productos:
        lista_ingredientes_calorias = []
        for ingrediente in producto.ingredientes:
            lista_ingredientes_calorias.append(ingrediente.calorias)
            producto.calorias= producto.calcular_calorias(producto.tipo_producto, lista_ingredientes_calorias)
    return productos