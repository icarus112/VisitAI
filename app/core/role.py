from app.core.enum import Role

# !!! это все нужно только для тестирование методов по разным ролям
class RoleCheck:
    @staticmethod
    def is_super_admin(role: str) -> bool:
        return role == Role.SUPER_ADMIN

    @staticmethod
    def is_admin(role: str) -> bool:
        return role in (Role.ADMIN, Role.SUPER_ADMIN)

    @staticmethod
    def is_user(role: str) -> bool:
        return role in (Role.USER, Role.ADMIN, Role.SUPER_ADMIN)