# Changelog

## 0.3.3

* Add `models.Zone.purge_cache` method (and corresponding service support).

## 0.3.2

* Add `models.User.create_cname_zone` method.

## 0.3.1

* Add `services.CloudFlareHostService.zone_set` method.

## 0.3.0

* Switch to Demands >= 4.0.0

## 0.2.3

* Include `README.rst` file in package, since `setup.py` depends on it

## 0.2.2

* Assign `_data` to the returned result as the `Record` meta values change on
`save`.

## 0.2.1

* Move attributes required for SRV records into the correct field.

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
