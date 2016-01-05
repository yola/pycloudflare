# Changelog

## 0.2.0

* Add SRV record support to allow for the creation of SRV DNS records.
* Rename `service` attributes of models to `_service`.
* Use `record_type` instead of `type` in `create_record` signature.
* Make `content` parameter to `create_record` optional.
* Use `kwargs` for `priority` parameter in `create_record`.

## 0.1.2

* Raise `ZoneNotFound` instead of `IndexError` when zone isn't found.

## 0.1.1

* Rename `create_partner_zone` to `create_host_zone`
* Cleanup garbage records created for `full_zone_set`

## 0.1.0

* Add ability to create partner zone (both to service and model)
* Remove `api_key` attribute from User model

## 0.0.2

* Initial public release, MIT/Expat licensed.
* Expand service coverage.
* Add models.
* Add Python 3 support.

## 0.0.1

* Initial internal release.
