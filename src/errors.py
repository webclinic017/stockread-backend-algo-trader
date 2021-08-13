# Copyright (C) 2021-2030 StockRead Inc.
# Author: Thanh Tung Nguyen
# Contact: tungstudies@gmail.com

"""algo-trading project exception classes."""
from typing import Optional


# DIVIDER: --------------------------------------
# INFO: MissingPrice ErrorClass

class MissingPrice(ValueError):
    """Basic exception for errors raised by brokers, orders and positions"""

    def __init__(self, class_name: str, price_type: str, message=None,
                 price_types: tuple = ('ref_price', 'stop_price', 'limit_price', 'filled_price', 'buy_price',
                                       'sell_price', 'market_price')):

        if price_type not in price_types:
            raise ValueError(f"InvalidPriceType: expected one of: {price_types}")
        else:
            self.price_types = price_types
            self.price_type = price_type

        self.class_name = class_name

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred with {self.class_name} class because {self.price_type} is missing"

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ClassHasError: {}'.format(self.class_name))
        tojoin.append('PriceTypes: {}'.format(self.price_types))
        tojoin.append('MissingPrice: {}'.format(self.price_type))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: ItemExistenceError Abstract ErrorClass

class ItemExistenceError(Exception):
    """Abstract exception for item-existence errors raised by brokers, orders and positions"""

    def __init__(self, class_name: str, item_type: str, is_non_exist: bool, message: str,
                 item_types: tuple = ('size', 'order')):

        if item_type not in item_types:
            raise ValueError(f"InvalidItemType: expected one of: {item_types}")
        else:
            self.item_types = item_types
            self.item_type = item_type

        self.class_name = class_name
        self.message = message
        self.is_non_exist: bool = is_non_exist

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ClassHasError: {}'.format(self.class_name))
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

    def __init__(self, class_name: str, item_type: str, message: str = '',
                 item_types: tuple = ('size', 'order')):

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred with {class_name} class because {item_type} does not exist"

        super().__init__(class_name=class_name, item_type=item_type, message=self.message, is_non_exist=True,
                         item_types=item_types)


# DIVIDER: --------------------------------------
# INFO: ItemAlreadyExistError ErrorClass

class ItemAlreadyExistError(ItemExistenceError):
    """Exception for item-non-existence errors raised by brokers, orders and positions"""

    def __init__(self, class_name: str, item_type: str, message: str = '',
                 item_types: tuple = ('size', 'order')):

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred with {class_name} class because {item_type} already exists"

        super().__init__(class_name=class_name, item_type=item_type, message=self.message, is_non_exist=False,
                         item_types=item_types)


# DIVIDER: --------------------------------------
# INFO: OrderTypeError ErrorClass

class OrderTypeError(TypeError):
    """Exception for order type errors raised by brokers, orders"""

    def __init__(self, class_name: str, expected_type: str = '', unexpected_type: str = '',
                 order_types=('market', 'limit', 'stop', 'stop_limit'), message=None):

        if message:
            self.message = message
        else:
            tojoin = list(f"An order type error occurred with {class_name} class")
            if expected_type:
                if expected_type not in order_types:
                    raise ValueError(f"InvalidOrderType: expected one of: {order_types}")
                else:
                    tojoin.append(f'Expected {expected_type} order')

            if unexpected_type:
                tojoin.append(f'Got unexpected {unexpected_type} order')

            self.message = '. '.join(tojoin)

        super().__init__(self.message)

        self.class_name = class_name
        self.expected_type = expected_type
        self.unexpected_type = unexpected_type

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ClassHasError: {}'.format(self.class_name))
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

    def __init__(self, class_name: str, element_type: str, message=None,
                 element_types: tuple = ('trading_account_id', 'ticker_id', 'trading_symbol',
                                         'currency', 'position', 'connection')):

        if element_type not in element_types:
            raise ValueError(f"InvalidElementType: expected one of: {element_types}")
        else:
            self.element_types = element_types
            self.element_type = element_type

        self.class_name = class_name

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An error occurred with {self.class_name} class. The {self.element_type} " \
                           f"is missing while setting up a {self.class_name} instance"

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ClassHasError: {}'.format(self.class_name))
        tojoin.append('ElementTypes: {}'.format(self.element_types))
        tojoin.append('MissingElement: {}'.format(self.element_type))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: MissingRequiredTradingElement ErrorClass

class InvalidOrderListCUD(ValueError):
    """Ticker symbol conflicts between 02 trading components (i.e.: order vs broker, order vs position, etc., ...)"""

    def __init__(self, class_name: str, operation: str, order_list_type: str, additional_msg: str = '',
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
            tojoin = list(f"An order type error occurred with {class_name} class. "
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

        self.class_name = class_name
        self.operation = operation
        self.operation_types = operation_types
        self.order_list_type = order_list_type
        self.list_types = list_types
        self.expected_list = expected_order
        self.unexpected_list = unexpected_order

    def __str__(self):
        tojoin = list()
        tojoin.append('ClassHasError: {}'.format(self.class_name))
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

    def __init__(self, class_name: str, provided_input: str, input_types: tuple, expected_corresponding_input: str,
                 unexpected_corresponding_input: str, corresponding_input_types: tuple, message=None):

        if provided_input not in input_types:
            raise ValueError(f"InvalidInputType: provided_input is expected one of: {input_types}")

        if expected_corresponding_input not in corresponding_input_types or \
                unexpected_corresponding_input not in corresponding_input_types:
            raise ValueError(f"InvalidInputType: expected_corresponding_input and "
                             f"unexpected_corresponding_input is expected one of: {input_types}")

        self.class_name = class_name
        self.provided_input = provided_input
        self.input_types = input_types
        self.expected_corresponding_input = expected_corresponding_input
        self.unexpected_corresponding_input = unexpected_corresponding_input
        self.corresponding_input_types = corresponding_input_types

        if message:
            self.message = message
        else:
            # Set some default useful error message
            self.message = f"An input parameter conflict error occurred with {self.class_name} class. " \
                           f"The {self.class_name.lower()} is {self.provided_input.upper()} and it requires " \
                           f"{self.expected_corresponding_input.upper()} instead of " \
                           f"{self.unexpected_corresponding_input.upper()}."

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ClassHasError: {}'.format(self.class_name))
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

    def __init__(self, class_name: str, expected_live_broker: bool, message=None):

        self.expected_broker_type = 'live' if expected_live_broker else 'back'
        self.unexpected_broker_type = 'live' if not expected_live_broker else 'back'
        self.class_name = class_name

        if message:
            self.message = message
        else:

            self.message = f"An broker type conflict occurred with {self.class_name} class. " \
                           f"Expected {self.expected_broker_type} broker. " \
                           f"Got {self.unexpected_broker_type} broker instead"

        super().__init__(self.message)

    def __str__(self):
        tojoin = list()
        tojoin.append('Message: {}'.format(self.message))
        tojoin.append('ClassHasError: {}'.format(self.class_name))
        tojoin.append('ExpectedBrokerType: {}'.format(self.class_name))
        tojoin.append('UnexpectedBrokerType: {}'.format(self.unexpected_broker_type))

        return '\n '.join(tojoin)


# DIVIDER: --------------------------------------
# INFO: TickerIDNotFoundError ErrorClass

class TickerIDNotFoundError(Exception):
    """Error thrown when a broker cannot find any ticker ID matching the provided security ticker symbol"""

    def __init__(self, class_name: str, ticker_symbol: str):
        super().__init__(
            f"Broker {class_name} cannot find a corresponding ticker_id for {ticker_symbol}"
        )
