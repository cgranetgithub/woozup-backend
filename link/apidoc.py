LinkResource = u""" 
When a user registers, its contact list is sent to the backend 
(API contact/sort/).<br>A Link is created between the user and each contact 
already registered as a user.<br>In parallel, the backend will look for all 
Invites where the receiver is the new user and transform it into a link.<br>
<ul>
<li>sender_status = NEW</li>
<li>receiver_status = NEW</li>
</ul> <br> <br>
If the sender clicks on "connect" button in the app (API link/id/connect/)
<ul>
<li>sender_status => ACCEPTED</li>
<li>receiver_status => PENDING</li>
</ul> <br> <br>
If the receiver accepts the request for connection (API link/id/accept/)
<ul>
<li>sender_status = ACCEPTED</li>
<li>receiver_status => ACCEPTED</li>
</ul> <br> <br>
If the receiver rejects the request for connection (API link/id/reject/)
<ul>
<li>sender_status = ACCEPTED</li>
<li>receiver_status => REJECTED</li>
</ul> <br> <br>
If the sender or the receiver blacklist someone (API link/id/?/)
<ul>
<li>x_status => BLOCKED</li>
</ul>
"""
LinkResourceConnect = u"""[Custom API] - Requires authentication<br><br>
Sender requests the receiver to connect.<br>This will change the Link status 
from NEW/NEW to ACC/PEN."""
LinkResourceAccept = u"""[Custom API] - Requires authentication<br><br>
Receiver accepts to connect.<br>
This will change the Link status from ACC/PEN to ACC/ACC."""
LinkResourceReject = u"""[Custom API] - Requires authentication<br><br>
Receiver refuse to connect.<br>
This will change the Link status from ACC/PEN to ACC/REJ."""
ContactResourceSort = u"""[Custom API] - Requires authentication<br><br>
Takes a list of usernames and triggers a background job that will create the 
appropriate INVITE and LINK between the user and each person in the list"""
ContactResourceSortFields = { u"username list": {
                                u"type": "json list",
                                u"required": True,
                                u"description": u"""The list of username that 
will be passed to the BG job.""" } }
ContactResourceError = u"""data must have the following form: 
{ 'number' : { 'email' : ..., 'name' : ... },
  'number' : { ... }
}
the API will also recognize 'photo' field if given """
