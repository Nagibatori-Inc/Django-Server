from django.urls import path

from support.views import ClientSupportMessagesAPIView, AgentSupportMessagesAPIView

urlpatterns = [
    path("support/messages/", ClientSupportMessagesAPIView.as_view(), name="client_support_messages"),
    path("support/<int:message_id>/answers/", AgentSupportMessagesAPIView.as_view(), name="agent_support_answers"),
]
