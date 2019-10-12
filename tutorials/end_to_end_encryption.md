# End-to-End Encryption

End-to-end encryption is enabled by default with the bot

* Set a store path
* Enable encryption in AsyncClient
* Use sync_forever after a single full sync to fix bug with getting old messages
	* Save the sync token only on shutdown instead of constantly
* ignore_unverified_devices on sending

* Possibly simply as easy as enabling an option for where to set up the store
* Will need to explain verifying other devices. How would a bot auto-verify?
