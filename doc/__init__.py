descr = """(can be passed in the header or as a url parameter)"""

fields = {  "type": "string",
            "required": True,
            "description": descr }

authdoc = { "username": fields,
            "api_key" : fields }
