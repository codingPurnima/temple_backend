from sqlalchemy import Enum
import enum

class UserRole(enum.Enum):
    NORMAL= "NORMAL"
    PREMIUM= "PREMIUM"
    ADMIN= "ADMIN"
    SUPER_ADMIN= "SUPER_ADMIN"