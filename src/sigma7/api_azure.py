from abc import ABC, abstractmethod
import azure.functions as func
import logging
import json

class API7(ABC):
    """This is an abstract class meant to streamline transactions between Azure Blob Storage.
    It is divided up into 3 (logical) parts:
    * Creates BLOB Client instance.
    * Allows for the upload and download of blob data.

    :param ABC: Abstract class inheritance. 
    :type ABC: abc.ABC

    """

    def __init__(self, params, **args):
        self.params = params
        self.misc = args
        super().__init__()
    
    def gather_params(self, req: func.HttpRequest) -> dict:
        """
        Gathers the API input parameters.
        Searches for all parameters in an API and returns the name and value of the parameters in a dict.

        :classmethod:

        :param req: HTTP request object - per the Azure functions library/sdk
        :type req: azure.functions.HttpRequest

        :return: A dictionary containing the api parameters and their inputs from the user.
        :rtype: dict

        """

        out = {}
        for param in self.params:
            inpt = req.params.get(param)
            if not inpt:
                try:
                    req_body = req.get_json()
                except ValueError:
                    pass
                else:
                    inpt = req_body.get('param')
            out.update({param: inpt})
            logging.info("{} : {}".format(param, inpt))
        return(out)

    def conditional_params(self, cond: str, func: type(abs), params: dict) -> func.HttpResponse:
        """
        Conditional function to specify how to treat any combination of API parameters.
        Per the Azure tutorial/example, this should simplify how to handle parameters when provided.

        :classmethod:

        :param cond: A string of PYTHON CODE. This string will be evaluated as a conditional statement.
        :type cond: str
        :param func: An actual python function. This function will be executed when cond is true with the parameters provided in params.
        :type func: class: 'function'
        :param params: A dictionary containing the named parameters to be fed into func. \n
        The keys should be the name of the parameters corresponding to the parameters in your provided function in func. 
        :type params: dict

        :return: A dictionary of the input parameters. key = name of param // value = actual input
        :rtype: dict
        """

        if params not in self.params:
            raise Exception("Parameter not found in AzHelper obj.")
        if eval(cond):
            out = func(**params)
            if(type(out) != dict):
                raise Exception("Output from input function must be a dict.")
            return func.HttpResponse(json.dumps(out), status_code = 200)
        return func.HttpResponse("Something went wrong..", status_code=400)

    @abstractmethod
    def retrieve_data(self):
        """Abstract method to be defined on how the object retrieves data.
        :abstractmethod:
        """
        pass

    @abstractmethod
    def format_data(self):
        """Abstract method to be defined on how the object formats data.
        :abstractmethod:
        """
        pass


