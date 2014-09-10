#!/usr/bin/python

#    This file is part of Morse.
#
#    Morse is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Morse is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Morse.  If not, see <http://www.gnu.org/licenses/>.

from iptools import IpRange
from flask import jsonify, request

def json_input (schema_dict, optional = {}):

    """ 
    json_input is a function decorator that makes sure,
    that a json request has a certain format, if not it returns
    a 400 status and a json object with details about the 
    problem.

    if you want e.g. a json object structured like
    { id: 3, title: "hello", content: "hello world<br>" }
    
    you invoke json_input with
    json_input({"id": Number, "title": String, "content": HTML})
    """

    # Note: this is only a wrapper to allow named argument calling
    # For the inner workings see _json_input

    def _wrapper (f):
        return _json_input(f, schema_dict, optional)
    return _wrapper


class _json_input (object):

    def __init__ (self, f, schema_dict, optional):
        self.f = f
        self.schema_dict = schema_dict
        self.optional = optional
        # needed for flask integration
        self.__name__ = self.f.__name__

    def __call__ (self, *args, **kwargs):

        for attribute in self.schema_dict:

            if not attribute in request.json:
                return jsonify(errorCode = 1, errorMessage = "Missing attribute: " + attribute), 400

            value = request.json[attribute]
            validator = self.schema_dict[attribute]
            is_valid = validator.validate(value)
            if not is_valid:
                return jsonify(errorCode = 2, rejectedAttribute = attribute, errorMessage = "Attribute " + attribute + " is invalid"), 400

        for attribute in self.optional:

            if not attribute in request.json:
                continue
            
            value = request.json[attribute]
            validator = self.optional[attribute]
            is_valid = validator.validate(value)
            if not is_valid:
                return jsonify(errorCode = 2, rejectedAttribute = attribute, errorMessage = "Attribute " + attribute + " is invalid"), 400

        return self.f(*args, **kwargs)

class Validator (object):

    def validate (self, value):
        raise NotImplementedError(self.__class__.__name__ + " doesn't have a validate method")

class Boolean (Validator):

    def validate (self, value):
        print value, type(value)
        return type(value) is bool

class String (Validator):

    def __init__ (self, may_be_empty = True):
        self.may_be_empty = True

    def validate (self, value):
        value = value.replace(" ", "")
        value = value.replace("\t", "")
        return (type(value) is str or type(value) is unicode) and (value != "" or self.may_be_empty)

class Integer (Validator):

    def validate (self, value):
        return type(value) is int

class List (Validator):

    def __init__ (self, inner_validator):
        self.inner_validator = inner_validator

    def validate (self, value):
        if not type(value) is list:
            return False
        for element in value:
            is_valid = self.inner_validator.validate(element)
            if not is_valid:
                return False
                break
        return True

class Pair (Validator):

    def __init__ (self, first_validator, second_validator):
        self.first_validator = first_validator
        self.second_validator = second_validator

    def validate (self, value):
        if not type(value) is list:
            return False
        if not len(value) == 2:
            return False
        first_valid = self.first_validator.validate(value[0])
        second_valid = self.second_validator.validate(value[1])
        if not (first_valid and second_valid):
            return False
        return True

class IPRange (Validator):

    def validate (self, value):
        try:
            test = IpRange(value)
            return True
        except:
            return False

