from locker_server.core.exceptions.app import CoreException


class PaymentException(CoreException):
    """
    Payment base exception
    """


class PaymentMethodNotSupportException(PaymentException):
    """

    """

    def __init__(self, payment_method, message="Payment method is not support"):
        message = "Payment method {} is not supported".format(payment_method) if payment_method else message
        super(PaymentMethodNotSupportException, self).__init__(message)
        self._payment_method = payment_method

    @property
    def payment_method(self):
        return self._payment_method


class PaymentInvoiceDoesNotExistException(PaymentException):
    """
    The payment does not exist
    """


class PaymentPromoCodeInvalidException(PaymentException):
    """
    The promo code is invalid
    """


class PaymentNotFoundCardException(PaymentException):
    """
    The user does not any card
    """
