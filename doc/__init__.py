descr = """(can be passed in the header or as a parameter in the url 
request)"""

fields = {  "type": "string",
            "required": True,
            "description": descr }

authdoc = { "username": fields,
            "api_key" : fields }
