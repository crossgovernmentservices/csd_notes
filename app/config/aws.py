# -*- coding: utf-8 -*-
"""
Dictionary-like class for config settings from AWS credstash
"""

from boto import ec2, utils
import credstash


class AWSIntanceEnv(object):

    def __init__(self):
        metadata = utils.get_instance_metadata()
        self.instance_id = metadata['instance-id']
        self.region = metadata['placement']['availability-zone'][:-1]

        conn = ec2.connect_to_region(self.region)
        reservations = conn.get_all_instances(instance_ids=[self.instance_id])
        instance = reservations[0].instances[0]
        self.env = instance.tags['Environment']
        self.version = instance.tags['ConfigVersion']

    def getSecret(self, name, table=None, context=None, profile_name=None):
        """
        Low level API for fetching secrets for the current instance
        """

        if not table:
            table = '{}-credentials'.format(self.env)

        return credstash.getSecret(
            name,
            self.version,
            region=self.region,
            table=table,
            context=context,
            profile_name=profile_name)

    def __getitem__(self, key):
        """
        Enable dict-like access
        """

        return self.getSecret(key)

    def get(self, key, default=None):
        """
        Return the value, or the default if not found
        """

        try:
            return self.__getitem__(key)

        except credstash.ItemNotFound:
            return default
