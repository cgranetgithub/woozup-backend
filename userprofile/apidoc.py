UserResourceLogout = u"""[Custom API] - Requires authentication<br><br>
Logout the user. <br><br>"""
UserResourceCheckAuth = u"""[Custom API] - Requires authentication<br><br>
Check the user authentication status.<br><br>
Return a dict with { 'api_key' : API key, 'userid' : User ID }."""
UserResourcePushNotifReg = u"""[Custom API] - Requires authentication <br><br>
Update the registration_id / token of the device.<br>This ID is
used to send push notification to the device, via the GCM/APN service."""
UserResourcePushNotifRegFields = { "name": {
        "type": "string",
        "required": True,
        "description": "Device name" },
    "device_id": {
        "type": "string",
        "required": True,
        "description": "Device unique ID" },
    "registration_id": {
        "type": "string",
        "required": True,
        "description": "Registration ID" },
    }
AuthResourceRegister = u"""[Custom API] - Does not require authentication
<br><br>Create a new User in the backend, as well as its UserProfile and
UserPosition (location profile).<br>Then authenticate and login the user.
<br><br>Return a dict with { 'api_key' : API key, 'userid' : User ID }."""
AuthResourceRegisterFields = { "username": {
                                "type": "string",
                                "required": True,
                                "description": u"username passed as a data" },
                         "password": {
                                "type": "string",
                                "required": True,
                                "description": u"password passed as a data" },
                       }
AuthResourceLogin = u"""[Custom API] - Does not require authentication
<br><br>Authenticate and login the user.<br><br>
Return a dict with { 'api_key' : API key, 'userid' : User ID }."""
AuthResourceLoginFields = { "username": {
                                "type": "string",
                                "required": True,
                                "description": u"username passed as a data" },
                            "password": {
                                "type": "string",
                                "required": True,
                                "description": u"password passed as a data" },
                          }
