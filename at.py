
from utils.africastalking.premium_sms import PremiumSMS
from utils.africastalking.subscription import Subscription
from utils.broadcast import Broadcast
from utils.postgres_crud import PostgresCRUD

class AT():
    def __init__(self):
        self.short_code = '22384'
        self.keyword = 'TIP'
        
        self.subscription = Subscription()
        self.postgres_crud = PostgresCRUD()
        self.premium_sms = PremiumSMS()
        self.broadcast = Broadcast()
    
    def send_sub_push(self, phone_number):
        #self.subscription.create_subscription_sync(self.short_code, self.keyword, phone_number)
        self.premium_sms.subscribe(self.short_code, self.keyword, phone_number) 
        
    def fetch_and_save_subs(self):    
        phone_numbers = self.subscription.fetch_subscriptions_sync(self.short_code, self.keyword)
        for phone_number in phone_numbers:
            self.postgres_crud.add_or_remove_subscriber(phone_number, status=1)
    
    def send_premium_sms_to_subscribed(self):  
        message = self.broadcast.upcoming_sms()
        active_subscribers = self.postgres_crud.fetch_subscribers(0)
        recipients = ''
        for subscriber in active_subscribers:
            recipients = recipients + f'+{subscriber[0]},'
        
        if len(recipients) > 0:  
            print(message)
            print(recipients)
            data = self.premium_sms.send(self.short_code, self.keyword, recipients[:-1], message)
            if data is not None:
                for datum in data["SMSMessageData"]["Recipients"]:
                    message_id = datum["messageId"]
                    number = datum["number"]
                    status_code = datum["statusCode"]
                    
                    self.postgres_crud.update_subscriber_on_send(number, message_id, status_code)
                                                
             
if __name__ == '__main__':
    AT().send_sub_push("+254105565532")
    #AT().fetch_and_save_subs()
    #AT().send_premium_sms_to_subscribed()
        