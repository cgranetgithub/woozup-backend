import phonenumbers

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
            return phonenumbers.format_number(ph,
                                        phonenumbers.PhoneNumberFormat.E164)
    else:
        return None
