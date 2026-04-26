from conf import SUPER_ADMINS

# def is_super_admin(tg_id: int) -> bool:
#     return tg_id in SUPER_ADMINS

class AdminService:
    def __init__(self, ad_rp):
        self.ad_rp = ad_rp

    def is_super_admin(self, tg_id: int) -> bool:
        return tg_id in SUPER_ADMINS
