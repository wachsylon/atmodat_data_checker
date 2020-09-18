"""
nc_file_checks_register.py
==========================

A register of checks for NetCDF4 files.

"""

from netCDF4 import Dataset
from compliance_checker.base import Result
from checklib.register.callable_check_base import CallableCheckBase
from atmodat_checklib.utils import nc_util
from atmodat_checklib.utils.ess_vocabs_utils import ESSVocabsAtmodat
from checklib.code.errors import FileError


class NCFileCheckBase(CallableCheckBase):
    """Base class for all NetCDF4 File Checks (that work on a file path)."""

    def _check_primary_arg(self, primary_arg):
        if not isinstance(primary_arg, Dataset):
            raise FileError("Object for testing is not a netCDF4 Dataset: {}".format(str(primary_arg)))


class GobalAttrResolutionFormatCheck(NCFileCheckBase):
    """
    The global attribute '{attribute}' must be in number+unit format .
    """
    short_name = "Global attribute: {attribute}"
    defaults = {}
    required_args = ['attribute']
    message_templates = ["'{status}' '{attribute}' global attribute is not present.",
                         "'{status}' '{attribute}' No valid value+unit combination"]

    def _get_result(self, primary_arg):
        ds = primary_arg

        score = nc_util.check_global_attribute_resolution_format(ds, self.kwargs["attribute"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class GlobalAttrTypeCheck(NCFileCheckBase):
    """
    The global attribute '{attribute}' must have a valid type '{type}'.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {}
    required_args = ['attribute', 'type', 'status']
    message_templates = ["'{status}' '{attribute}' global attribute is not present.",
                         "'{status}' '{attribute}' global attribute value does not match "
                         "type '{type}'."]
    level = "HIGH"

    def _get_result(self, primary_arg):
        ds = primary_arg

        score = nc_util.check_global_attr_type(ds, self.kwargs["attribute"], self.kwargs["type"],)
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class DateISO8601Check(NCFileCheckBase):
    """
    The global attribute '{attribute}' must be a valid ISO 8601 date.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {}
    required_args = ['attribute']
    message_templates = ["{status} {attribute} global attribute is not present.",
                         "{status} {attribute} global attribute value does not match ISO8601"]
    level = "HIGH"

    def _get_result(self, primary_arg):
        ds = primary_arg

        score = nc_util.check_global_attr_iso8601(ds, self.kwargs["attribute"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)


class GlobalAttrVocabCheckByStatus(NCFileCheckBase):
    """
    The global attribute '{attribute}' must exist (if `status` = mandatory) and have a valid value
    from the relevant vocabulary.
    """
    short_name = "Global attribute: {attribute}"
    defaults = {"vocab_lookup": "canonical_name"}
    required_args = ['attribute', 'status']
    message_templates = ["{status} {attribute} global attribute is not present.",
                         "{status} {attribute} global attribute value is invalid."]
    level = "HIGH"

    def _get_result(self, primary_arg):
        ds = primary_arg
        vocabs = ESSVocabsAtmodat(*self.vocabulary_ref.split(":")[:2])

        score = vocabs.check_global_attribute(ds, self.kwargs["attribute"], property_check=self.kwargs["vocab_lookup"])
        messages = []

        if score < self.out_of:
            messages.append(self.get_messages()[score])

        return Result(self.level, (score, self.out_of),
                      self.get_short_name(), messages)
