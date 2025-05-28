import simpy
import random

# 3D 프린터 클래스
class Printer:
    def __init__(self, env, printer_id, metrics):
        self.env = env
        self.printer_id = printer_id
        self.resource = simpy.Resource(env, capacity=1)  # 각 프린터는 단일 리소스
        self.metrics = metrics

    def process_product(self, order_id, product_id, filament, paint):
        with self.resource.request() as req:
            yield req
            print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} 제조 시작 (프린터 {self.printer_id})")
            self.metrics.record_product(self.printer_id)  # 제품 처리 기록

            # 제조 공정: 필라멘트 5개, 8분 소요
            filament_needed = 5
            if filament.level < filament_needed:
                print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} - 필라멘트 부족, 대기 (프린터 {self.printer_id})")
            yield filament.get(filament_needed)
            yield self.env.timeout(8)
            print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} 제조 완료 (프린터 {self.printer_id}, 필라멘트 {filament_needed}개 사용)")

            # 후공정: 서포트 제거 (3분)
            yield self.env.timeout(3)
            print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} 서포트 제거 완료 (프린터 {self.printer_id})")

            # 후공정: 세척 (2분)
            yield self.env.timeout(2)
            print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} 세척 완료 (프린터 {self.printer_id})")

            # 후공정: 페인트 0.5리터, 5분 소요
            paint_needed = 0.5
            if paint.level < paint_needed:
                print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} - 페인트 부족, 대기 (프린터 {self.printer_id})")
            yield paint.get(paint_needed)
            yield self.env.timeout(5)
            print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} 페인팅 완료 (프린터 {self.printer_id}, 페인트 {paint_needed}리터 사용)")

            # 검사: 2분 소요, 0.01 확률로 불량
            yield self.env.timeout(2)
            if random.random() < 0.01:  # 1% 확률로 불량
                print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} 검사 불량 (프린터 {self.printer_id}), 재생산 시작")
                self.metrics.record_defect()  # 불량 기록
                yield self.env.process(self.process_product(order_id, product_id, filament, paint))  # 재생산
            else:
                print(f"{self.env.now:.2f}분: 주문 {order_id} 제품 {product_id} 검사 완료 (프린터 {self.printer_id})")
