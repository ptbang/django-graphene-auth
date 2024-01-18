# Changelog

## v1.0

### 1.0.1

- Fixed bug: when trying to login with wrong credentials, the response should contain
  null values for `payload` and `refreshExpiresIn` output fields, but the exception was thrown.

  Changed property `required` to False for the fields `payload` and `refreshExpiresIn`

### v1.0.1

- Cleanup code

### v1.0.0

- first commit
