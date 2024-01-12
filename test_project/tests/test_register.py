import json
from abc import abstractmethod
from smtplib import SMTPException
from unittest import mock

from graphql_auth.constants import Messages
from graphql_auth.exceptions import EmailAlreadyInUseError
from graphql_auth.signals import user_registered

from .testCases import BaseTestCase


class RegisterBaseTestCase(BaseTestCase):
    RESPONSE_RESULT_KEY: str

    @abstractmethod
    def register_query(self, password='aaa&&111', username='username'):
        raise NotImplementedError()

    @abstractmethod
    def register_query_b(self, password='aaa&&111', username='username'):
        raise NotImplementedError()

    @abstractmethod
    def verify_query(self, token):
        raise NotImplementedError()

    def _test_register_invalid_password_validation(self):
        response = self.query(self.register_query('123'))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIn('password2', result['errors'].keys())

    def _test_register(self):
        """Register user, fail to register same user again"""
        signal_received = False

        def receive_signal(sender, user, signal):
            self.assertTrue(user.id is not None)
            nonlocal signal_received
            signal_received = True

        user_registered.connect(receive_signal)

        # register successfully
        response = self.query(self.register_query())
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertTrue(result['success'])
        self.assertIsNone(result['errors'])
        self.assertIsNotNone(result['token'])
        self.assertIsNotNone(result['refreshToken'])
        self.assertTrue(signal_received)

        # try to register again
        response = self.query(self.register_query())
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIsNone(result['token'])
        self.assertIsNone(result['refreshToken'])
        self.assertIn('username', result['errors'].keys())

        # try to register again with other username
        response = self.query(self.register_query(username='other_username'))
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIsNone(result['token'])
        self.assertIsNone(result['refreshToken'])
        self.assertEqual(result['errors'], Messages.EMAIL_IN_USE)

    def _test_register_with_mocked_async_email_func(self):
        """Register user, fail to register same user again"""
        with mock.patch('graphql_auth.mixins.async_email_func') as async_email_mock:
            response = self.query(self.register_query())
        result = self.get_response_result(response)
        self.assertEqual(result['success'], True)
        self.assertTrue(result['token'])
        self.assertTrue(result['refreshToken'])
        self.assertTrue(async_email_mock.called)

    def _test_register_with_standard_email_func(self):
        """Register user, fail to register same user again"""
        with self.settings(EMAIL_ASYNC_TASK=None):
            with mock.patch('graphql_auth.models.UserStatus.send_activation_email') as send_email_mock:
                response = self.query(self.register_query())
        result = self.get_response_result(response)
        self.assertEqual(result['success'], True)
        self.assertTrue(result['token'])
        self.assertTrue(result['refreshToken'])
        self.assertTrue(send_email_mock.called)

    def _test_register_duplicate_unique_email(self):
        self.register_user(
            email='foo@email.com',
            username='foo',
            verified=True,
            secondary_email='test@email.com',
        )
        response = self.query(self.register_query())
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertEqual(result['errors'], Messages.EMAIL_IN_USE)

    @mock.patch(
        'graphql_auth.models.UserStatus.send_activation_email',
        mock.MagicMock(side_effect=SMTPException),
    )
    def _test_register_email_send_fail(self):
        response = self.query(self.register_query())
        self.assertResponseNoErrors(response)
        result = self.get_response_result(response)
        self.assertFalse(result['success'])
        self.assertIsNone(result['token'])
        self.assertEqual(result['errors'], Messages.FAILED_SENDING_ACTIVATION_EMAIL)



class RegisterTestCase(RegisterBaseTestCase):
    RESPONSE_RESULT_KEY = 'register'

    def register_query(self, password='aaa&&111', username='username'):
        return '''
        mutation {
            register(
                email: "test@email.com",
                username: "%s",
                password1: "%s",
                password2: "%s"
            )
            { success, errors, token, refreshToken }
        }
        ''' % (
            username,
            password,
            password,
        )

    def register_query_b(self, password='aaa&&111', username='username'):
        return '''
        mutation {
            register(
                # email: "test@email.com",
                username: "%s",
                password1: "%s",
                password2: "%s"
            )
            { success }
        }
        ''' % (
            username,
            password,
            password,
        )

    def verify_query(self, token):
        return '''
        mutation {
            verifyAccount(token: "%s")
                { success, errors }
            }
        ''' % (token)


class RegisterRelayTestCase(RegisterTestCase):
    RESPONSE_RESULT_KEY = 'relayRegister'

    def register_query(self, password='aaa&&111', username='username'):
        return '''
        mutation {
            relayRegister(input: {email: "test@email.com", username: "%s", password1: "%s", password2: "%s"}) {
                success,
                errors,
                token,
                refreshToken
            }
        }
        ''' % (
            username,
            password,
            password,
        )

    def register_query_b(self, password='aaa&&111', username='username'):
        return '''
        mutation {
            relayRegister(input: {email: "test@email.com", username: "%s", password1: "%s", password2: "%s"}) {
                success,
                errors
            }
        }
        ''' % (
            username,
            password,
            password,
        )

    def verify_query(self, token):
        return '''
        mutation {
            relayVerifyAccount(input: {token: "%s"})
                { success, errors  }
        }
        ''' % (token)
