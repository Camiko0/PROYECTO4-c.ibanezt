from models.usuario import Usuario

#Variable global y sus metodos para actualizar y consultar
ventas_del_dia = 0
username = ""
current_user = None

def reset_ventas_del_dia() -> None:
    global ventas_del_dia
    ventas_del_dia = 0

def set_variable_ventas_del_dia(ventas: int) -> None:
    global ventas_del_dia
    ventas_del_dia += ventas

def get_variable_ventas_del_dia() -> int:
    return ventas_del_dia

def set_variable_username(user: str) -> None:
    global username
    username = user

def get_variable_username() -> str:
    return username

def set_variable_current_user(user: Usuario) -> None:
    global current_user
    current_user = user

def get_variable_current_user() -> Usuario:
    return current_user