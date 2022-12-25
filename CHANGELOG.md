# Changelog

## 4.0.0
* Rename `CloudFlareService.remove_account_member()` to 
  `CloudFlareService.delete_account_member()`.

## 3.1.0
* Add `CloudFlareService.add_account_member()`.
* Add `CloudFlareService.list_account_members()`.
* Add `CloudFlareService.remove_account_member()`.

## 3.0.0
* Add `CloudFlareService.create_account()`.
* Add `CloudFlareService.get_account_by_name()`.
* Fix `CloudFlareService.create_zone()` to match CloudFlare API.
* Add `User.create_account_and_zone()`.
* Add `User.get_or_create_account()`.
* Fix `User.create_zone()` to match CloudFlare API 
  and `CloudFlareService.create_zone()`.

## 2.3.0
* Add `CloudFlareService.update_custom_hostname()`.

## 2.2.0
* Add `CloudFlareService.delete_custom_hostname()`.

## 2.1.0
* Add `CloudFlareService.create_custom_hostname()`.
* Add `CloudFlareService.get_custom_hostname_by_name()`.

## 2.0.0
* Remove pagination from `CloudFlareService.get_zone_settings()` since
  the corresponding API isn't paginated.

## 1.0.0
* Add optional `hosts` parameter to `CloudFlareService.purge_cache()` method.
* Add optional `hosts` parameter to `models.Zone.purge_cache()` method.

## 0.4.5
* Insert a delay in the Universal SSL toggling, so it takes effect.

## 0.4.4
* Allow toggling Universal SSL on a CNAME zone, to re-verify it.

## 0.4.3
* Fix bug in HTTP errors translation.

## 0.4.2
* Raise `exceptions.SSLUnavailable` if SSL info is not available for zone.

## 0.4.1
* Add modelling and service methods for PageRules.

## 0.4.0
* Remove `pycloudflare.pagination`, in favour of Demands' pagination.
* Switch to 1-based indexing. Previously, page 0 and 1 would have
  returned the same content, leading to some duplication in results.

## 0.3.4
* Add `models.Zone.get_ssl_verification_info` method.
* Add `services.CloudFlareService.get_ssl_verification_info` method.

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
