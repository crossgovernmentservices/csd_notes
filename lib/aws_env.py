# -*- coding: utf-8 -*-
"""
Fetch environment variables from credstash instead of os.environ
"""

from boto import ec2, utils
import credstash


class AWSInstanceEnv(object):

    def __init__(self):
        self._initialized = False
        self._region = None
        self._table = None
        self._version = None

    def _initialize(self):
        metadata = utils.get_instance_metadata(timeout=5, num_retries=1)
        instance_id = metadata['instance-id']

        self._region = metadata['placement']['availability-zone'][:-1]

        conn = ec2.connect_to_region(self._region)
        reservations = conn.get_all_instances(instance_ids=[instance_id])
        instance = reservations[0].instances[0]

        env = instance.tags['Environment']
        self._table = 'notes-{}-credentials'.format(env)
        self._version = instance.tags['ConfigVersion']
        self._initialized = True

    def __getitem__(self, key):
        """
        Enable dict-like access
        """

        if not self._initialized:
            self._initialize()

        return credstash.getSecret(
            key,
            version=self._version,
            region=self._region,
            table=self._table)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)

        except credstash.ItemNotFound:
            return default


env = AWSInstanceEnv()
