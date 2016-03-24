from unittest.mock import patch

from app.factory import create_app


class TestWhenDeployedInAWS(object):

    def test_it_fetches_secrets_from_credstash(self):

        patcher = patch('lib.aws_env.env.__getitem__')
        get = patcher.start()
        expected = 'fetched from credstash'
        get.return_value = expected

        with patch.dict('os.environ', SETTINGS='AWS'):
            test_app = create_app()
            assert test_app.config['SECRET_KEY'] == expected

        patcher.stop()
