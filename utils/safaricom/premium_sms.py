
from .utils import Utils


class PremiumSMS:
    def __init__(self, sdp):
        """
        Subscription constructor.
        
        :param sdp: Instance of the SDP class
        """
        self.SDP = sdp

    def send_sms(self, request_id, offer_code, phone_number, message, link_id=None):
        """
        Send a premium message to a user.
        
        :param request_id: Unique transaction ID for tracking
        :param offer_code: The offer code associated with the SMS
        :param phone_number: The recipient's phone number
        :param message: The content of the SMS
        :param link_id: Optional link ID
        :return: dict
        """
        data = [
            {"name": "Msisdn", "value": phone_number},
            {"name": "Content", "value": message},
            {"name": "OfferCode", "value": offer_code},
            {"name": "CpId", "value": self.SDP.cp_id}
        ]

        if link_id is not None:
            data.append({"name": "LinkId", "value": link_id})

        body = {
            "requestId": request_id,
             "requestTimeStamp": self.SDP.generate_timestamp(),
            "channel": "APIGW",
            "operation": "SendSMS",
            "requestParam": {"data": data}
        }

        response = self.SDP.request.request("post", "public/SDP/sendSMSRequest", self.SDP.token, body)
        
        return Utils.get_response(response, self.SDP.debug_level)
