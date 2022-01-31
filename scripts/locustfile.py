from locust import HttpUser, task, constant
import json

# from locust import LoadTestShape
# Taskset,


class K(HttpUser):
    wait_time = constant(1)

    host = "https://fs-dev-webstore-api.alphasolution.com.mo"

    # tasks = [callCheckQtyAndPlaceOrder]

    @task()
    def work_flow(self):
        self.get_product_available()
        self.place_order()

    def get_product_available(self):
        self.client.post(
            "/quantity-service/get-redis-qty",
            json={
                "merchant_id": "as-one",
                "product_ids": ["614d8ed9ff6b830006860d04", "5fab9e0d33a439000ae19acd", "61dd25ad41dea4000af7c1fd"],
            },
        )

    def place_order(self):
        self.client.post(
            "/checkout-service/quota-checkout",
            data=json.dumps(
                {
                    "checkout_request": {
                        "merchant_id": "as-one",
                        "items": [
                            {
                                "product_id": "61dd25ad41dea4000af7c1fd",
                                "qty": 3,
                                "sku": "5151432",
                                "options": [],
                                "additionalMessage": None,
                                "flash_sale": True,
                            }
                        ],
                        "contact_info": {"name": "world-first", "mobile_no": "85366666666", "email": ""},
                        "payment_method": "cybersource",
                        "remarks": None,
                        "additional_parameters": [
                            {
                                "flow": "shipping_date",
                                "parameters": [
                                    {"key": "pickup_date", "value": "2022-02-03"},
                                    {"key": "pickup_time", "value": "08:30-16:30"},
                                ],
                            }
                        ],
                        "order_lang": "default",
                        "boc_promo": False,
                        "shipping_method": {"pick_up": {"store": "澳門信達店", "address": "澳門天神行信達城商場地下AM舖"}},
                    },
                    "token": "FFFF0N0000000000A04C:nc_activity_h5:1643098018809:0.560921693643984",
                    "session_id": "01fjylpqJj9JJlmgKL5AXxBtuAqCudAjplYmtmO5dU2vMjg_dqHcbGBIZL8lnBn4OOVmdb1W6mPeGh-jiKuQRG71XNzYZFz6cmFHkClTuWuYU8kzD3ifx_cIVDty9213Cfsx1lsrYkpZL0lXdVkT7_uMi0-umHlYH5jxhgzQ8aud5sLoMVYQvW5lQug540prbzg986Sjs9dC8LdJlO_CaEoLlgSHMhjoy_75wV1Xu5YzA",
                    "sig": "05XqrtZ0EaFgmmqIQes-s-CMAhlxSnuKRn3bxz6FfiPMDk4jtD6NbM-MgD70p6HAFNtgYrtZPSMYL0nfbTE-pd_8zs7lmMzw5Tj9tYeVRyq5d-manwN0gf4R7SnVjzd2AZB_29QdojrZFw4CO-Z0kwbb7NqiKinyePbA_IdTnO3958vIKBNLlMGls8TTNxL55_IjcueQOpqPqLz6N4YEYA0wT0ZGVePWvbxh24nEZ-n50ebzKSMdL15fsX6ez5vd615-0Wyvqf92sIlApWy57mAryUQ5B2-073l_I-KHaIT4J_DV1A6MCncZv1l3f72sMDXKQ101cEBVDGKhPAlFIyFSBZ7nVMvml3gQ5aUTWGhcIzN5aesIjOjgnfHU3OIRC3iZ3qcaXcNxYDJh4I0qjodKUlQzxrAHc_dNPQ0GrKUtSF8bbpE7eubh4FMK3W1pxUetyB00uTXs39v9QP6RuXowMPEUDablSXHXOR6kAGIpdj-6y4Djv6Bm1tjgkOf2Sk3T5Lp2isFXfaeSVUBs_skA",
                }
            ),
        )
