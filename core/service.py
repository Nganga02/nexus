from django_daraja.mpesa.core import MpesaClient



class MpesaService:
    def __init__(self, phone_number: str, amount: int):
        self.phone_number = phone_number
        self.amount = amount
        self.client = MpesaClient()

    def initiate_stk_push(self):
        account_reference = 'nexus'
        transaction_desc='booking payment'
        callback_url=''#TODO: add callback url
        response = self.cl.stk_push(
            self, 
            self.phone_number,
            self.amount,
            account_reference,
            transaction_desc,
            callback_url
            )
        return response 
        
    async def callback_handler(self):
        response = await self.initiate_stk_push()
        data = self.cl.parse_stk_result(response)
        return data
