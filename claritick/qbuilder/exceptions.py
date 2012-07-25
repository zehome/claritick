class QBException(Exception):
    pass

class QBMsgException(QBException):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class QBNoModelsLoaded(QBException):
    pass

class QBIncorrectModel(QBMsgException):
    def __init__(self, model_name):
        self.message = "Model %s does not exist or is used as main model but is not in selectables." % (model_name,)

class QBIncorrectQuery(QBMsgException):
    pass

class QBStop(QBException):
    pass

class QBEmptyDatabase(QBMsgException):
    pass

class QBPercentile(QBMsgException):
    pass

class QBArgs(QBMsgException):
    pass
