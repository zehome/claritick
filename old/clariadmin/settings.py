# -*- coding: utf-8 -*-

SECURITY = {
    # The default security level to give to users
    # which do not have defined level.
    #
    # Remember higher level is lower security level.
    # 0: Highest security level
    # 99: Lowest security level
    "DEFAULT_USER_LEVEL": 99,
    "DEFAULT_LEVEL": 10,
    # Permits to chose which field in the clariadmin/models.py Host
    # needs which security level at the minimum.
    "HostForm": {
        # Security level 10 needed for any field
        "__default__": 10,
        # Root password needs level 2 or lower
        "rootpw": 2,
    },
    "SearchHostForm": {
        # Security level 10 needed for any field
        "__default__": 10,
        # Root password needs level 2 or lower
        "rootpw": 2,
    },

}
