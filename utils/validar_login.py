
from flask import jsonify
from flask import render_template
import utils.variables_generales
from models.enum_roles import Roles_Enum
from functools import wraps

def is_login() -> bool:
    return utils.variables_generales.get_variable_current_user()

# Función para obtener el rol del usuario y validar si tiene permisos para acceder a la ruta de la api
def validar_rol(rol: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario = utils.variables_generales.get_variable_current_user()
            #Valida dependiendo del rol, si coincide deja continuar sino envia 403 con mensaje
            if usuario:
                match rol:
                    case Roles_Enum.ADMIN:
                        if (usuario.es_admin):
                            return f(*args, **kwargs)
                    case Roles_Enum.EMPLEADO:
                        if (usuario.es_empleado or usuario.es_admin):
                            return f(*args, **kwargs)
                    case Roles_Enum.CLIENTE:
                        if ((not usuario.es_admin and not usuario.es_empleado) or usuario.es_empleado or usuario.es_admin):
                            return f(*args, **kwargs)
                #return jsonify({'message': 'No autorizado. Acceso denegado'}), 403
                return render_template('acceso_denegado.html')
            else:
                return render_template('acceso_denegado.html')
        return decorated_function
    return decorator