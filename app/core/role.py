from app.core.enum import AdminRole

# !!! это все нужно только для тестирование методов по разным ролям
class RoleCheck:
    @staticmethod
    def is_super_admin(role: str) -> bool:
        return role == AdminRole.SUPER_ADMIN

    @staticmethod
    def is_admin(role: str) -> bool:
        return role in (AdminRole.ADMIN, AdminRole.SUPER_ADMIN)

    @staticmethod
    def is_user(role: str) -> bool:
        return role in (AdminRole.USER, AdminRole.ADMIN, AdminRole.SUPER_ADMIN)