# Changelog

## v1.1

### 1.1.0

- Added CommonTestCase class for testing both GraphQL and Relay queries.
- Cleanup testing code

## v1.0

### 1.0.3

- Fixed bug: when trying to refresh token (`mutation` `refreshToken`)  with invalid refresh_token,
  the response should contain null values for `refreshExpiresIn` output fields,
  but the exception was thrown.

  Changed property `required` to False for the fields `refreshExpiresIn` for
  classes `RefreshToken` and `RelayRefreshToken`

### 1.0.2

- Fixed bug: when trying to login (`mutation` `tokenAuth`) with wrong credentials, the response should contain
  null values for `payload` and `refreshExpiresIn` output fields, but the exception was thrown.

  Changed property `required` to False for the fields `payload` and `refreshExpiresIn`

### v1.0.1

- Cleanup code

### v1.0.0

- first commit
