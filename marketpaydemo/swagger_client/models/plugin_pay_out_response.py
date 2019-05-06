# coding: utf-8

"""
    MarketPay API

    API for Smart Contracts and Payments  # noqa: E501

    OpenAPI spec version: v2.01
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from swagger_client.models.money import Money  # noqa: F401,E501


class PluginPayOutResponse(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'debited_funds': 'Money',
        'debited_wallet_id': 'str',
        'id': 'str',
        'creation_date': 'int',
        'tag': 'str'
    }

    attribute_map = {
        'debited_funds': 'DebitedFunds',
        'debited_wallet_id': 'DebitedWalletId',
        'id': 'Id',
        'creation_date': 'CreationDate',
        'tag': 'Tag'
    }

    def __init__(self, debited_funds=None, debited_wallet_id=None, id=None, creation_date=None, tag=None):  # noqa: E501
        """PluginPayOutResponse - a model defined in Swagger"""  # noqa: E501

        self._debited_funds = None
        self._debited_wallet_id = None
        self._id = None
        self._creation_date = None
        self._tag = None
        self.discriminator = None

        if debited_funds is not None:
            self.debited_funds = debited_funds
        if debited_wallet_id is not None:
            self.debited_wallet_id = debited_wallet_id
        if id is not None:
            self.id = id
        if creation_date is not None:
            self.creation_date = creation_date
        if tag is not None:
            self.tag = tag

    @property
    def debited_funds(self):
        """Gets the debited_funds of this PluginPayOutResponse.  # noqa: E501


        :return: The debited_funds of this PluginPayOutResponse.  # noqa: E501
        :rtype: Money
        """
        return self._debited_funds

    @debited_funds.setter
    def debited_funds(self, debited_funds):
        """Sets the debited_funds of this PluginPayOutResponse.


        :param debited_funds: The debited_funds of this PluginPayOutResponse.  # noqa: E501
        :type: Money
        """

        self._debited_funds = debited_funds

    @property
    def debited_wallet_id(self):
        """Gets the debited_wallet_id of this PluginPayOutResponse.  # noqa: E501


        :return: The debited_wallet_id of this PluginPayOutResponse.  # noqa: E501
        :rtype: str
        """
        return self._debited_wallet_id

    @debited_wallet_id.setter
    def debited_wallet_id(self, debited_wallet_id):
        """Sets the debited_wallet_id of this PluginPayOutResponse.


        :param debited_wallet_id: The debited_wallet_id of this PluginPayOutResponse.  # noqa: E501
        :type: str
        """

        self._debited_wallet_id = debited_wallet_id

    @property
    def id(self):
        """Gets the id of this PluginPayOutResponse.  # noqa: E501

        The item's ID  # noqa: E501

        :return: The id of this PluginPayOutResponse.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this PluginPayOutResponse.

        The item's ID  # noqa: E501

        :param id: The id of this PluginPayOutResponse.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def creation_date(self):
        """Gets the creation_date of this PluginPayOutResponse.  # noqa: E501

        When the item was created  # noqa: E501

        :return: The creation_date of this PluginPayOutResponse.  # noqa: E501
        :rtype: int
        """
        return self._creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        """Sets the creation_date of this PluginPayOutResponse.

        When the item was created  # noqa: E501

        :param creation_date: The creation_date of this PluginPayOutResponse.  # noqa: E501
        :type: int
        """

        self._creation_date = creation_date

    @property
    def tag(self):
        """Gets the tag of this PluginPayOutResponse.  # noqa: E501

        Custom data that you can add to this item  # noqa: E501

        :return: The tag of this PluginPayOutResponse.  # noqa: E501
        :rtype: str
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """Sets the tag of this PluginPayOutResponse.

        Custom data that you can add to this item  # noqa: E501

        :param tag: The tag of this PluginPayOutResponse.  # noqa: E501
        :type: str
        """

        self._tag = tag

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(PluginPayOutResponse, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, PluginPayOutResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
