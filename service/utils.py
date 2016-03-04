import phonenumbers

def is_mobile(number):
    ### hack for French mobile only
    if ( number.startswith('+336') or number.startswith('+337') ):
        return True
    return False
    ###


def get_clean_number(i):
    ### hardcoded, need to fix it
    country_code = 'FR'
    ###
    # normalize phonenumber and skip if fail
    ph = None
    try:
        ph = phonenumbers.parse(i, None)
    except phonenumbers.NumberParseException:
        try:
            ph = phonenumbers.parse(i, country_code)
        except:
            return None
    # check if validate num
    if (    phonenumbers.is_possible_number(ph)
        and phonenumbers.is_valid_number(ph)    ):
            number = phonenumbers.format_number(ph,
                                        phonenumbers.PhoneNumberFormat.E164)
            if is_mobile(number):
                return number
    return None

def is_personal_email(email):
    if '@' in email:
        for i in ['gmail', 'hotmail', 'orange', 'numericable', 'bbox', 'live',
                  'free', 'yahoo', 'outlook', 'aol']:
            if i in email:
                return True
    return False
