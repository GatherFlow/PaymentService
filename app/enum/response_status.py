
import enum


class CreatePaymentStatus(enum.Enum):
    ok = "ok"
    unexpected_error = "unexpected_error"

    no_ticket_error = "no_event_ticket_error"
    no_event_ticket_error = "no_event_ticket_error"
    no_sub_error = "no_sub_error"
    unknown_gateway_error = "unknown_gateway_error"


class GetPaymentStatus(enum.Enum):
    ok = "ok"
    unexpected_error = "unexpected_error"

    no_payment_error = "no_payment_error"
