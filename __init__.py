from .genero import (
    create_genero,
    get_genero,
    get_generos,
    update_genero,
    delete_genero
)
from .usuario import (
    create_user,
    authenticate_user,
    get_user_by_username,
    get_user,
    get_users,  # Usa directamente get_users
    update_user,
    delete_user,
    get_user_by_id  # Mantén esta función
)