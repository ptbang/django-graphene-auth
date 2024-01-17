import base64
import json

from django.contrib.auth import get_user_model

from .base_test_case import BaseTestCase

UserModel = get_user_model()


class QueryTestCase(BaseTestCase):
    def setUp(self):
        self.user1 = self.register_user(email="foo@email.com", username="foo", verified=False)
        self.user2 = self.register_user(email="bar@email.com", username="bar", verified=True)
        self.user3 = self.register_user(email="gaa@email.com", username="gaa", verified=True, archived=True)

    def test_user(self):
        id = base64.b64encode(('UserNode:' + str(self.user1.pk)).encode()).decode()
        query = """
        query {
            user(id: "%s") {
                id, pk
            }
        }
        """ % (base64.b64encode(('UserNode:' + str(self.user1.pk)).encode()).decode(),)
        response = self.query(query)
        result = json.loads(response.content)['data']['user']
        self.assertIsNone(result)

        self.client.force_login(self.user2)
        response = self.query(query)
        result = json.loads(response.content)['data']['user']
        self.assertIsNone(result)

        self.user2.is_staff = True  # type: ignore
        self.user2.save()
        response = self.query(query)
        result = json.loads(response.content)['data']['user']
        self.assertEqual(result['pk'], self.user1.pk)

    def test_users(self):
        query = """
        query {
            users(first: 2) {
                totalCount
                edges {
                    node {
                        archived,
                        verified,
                        secondaryEmail,
                        pk,
                        id
                    }
                }
                pageInfo { startCursor, endCursor, hasPreviousPage, hasNextPage }
            }
        }
        """
        response = self.query(query)
        result = json.loads(response.content.decode())['data']['users']
        self.assertEqual(result['edges'], [])

        self.client.force_login(self.user2)
        response = self.query(query)
        result = json.loads(response.content)['data']['users']
        self.assertEqual(result['edges'], [])

        self.user2.is_staff = True  # type: ignore
        self.user2.save()
        response = self.query(query)
        result = json.loads(response.content)['data']['users']
        self.assertEqual(len(result['edges']), 2)
        self.assertEqual(result['totalCount'], UserModel.objects.all().count())

        query = """
        query {
            users (email: "%s") {
                edges {
                    node {
                        email,
                        archived,
                        verified,
                        secondaryEmail,
                        pk,
                        id
                    }
                }
            }
        }
        """ % (self.user3.email)  # type: ignore
        response = self.query(query)
        result = json.loads(response.content)['data']['users']
        self.assertEqual(result["edges"][0]['node']['email'], self.user3.email)  # type: ignore

    def test_db_queries(self):
        """
        Querying users should only use 2 db queries.

        1. SELECT COUNT(*) AS "__count" FROM "auth_user"
        2. SELECT ... FROM "auth_user"
            LEFT OUTER JOIN "graphql_auth_userstatus" ON (
                "auth_user"."id" = "graphql_auth_userstatus"."user_id"
            )
            LIMIT 3
        """
        self.user2.is_staff = True  # type: ignore
        self.user2.save()
        login_query = """
            mutation {tokenAuth(email: "%s", password: "%s") { token }}
            """ % (self.user2.email, self.default_password)  # type: ignore
        response = self.query(login_query)
        token = json.loads(response.content.decode())['data']['tokenAuth']['token']

        query = """
        query {
            users {
                edges {
                    node {
                        archived,
                        verified,
                        secondaryEmail,
                        pk
                    }
                }
            }
        }
        """
        with self.assertNumQueries(3):
            response = self.query(query, headers=self.get_authorization_header(token))
        result = json.loads(response.content.decode())['data']['users']
        self.assertEqual(len(result["edges"]), UserModel.objects.all().count())

    def test_me_authenticated(self):
        query = """
        query {
            me {
                username
            }
        }
        """
        self.client.force_login(self.user2)
        response = self.query(query)
        self.assertResponseNoErrors(response)
        result = json.loads(response.content.decode())['data']['me']
        self.assertEqual(result['username'], self.user2.username)  # type: ignore

    def test_me_anonymous(self):
        query = """
        query {
            me {
                username
            }
        }
        """
        response = self.query(query)
        result = json.loads(response.content.decode())['data']['me']
        self.assertIsNone(result)
