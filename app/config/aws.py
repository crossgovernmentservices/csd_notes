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

    def getSecret(self, name, table="credential-store", context=None,
                  profile_name=None):
        return credstash.getSecret(
            name,
            self.version,
            region=self.region,
            table=table,
            context=context,
            profile_name=profile_name)

    def __getitem__(self, key):
        return self.getSecret(key, table='{}-credentials'.format(self.env))

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)

        except credstash.ItemNotFound:
            return default
