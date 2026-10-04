from getpass import getpass

from database import SessionLocal
from models.usuario import Usuario
from security import hash_password


def crear_administrador():
    db = SessionLocal()

    try:
        administrador_existente = db.query(Usuario).filter(
            Usuario.rol == "administrador"
        ).first()

        if administrador_existente is not None:
            print(
                "Ya existe un usuario administrador. "
                "No se creó otro."
            )
            return

        username = input(
            "Nombre del administrador: "
        ).strip()

        if len(username) < 3 or len(username) > 50:
            print(
                "El nombre debe tener entre 3 y 50 caracteres."
            )
            return

        usuario_existente = db.query(Usuario).filter(
            Usuario.username == username
        ).first()

        if usuario_existente is not None:
            print("Ese nombre de usuario ya existe.")
            return

        password = getpass(
            "Contraseña: "
        )

        confirmacion = getpass(
            "Repetir contraseña: "
        )

        if password != confirmacion:
            print("Las contraseñas no coinciden.")
            return

        if len(password) < 8 or len(password) > 72:
            print(
                "La contraseña debe tener entre "
                "8 y 72 caracteres."
            )
            return

        administrador = Usuario(
            username=username,
            password=hash_password(password),
            rol="administrador"
        )

        db.add(administrador)
        db.commit()

        print("Administrador creado correctamente.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    crear_administrador()