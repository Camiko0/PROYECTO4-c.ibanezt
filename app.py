from flask import Flask, request, render_template
from flask_restful import Api
from flask_login import LoginManager, login_required, login_user, logout_user
from models.usuario import Usuario
from heladeria import Heladeria
import utils.variables_generales
import utils
import os
import utils.validar_login
from models.enum_roles import Roles_Enum
from dotenv import load_dotenv
from db import db
from controllers import controller_ingrediente
from controllers import controller_producto

#Cargar variables de entorno
load_dotenv()

secret_key = os.urandom(24)

#Cargar configuración de la base de datos
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_SCHEMA")}'
app.config["SECRET_KEY"] = secret_key
db.init_app(app)
api = Api(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    user = Usuario.query.get(user_id)
    if user:
        return user
    return None

#Pantalla de inicio con login
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and utils.variables_generales.get_variable_current_user():
        return render_template('main.html', ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                                   username=utils.variables_generales.get_variable_username())
    elif request.method == 'GET':
        logout()
        return render_template("login.html")
    else:
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username, password=password).first()
        if user:
            utils.variables_generales.set_variable_username(username)
            utils.variables_generales.set_variable_current_user(user)
            login_user(user)
            return render_template('main.html', ventas=utils.variables_generales.get_variable_ventas_del_dia(), 
                                   username=utils.variables_generales.get_variable_username())
    logout()
    return render_template("login.html")

#Función para cerrar sesión y borrar variables globales
@app.route("/logout")
def logout():
    utils.variables_generales.set_variable_username("")
    utils.variables_generales.set_variable_current_user(None)
    logout_user()
    return render_template("login.html")

#Reiniciar las ventas de la heladeria
@app.route("/reiniciar-ventas")
@utils.validar_login.validar_rol(Roles_Enum.EMPLEADO)
@login_required
def ventas():
    utils.variables_generales.reset_ventas_del_dia()
    return render_template('main.html', ventas=utils.variables_generales.get_variable_ventas_del_dia(),
                           username=utils.variables_generales.get_variable_username())

#Vender producto
@app.route("/heladeria/vender")
@utils.validar_login.validar_rol(Roles_Enum.CLIENTE)
@login_required
def vender():
    session = db.session
    producto = request.args.get('producto')
    heladeria = Heladeria()
    try:
        vendido=heladeria.vender(producto)
        if vendido: utils.variables_generales.set_variable_ventas_del_dia(1)
        #Hacer commit
        session.commit()
        #Enviar a pantalla de venta
        return render_template('vender.html', ventas=utils.variables_generales.get_variable_ventas_del_dia(), producto=producto, vendido=vendido)
    except ValueError as e:
        return render_template('vender.html', ventas=utils.variables_generales.get_variable_ventas_del_dia(), producto=producto, vendido=False, response=e)

#Calcular el producto más rentable
@app.route("/producto-mas-rentable")
@utils.validar_login.validar_rol(Roles_Enum.ADMIN)
@login_required
def producto_mas_rentable():
    heladeria = Heladeria()
    producto = heladeria.calcular_producto_mas_rentable()

    return render_template('main.html', ventas=utils.variables_generales.get_variable_ventas_del_dia(), producto=producto,
                           username=utils.variables_generales.get_variable_username())
        
#Agregar controladores para ingrediente y producto
app.route("/productos")(controller_producto.get_producto_all)
app.route("/productos/<id_producto>")(controller_producto.get_producto_by_id)
app.route("/productos/nombre/<nombre_producto>")(controller_producto.get_producto_by_name)
app.route("/productos/calorias/<id_producto>")(controller_producto.get_producto_by_id_calorias)
app.route("/productos/rentabilidad/<id_producto>")(controller_producto.get_rentabilidad_producto_by_id)
app.route("/productos/costo/<id_producto>")(controller_producto.get_costo_producto_by_id)

app.route("/ingredientes")(controller_ingrediente.get_ingrediente_all)
app.route("/ingredientes/<id_ingrediente>")(controller_ingrediente.get_ingrediente_by_id)
app.route("/ingredientes/nombre/<nombre_ingrediente>")(controller_ingrediente.get_ingrediente_by_name)
#Se usa el mismo método de consultar por id porque este retorna toda la información del ingrediente
app.route("/ingredientes/sano/<id_ingrediente>")(controller_ingrediente.get_ingrediente_by_id)
app.route("/ingredientes/abastecer/<id_ingrediente>")(controller_ingrediente.abastecer_by_id)

if __name__ == '__main__':
    app.run(debug=True)