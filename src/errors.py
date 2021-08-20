# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

"""algo-trading project exception classes."""


# DIVIDER: --------------------------------------
# INFO: SignalNotRequiredException ErrorClass
class SignalNotRequiredException(ValueError):
    """Missing trading required elements while setting up trading component such as brokers, trades, strategies"""

    def __init__(self, signal_type: str, signal_types: tuple = ('leading', 'trailing')):

        if signal_type not in signal_types:
            raise ValueNotPresentException(provided_value=signal_type, value_list=signal_types)
        else:
            super().__init__(f'{signal_type.title()} dependent signal is not required')


# DIVIDER: --------------------------------------
# INFO: SignalNotRequiredException ErrorClass
class MissingDependentSignalError(ValueError):
    """Missing trading required elements while setting up trading component such as brokers, trades, strategies"""

    def __init__(self, signal_type: str, signal_types: tuple = ('leading', 'following', 'both')):

        if signal_type not in signal_types:
            raise ValueNotPresentException(provided_value=signal_type, value_list=signal_types)
        else:
            if signal_type == 'both':
                text_str = "Both leading and trailing"
            else:
                text_str = signal_type.title()

            super().__init__(f'{text_str} dependent signal(s) is/are required but missing')


# DIVIDER: --------------------------------------
# INFO: DependentSignalConflict ErrorClass
class DependentSignalConflict(ValueError):
    """Error thrown when a signal has a type conflict with its dependent signal"""

    def __init__(self, isbuy: bool):
        super().__init__(f'Dependent signal is required to be a {"BUY" if isbuy else "SELL"}')


# DIVIDER: --------------------------------------
# INFO: UnsettledOrderPersistError ErrorClass
class UnsettledOrderPersistError(Exception):
    """Error thrown when there are unsettled orders by next data bar"""

    def __init__(self, order, additional_msg: str = 'It is required to remove the settled '
                                                    'order before the next data refresh.\n'
                                                    'Please check the order removal logic & procedure.'):
        super().__init__(
            f"There is an unsettled order in the trade has not been removed.\n"
            f"Order details: {order}.\n"
            f"{additional_msg}"
        )


# DIVIDER: --------------------------------------
# INFO: MultiplePendingOrderException ErrorClass
class MultiplePendingOrderException(Exception):
    """Error thrown when there are more than 01 pending regular orders/stop orders at any given time"""

    def __init__(self, pending_orders, is_regular_order: bool,
                 additional_msg: str = 'It is required to have no more than 01 unsettled order at any given time.\n '
                                       'Please check the order removal logic & procedure.'):
        order_type = 'regular' if is_regular_order else 'stop'

        super().__init__(
            f"There are more than 01 unsettled {order_type} orders submitted to the broker.\n"
            f"Order details: {pending_orders}.\n"
            f"{additional_msg}"
        )


# DIVIDER: --------------------------------------
# INFO: PendingOrderNotInPendingListError ErrorClass

class PendingOrderNotInPendingListError(ValueError):
    """Error thrown when a pending order is not captured in the broker pending order list"""

    def __init__(self, order):
        super().__init__(
            f"The pending order was not captured in the broker pending order list. \n Order details: {order}"
        )


# DIVIDER: --------------------------------------
# INFO: PositionRequestError ErrorClass

class PositionRequestError(ValueError):
    def __init__(self, position, error):
        super().__init__(
            f"An error occurred while requesting for position information of {position}. \n Error details: {error}"
        )


# DIVIDER: --------------------------------------
# INFO: MissingOrderAttributeError ErrorClass

class MissingOrderAttributeError(ValueError):
    """Missing trading required elements while setting up trading component such as brokers, trades, strategies"""

    def __init__(self, attribute: str, message=None,
                 attribute_list: tuple = ('client_ref_id', 'trading_symbol', 'ticker_id', 'ref_price', 'size',
                                          'isbuy', 'status', 'created_at', 'created_timestamp', 'order_type',
                                          'broker_ref_id', 'is_broker_settled',
                                          'broker_traded_symbol', 'filled_price', 'transaction_value'
                                                                                  'filled_at', 'filled_timestamp',
                                          'fill_quantity', 'commission_fee'
                                          )):

        if attribute not in attribute_list:
            raise ValueNotPresentException(provided_value=attribute, value_list=attribute_list)
        else:

            self.attribute = attribute
            self.attribute_list = attribute_list

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred. The <<{self.attribute_list}>> attribute" \
                           f"is missing while setting up a trading order"

        super().__init__(self.message)


# DIVIDER: --------------------------------------
# INFO: TickerIDNotFoundError ErrorClass

class TickerIDNotFoundError(Exception):
    """Error thrown when a broker cannot find any ticker ID matching the provided security ticker symbol"""

    def __init__(self, ticker_symbol: str):
        super().__init__(
            f"Unable to find a corresponding ticker_id for {ticker_symbol}"
        )


# DIVIDER: --------------------------------------
# INFO: OrderPlacingError ErrorClass

class OrderPlacingError(Exception):
    """Error thrown when orders cannot be submitted to brokers or errors from brokers while placing orders"""

    def __init__(self, order, error):
        super().__init__(
            f"An error occurred while submitting the trading order -\n{order}.\nError details: {error}"
        )


# DIVIDER: --------------------------------------
# INFO: ValueNotPresentException ErrorClass

class ValueNotPresentException(ValueError):
    """Error thrown when a value is not found in a particular list of values"""

    def __init__(self, provided_value: str, value_list):
        super().__init__(f"Provided input value {provided_value} is expected to be one of: {value_list}")


# DIVIDER: --------------------------------------
# INFO: MissingPrice ErrorClass

class MissingPrice(ValueError):
    """Basic exception for errors raised by brokers, orders and positions"""

    def __init__(self, price_type: str, message=None,
                 price_types: tuple = ('ref_price', 'stop_price', 'limit_price', 'filled_price', 'buy_price',
                                       'sell_price', 'market_price')):

        if price_type not in price_types:
            raise ValueNotPresentException(provided_value=price_type, value_list=price_types)
        else:
            self.price_types = price_types
            self.price_type = price_type

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred because the {self.price_type} is missing"

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('PriceTypes: {}'.format(self.price_types))
        tojoin.append('MissingPrice: {}'.format(self.price_type))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: ItemExistenceError Abstract ErrorClass

class ItemExistenceError(Exception):
    """Abstract exception for item-existence errors raised by brokers, orders and positions"""

    def __init__(self, item_type: str, is_non_exist: bool, message: str,
                 item_types: tuple = ('size', 'order')):

        if item_type not in item_types:
            raise ValueNotPresentException(provided_value=item_type, value_list=item_types)
        else:
            self.item_types = item_types
            self.item_type = item_type

        self.message = message
        self.is_non_exist: bool = is_non_exist

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ItemTypes: {}'.format(self.item_types))
        if self.is_non_exist:
            tojoin.append('ItemHasNonExistenceError: {}'.format(self.item_type))
        else:
            tojoin.append('ItemHasAlreadyExistError: {}'.format(self.item_type))
        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: ItemExistenceError ErrorClass

class ItemNonExistenceError(ItemExistenceError):
    """Exception for item-non-existence errors raised by brokers, orders and positions"""

    def __init__(self, item_type: str, message: str = '',
                 item_types: tuple = ('size', 'order')):

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred because {item_type} does not exist"

        super().__init__(item_type=item_type, message=self.message, is_non_exist=True,
                         item_types=item_types)


# DIVIDER: --------------------------------------
# INFO: ItemAlreadyExistError ErrorClass

class ItemAlreadyExistError(ItemExistenceError):
    """Exception for item-non-existence errors raised by brokers, orders and positions"""

    def __init__(self, item_type: str, message: str = '',
                 item_types: tuple = ('size', 'order')):

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred because {item_type} already exists"

        super().__init__(item_type=item_type, message=self.message, is_non_exist=False,
                         item_types=item_types)


# DIVIDER: --------------------------------------
# INFO: OrderTypeError ErrorClass

class OrderTypeError(TypeError):
    """Exception for order type errors raised by brokers, orders"""

    def __init__(self, expected_type: str = '', unexpected_type: str = '',
                 order_types=('market', 'limit', 'stop', 'stop_limit'), message=None):

        if message:
            self.message = message
        else:
            tojoin = list(f"An order type error occurred.")
            if expected_type:
                if expected_type not in order_types:
                    raise ValueNotPresentException(provided_value=expected_type, value_list=order_types)
                else:
                    tojoin.append(f'Expected {expected_type} order')

            if unexpected_type:
                tojoin.append(f'Got unexpected {unexpected_type} order')

            self.message = '. '.join(tojoin)

        super().__init__(self.message)

        self.expected_type = expected_type
        self.unexpected_type = unexpected_type

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        if self.expected_type:
            tojoin.append('MissingExpectedOrderType: {}'.format(self.expected_type))
        if self.unexpected_type:
            tojoin.append('UnexpectedOrderTypeReturn: {}'.format(self.unexpected_type))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: UnmatchedTickerError ErrorClass

class UnmatchedTickerError(ValueError):
    """Ticker symbol conflicts between 02 trading components (i.e.: order vs broker, order vs position, etc., ...)"""

    def __init__(self, primary_class_name: str, primary_class_ticker: str,
                 foreign_class_name: str, foreign_class_ticker: str, message=None):
        self.primary_class_name = primary_class_name
        self.primary_class_ticker = primary_class_ticker
        self.foreign_class_name = foreign_class_name
        self.foreign_class_ticker = foreign_class_ticker

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred with {self.primary_class_name} class. There is as ticker conflict " \
                           f"between primary class {self.primary_class_name} with ticker {self.primary_class_ticker} " \
                           f"AND foreign class {self.foreign_class_name} with ticker {self.foreign_class_ticker}"

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ClassHasError: {}'.format(self.primary_class_name))
        tojoin.append('PrimaryClass: {}'.format(self.primary_class_name))
        tojoin.append('PrimaryClassTicker: {}'.format(self.primary_class_name))
        tojoin.append('ForeignClass: {}'.format(self.foreign_class_name))
        tojoin.append('ForeignClassTicker: {}'.format(self.foreign_class_ticker))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: MissingRequiredTradingElement ErrorClass

class MissingRequiredTradingElement(ValueError):
    """Missing trading required elements while setting up trading component such as brokers, trades, strategies"""

    def __init__(self, element_type: str, message=None,
                 element_types: tuple = ('trading_account_id', 'ticker_id', 'trading_symbol', 'currency', 'position',
                                         'connection', 'trader', 'sizer', 'quoter', 'broker', 'cash', 'strategy',
                                         'gain_loss_tracker', 'ticker_alias', 'market_hour', 'stop_order_pricer')):

        if element_type not in element_types:
            raise ValueError(f"InvalidElementType: expected one of: {element_types}")
        else:
            self.element_types = element_types
            self.element_type = element_type

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred. The {self.element_type} " \
                           f"is missing while setting up a class instance"

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ElementTypes: {}'.format(self.element_types))
        tojoin.append('MissingElement: {}'.format(self.element_type))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: MissingRequiredTradingElement ErrorClass

class InvalidOrderListCUD(ValueError):
    """Ticker symbol conflicts between 02 trading components (i.e.: order vs broker, order vs position, etc., ...)"""

    def __init__(self, operation: str, order_list_type: str, additional_msg: str = '',
                 expected_order: str = '', unexpected_order: str = '', list_types: tuple = ('pending', 'settled'),
                 operation_types: tuple = ('update', 'insert', 'delete'), message=None):

        if operation not in operation_types:
            raise ValueError(f"InvalidOperation: operation is expected one of: {operation_types}")

        if order_list_type not in list_types:
            raise ValueError(f"InvalidOrderListType: order_list_type, expected_list, unexpected_list "
                             f"is expected one of: {operation_types}")

        if message:
            self.message = message

        else:
            tojoin = list(f"An order type error occurred. "
                          f"An invalid {str(operation).upper()} was performed on {str(order_list_type)}")
            if expected_order:
                if expected_order not in list_types:
                    raise ValueError(f"InvalidOrderStatusType: expected_order is expected one of: {operation_types}")
                else:
                    tojoin.append(f'Expected {expected_order} order')

            if unexpected_order:
                if unexpected_order not in list_types:
                    raise ValueError(f"InvalidOrderStatusType: unexpected_order is expected one of: {operation_types}")
                else:
                    tojoin.append(f'Got unexpected {unexpected_order} order')

            if additional_msg:
                tojoin.append(additional_msg)

            self.message = '. '.join(tojoin)

        super().__init__(self.message)

        self.operation = operation
        self.operation_types = operation_types
        self.order_list_type = order_list_type
        self.list_types = list_types
        self.expected_list = expected_order
        self.unexpected_list = unexpected_order

    def __str__(self):
        tojoin = list()
        tojoin.append('InvalidOperation: {}'.format(self.operation))
        tojoin.append('OperationTypes: {}'.format(self.operation_types))
        tojoin.append('OrderListType: {}'.format(self.order_list_type))
        tojoin.append('OrderListTypes: {}'.format(self.list_types))

        if self.expected_list:
            tojoin.append('ExpectedOrderList: {}'.format(self.expected_list))
        if self.unexpected_list:
            tojoin.append('UnexpectedOrderList: {}'.format(self.unexpected_list))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: ItemExistenceError Abstract ErrorClass

class InputParameterConflict(ValueError):
    """Constructor/Setter input parameter conflicts between 02 provide target input type (i.e.: by-size sizer)
     and corresponding input (i.e.: cash amount instead of size value)"""

    def __init__(self, provided_input: str, input_types: tuple, expected_corresponding_input: str,
                 unexpected_corresponding_input: str, corresponding_input_types: tuple, message=None):

        if provided_input not in input_types:
            raise ValueError(f"InvalidInputType: provided_input is expected one of: {input_types}")

        if expected_corresponding_input not in corresponding_input_types or \
                unexpected_corresponding_input not in corresponding_input_types:
            raise ValueError(f"InvalidInputType: expected_corresponding_input and "
                             f"unexpected_corresponding_input is expected one of: {input_types}")

        self.provided_input = provided_input
        self.input_types = input_types
        self.expected_corresponding_input = expected_corresponding_input
        self.unexpected_corresponding_input = unexpected_corresponding_input
        self.corresponding_input_types = corresponding_input_types

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An input parameter conflict error." \
                           f"The {self.provided_input.upper()} input parameter requires " \
                           f"{self.expected_corresponding_input.upper()} instead of " \
                           f"{self.unexpected_corresponding_input.upper()}."

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ProvidedInput: {}'.format(self.provided_input))
        tojoin.append('InputTypes: {}'.format(self.input_types))
        tojoin.append('ExpectedCorrespondingInput: {}'.format(self.expected_corresponding_input))
        tojoin.append('UnexpectedCorrespondingInput: {}'.format(self.unexpected_corresponding_input))
        tojoin.append('CorrespondingInputTypes: {}'.format(self.corresponding_input_types))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: BrokerTypeError ErrorClass

class BrokerTypeError(TypeError):
    """Exception for broker type errors raised by brokers, strategies, trades"""

    def __init__(self, expected_live_broker: bool, message=None):

        self.expected_broker_type = 'live' if expected_live_broker else 'back'
        self.unexpected_broker_type = 'live' if not expected_live_broker else 'back'

        if message:
            self.message = message
        else:

            self.message = f"An broker type conflict occurred. " \
                           f"Expected {self.expected_broker_type} broker. " \
                           f"Got {self.unexpected_broker_type} broker instead"

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ExpectedBrokerType: {}'.format(self.expected_broker_type))
        tojoin.append('UnexpectedBrokerType: {}'.format(self.unexpected_broker_type))

        return '\n '.join(tojoin)


if __name__ == '__main__':
    raise MissingPrice(price_type='limit_price')
