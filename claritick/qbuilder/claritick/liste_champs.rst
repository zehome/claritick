Liste des champs
================

Voici pour chaque table la liste des champs et les filtres qu'il est possible de leur appliquer ::

    Service
        code_hprim
        groupe
        type

        filtres:
            'type' : ('=', 'IN', '!='),
            'code_hprim' : ('=', 'IN', '!='),
            'groupe' : ('=', 'IN', '!='),

    Prescripteur
        code_hprim
        groupe
        type

        filtres:
            'type' : ('=', 'IN', '!='),
            'code_hprim' : ('=', 'IN', '!='),
            'groupe' : ('=', 'IN', '!='),

    Testbio
        code
        bilan

        filtres:
            'code'  : ('=','IN','!='),
            'bilan' : ('=', 'IN','!='),

    Patient
        date_nai = Field(DateTime)
        sex = Field(String)
        taille = Field(Float)
        poids = Field(Float)

        filtres:
            'date_nai' : ALL_DATE_FILTERS,
            'sex' : ('=','IN','!='),

    Demande
        date_demande = Field(DateTime)
        urgence = Field(String, colname = 'urgence')
        demandeur = Field(String)

        filtres:
            'date_demande' : ALL_DATE_FILTERS,
            'priorite' : ('=','IN','!='),
            'demandeur' : ('=','IN','!='),

    DemAuto
        paillasse = Field(String, colname = 'automate')

        filtres:
            'paillasse' : ('=', 'IN', '!=', 'like'),

    DemAutoTest
        etat = Field(Integer, colname = 'status')

        filtres:
            "etat" : ('=','IN','!='),

    Resultat
        type_resu = Field(Integer)
        date_resu = Field(DateTime)
        resu = Field(Integer)
        seq = Field(Integer)
        stat_resu = Field(String)
        indic_norm = Field(String)

        filtres:
            'date_resu' : ALL_DATE_FILTERS,
            'type_resu' : ('=','IN','!='),
            'resu'      : ('=', '>', '<', '>=', '<='),
            'seq'       : ('=', 'IN', '!=', '<', '>', '<=', '>='),
            'stat_resu' : ('=','IN','!='),
            'indic_norm' : ('=','IN','!='),

    ResultatAnalyseur
        type_resu = Field(Integer)
        date = Field(DateTime)
        resu = Field(Integer)
        analyseur = Field(String)
        seq = Field(Integer)

        filtres:
            'date' : ALL_DATE_FILTERS,
            'type_resu' : ('=','IN','!='),
            'resu'      : ('=', '>', '<', '>=', '<='),
            'analyseur' : ('=', 'IN', '!=', 'like'),
            'seq'       : ('=', 'IN', '!=', '<', '>', '<=', '>='),

    User
        username    = Field(String)
        first_name  = Field(String)
        last_name   = Field(String)
        is_staff    = Field(Boolean)
        is_superuser= Field(Boolean)

        filtres:
            'username' : ('=', 'IN', '!='),
            'is_staff' : ('=', 'IN', '!='),
            'is_superuser' : ('=', 'IN', '!='),

    Tube
        code_barre  = Field(String)

        filtres:
            'code_barre' : ('=', 'IN', '!='),

    ModeleEvenement
        evenement   = Field(String)

        filtres:
            'evenement' : ('=', 'IN', '!='),

    EvenementTube
        date        = Field(DateTime)
        type        = Field(Integer)

        filtres:
            'date' : ALL_DATE_FILTERS,
            'type' : ('=', 'IN', '!='),
            'tube' : ('=', 'IN', '!='),

    TempsRendu
        start
        date
        end
        start_evt
        end_evt
        avg_temps_rendu
        min_temps_rendu
        max_temps_rendu

        filtres:
            'start' : ('=', 'IN', '!='),
            'end'   : ('=', 'IN', '!='),
            'start_evt' : ('=', 'IN', '!='),
            'end_evt'   : ('=', 'IN', '!='),
            'avg_temps_rendu' : ('>', '>=', '<', '<='),
            'min_temps_rendu' : ('>', '>=', '<', '<='),
            'max_temps_rendu' : ('>', '>=', '<', '<='),
            'date'   : ALL_DATE_FILTERS,

ALL_DATE_FILTERS
----------------

    * date_gt
    * date_lt
    * date_gt_now_less
    * date_lt_now_less
    * date_hour_gt
    * date_hour_lt
    * date_hour_eq
    * date_hour_ne
    * date_month_gt
    * date_month_lt
    * date_month_eq
    * date_month_ne
