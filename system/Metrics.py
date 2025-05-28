import pandas as pd

# 메트릭 클래스
class Metrics:
    def __init__(self, env, num_printers):
        self.env = env
        self.printer_product_counts = {i: 0 for i in range(num_printers)}  # 프린터별 제품 수
        self.order_completion = {}  # 주문별 완료 정보
        self.defect_count = 0  # 총 불량 수

    def record_product(self, printer_id):
        self.printer_product_counts[printer_id] += 1

    def record_order(self, order_id, num_products):
        self.order_completion[order_id] = num_products

    def record_defect(self):
        self.defect_count += 1

    def save_to_csv(self):
        # 프린터별 제품 수
        printer_data = pd.DataFrame(
            list(self.printer_product_counts.items()),
            columns=["Printer_ID", "Products_Processed"]
        )
        # 주문별 정보
        order_data = pd.DataFrame(
            list(self.order_completion.items()),
            columns=["Order_ID", "Products_Completed"]
        )
        # 불량 수
        defect_data = pd.DataFrame({"Total_Defects": [self.defect_count]})
        # CSV 저장
        with open("simulation_metrics.csv", "w") as f:
            f.write("Printer Metrics\n")
            printer_data.to_csv(f, index=False)
            f.write("\nOrder Metrics\n")
            order_data.to_csv(f, index=False)
            f.write("\nDefect Metrics\n")
            defect_data.to_csv(f, index=False)
        print(f"{self.env.now:.2f}분: 메트릭을 simulation_metrics.csv에 저장했습니다.")