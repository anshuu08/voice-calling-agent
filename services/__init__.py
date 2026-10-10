"""
TakeRemo — Decoupled Business Service Layer
Separates business logic and mock data from HTTP controllers/routes.
Allows future database, Excel processing, telephony, and AI adapters
to be plugged in seamlessly without changing frontend contracts.
"""

from .admin_service import AdminService
from .recruitment_service import RecruitmentService
from .sales_service import SalesService
from .support_service import SupportService
from .conversation_service import ConversationService
from .call_service import CallService

# CamelCase and snake_case aliases for flexible imports
adminService = AdminService
recruitmentService = RecruitmentService
salesService = SalesService
supportService = SupportService
conversationService = ConversationService
callService = CallService

__all__ = [
    'AdminService',
    'adminService',
    'RecruitmentService',
    'recruitmentService',
    'SalesService',
    'salesService',
    'SupportService',
    'supportService',
    'ConversationService',
    'conversationService',
    'CallService',
    'callService',
]
