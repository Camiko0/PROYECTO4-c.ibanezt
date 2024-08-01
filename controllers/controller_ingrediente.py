from flask import  render_template, request
from models.models_bd import Ingrediente
import utils.formatearHtml
import utils.variables_generales
from db import db
from models.enum_roles import Roles_Enum
from flask_login import login_required

#Obtener todos los ingredientes
@utils.validar_login.validar_rol(Roles_Enum.EMPLEADO)
@login_required
def get_ingrediente_all():
    ingredientes = Ingrediente.query.all()
    return render_template('ingredientes.html', ingredientes=ingredientes, ventas=utils.variables_generales.get_variable_ventas_del_dia())

#Obtener un ingrediente por id
@utils.validar_login.validar_rol(Roles_Enum.EMPLEADO)
@login_required
def get_ingrediente_by_id(id_ingrediente) -> str:
    ingredientes = Ingrediente.query.get(id_ingrediente)
    #Validar la consulta realizada
    if ingredientes is not None:
        ingrediente_list = [ingredientes]
    else:
        ingrediente_list = []
    return render_template('ingredientes.html', ingredientes=ingrediente_list, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           id_ingrediente=id_ingrediente)

#Obtener un ingrediente por nombre
@utils.validar_login.validar_rol(Roles_Enum.EMPLEADO)
@login_required
def get_ingrediente_by_name(nombre_ingrediente) -> str:
    ingredientes = Ingrediente.query.filter_by(nombre=nombre_ingrediente)
    #Validar la consulta realizada
    if ingredientes.count() > 0:
        ingrediente_list = ingredientes.all()
    else:
        ingrediente_list = []
    return render_template('ingredientes.html', ingredientes=ingrediente_list, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           nombre_ingrediente=nombre_ingrediente)

#Abastecer un ingrediente o renovar un ingrediente
@utils.validar_login.validar_rol(Roles_Enum.EMPLEADO)
@login_required
def abastecer_by_id(id_ingrediente):
    session = db.session
    #Buscar ingrediente a modificar inventario
    ingredientes_abastecer = Ingrediente.query.get(id_ingrediente)
    renovar = request.args.get('renovar')
    #Si tiene el parametro renovar (renovar inventario) sino abastecer
    if renovar:
        ingredientes_abastecer.renovar_inventario()
    else:
        ingredientes_abastecer.abastecer()
    #Hacer commit
    session.commit()
    ingredientes = Ingrediente.query.all()
    #Enviar a pantalla de ingredientes
    return render_template('ingredientes.html', ingredientes=ingredientes, ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                           renovar=True, ingrediente_abastecer=ingredientes_abastecer.nombre)