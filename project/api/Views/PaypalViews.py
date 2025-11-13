from datetime import datetime

from dateutil.relativedelta import relativedelta

from .imports import *


class CreatePaypalOrder(APIView):
    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')

        if not plan_id:
            return Response({"error": "plan_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        chosen_plan = SubscriptionPlan.objects.filter(id=plan_id).first()

        if not chosen_plan:
            return Response({"error": "Invalid plan_id, no plan found"}, status=status.HTTP_400_BAD_REQUEST)

        price = chosen_plan.price * chosen_plan.duration
        access_token = get_paypal_access_token()
        url = f"{settings.PAYPAL_API_BASE}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": str(price)
                    }
                }
            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            company = self.request.user.company
            PaymentHistory.objects.create(company=company, payment_plan=chosen_plan, amount=price, orderID=response.json()['id'])
            return Response(response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response({"error": response.text}, status=response.status_code)




class CapturePaypalOrder(APIView):
    def post(self, request, *args, **kwargs):
        try:
            order_id = request.data.get('orderID')
            if not order_id:
                return Response({"error": "orderID is required."}, status=status.HTTP_400_BAD_REQUEST)
            access_token = get_paypal_access_token()
            if not access_token:
                return Response({"error": "Failed to retrieve PayPal access token."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            url = f"{settings.PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            response = requests.post(url, headers=headers)

            if response.status_code == 201:
                company = self.request.user.company
                payment = PaymentHistory.objects.filter(company=company,orderID=request.data['orderID']).update( **request.data,status="success")
                if company.plan and company.plan.duration:
                    today = datetime.now()
                    new_expiry_date = today + relativedelta(months=company.plan.duration)
                    company.expiry = new_expiry_date
                    company.save()

                return Response(
                    {
                        "message": "Payment captured successfully and subscription updated.",
                        "payment_details": {
                            "orderID": payment.orderID,
                            "payerID": payment.payerID,
                            "paymentID": payment.paymentID,
                        },
                        "expiry_date": company.expiry,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Failed to capture PayPal order.", "details": response.text},
                    status=response.status_code,
                )

        except Exception as e:
            return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
